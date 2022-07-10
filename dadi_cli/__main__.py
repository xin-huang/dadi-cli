import argparse, glob, os.path, sys, signal
import numpy as np
import random
import dadi
import multiprocessing

from dadi_cli.GenerateFs import *
from dadi_cli.GenerateCache import *
from dadi_cli.InferDM import *
from dadi_cli.InferDFE import *
from dadi_cli.Pdfs import *
from dadi_cli.Models import *
from dadi_cli.utilities import *


def set_sigpipe_handler():
    if os.name == "posix":
        # Set signal handler for SIGPIPE to quietly kill the program.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def sys_exit(message):
    sys.exit(message)


# Worker functions for multiprocessing with demography/DFE inference
def _worker_func(func, in_queue, out_queue, args):
    while True:
        new_seed = in_queue.get()
        np.random.seed(new_seed)
        results = func(*args)
        out_queue.put(results)


def run_generate_fs(args):
    if args.mask_shared: mask='shared'
    elif args.mask: mask='singletons'
    else: mask=''
    generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size, seed=args.seed,
                pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized,
                marginalize_pops=args.marginalize_pops, subsample=args.subsample, masking=mask)

    
def run_generate_cache(args):
    func = get_model(args.model, args.model_file)
    generate_cache(func=func, grids=args.grids, popt=args.demo_popt,
                   gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                   output=args.output, sample_sizes=args.sample_sizes, mp=args.mp, cuda=args.cuda, dimensionality=args.dimensionality)


def run_simulate_dm(args):
    from dadi_cli.SimulateFs import simulate_demography
    simulate_demography(args.model, args.model_file, args.p0, args.ns, args.grids, args.misid, args.output, args.inference_file)


def run_simulate_dfe(args):
    from dadi_cli.SimulateFs import simulate_dfe

    import pickle
    if args.cache1d != None:
        cache1d = pickle.load(open(args.cache1d, 'rb'))
    else: cache1d = args.cache1d
    if args.cache2d != None:
        cache2d = pickle.load(open(args.cache2d, 'rb'))
    else: cache2d = args.cache2d

    simulate_dfe(args.p0, cache1d, cache2d, args.pdf1d, args.pdf2d, args.ratio, args.misid, args.output)


def run_simulate_demes(args):
    from dadi_cli.SimulateFs import simulate_demes
    simulate_demes(args.demes_file, atgs.ns, args.grids, args.output)


def run_infer_dm(args):
    fs = dadi.Spectrum.from_file(args.fs)
    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not (fs.folded or args.nomisid)

    if not args.model_file and args.constants != -1: args.constants = _check_params(args.constants, args.model, '--constant', args.misid)
    if not args.model_file and args.lbounds != -1: args.lbounds = _check_params(args.lbounds, args.model, '--lbounds', args.misid)
    if not args.model_file and args.ubounds != -1: args.ubounds = _check_params(args.ubounds, args.model, '--ubounds', args.misid)

    if args.p0 == -1: args.p0 = _calc_p0_from_bounds(args.lbounds, args.ubounds)

    # Extract model function, from custom model_file if necessary
    func = get_model(args.model, args.model_file)

    if args.maxeval == False: args.maxeval = max(len(args.p0)*50,1)

    existing_files = glob.glob(args.output_prefix+'.InferDM.opts.*')
    try:
        newest_file_num = max([int(ele.split('.')[-1]) for ele in existing_files]) + 1
    except:
        newest_file_num = 0
    fid = open(args.output_prefix+'.InferDM.opts.{0}'.format(newest_file_num), 'a')
    # Write command line to results file
    import sys
    fid.write('# {0}\n'.format(' '.join(sys.argv)))
    
    # Write column headers
    param_names = get_dadi_model_params(args.model, args.model_file)
    if not args.nomisid: param_names += ['misid']
    fid.write('# Log(likelihood)\t'+'\t'.join(param_names)+'\ttheta\n')

    # Check if demographic function uses inbreeding, need to be done before wrapping
    import inspect
    if 'from_phi_inbreeding' in  inspect.getsource(func):
        inbreeding = True
    else:
        inbreeding = False

    # Randomize or set seed for starting parameter values
    if args.seed == None: 
        import time, os
        ts = time.time()
        args.seed = int(time.time()) + int(os.getpid())
    import random
    np.random.seed(args.seed)

    if args.global_optimization:
        if inbreeding:
            print("Warning: can't down project inbreeding data for global optimization")
        else:
            existing_files = glob.glob(args.output_prefix+'.global.InferDM.opts.*')
            try:
                newest_file_num = max([int(ele.split('.')[-1]) for ele in existing_files]) + 1
            except:
                newest_file_num = 0
            fid_global = open(args.output_prefix+'.global.InferDM.opts.{0}'.format(newest_file_num), 'a')
            # Write command line to global results file
            fid_global.write('# {0}\n'.format(' '.join(sys.argv)))
            # Write column headers
            fid_global.write('# Log(likelihood)\t'+'\t'.join(param_names)+'\ttheta\n')
            global_optimizations = round(args.optimizations*.25)
            args.optimizations -= global_optimizations
            # Determin if the global optimization algorithm is
            # one that can be seeded or random (unseeded).
            import nlopt
            if args.seed == None:
                global_algorithm = nlopt.GN_MLSL
            else:
                global_algorithm = nlopt.GN_MLSL_LDS
            if args.work_queue:
                import work_queue as wq
                if args.debug_wq:
                    q = wq.WorkQueue(name = args.work_queue[0], debug_log = 'debug.log')
                else:
                    q = wq.WorkQueue(name = args.work_queue[0])
                # Returns 1 for success, 0 for failure
                if not q.specify_password_file(args.work_queue[1]):
                    raise ValueError('Work Queue password file "{0}" not found.'.format(args.work_queue[1]))

                for ii in range(global_optimizations): 
                    new_seed = np.random.randint(1,1e6)
                    t = wq.PythonTask(infer_global_opt, fs, func, args.p0, args.grids, 
                                      args.ubounds, args.lbounds, args.constants, args.misid, 
                                      args.cuda, args.maxeval, args.maxtime, global_algorithm, new_seed)
                    # If using a custom model, need to include the file from which it comes
                    if args.model_file:
                        t.specify_input_file(args.model_file+'.py')
                    q.submit(t)
            else:
                from multiprocessing import Process, Queue

                worker_args = (fs, func, args.p0, args.grids, args.ubounds, args.lbounds, args.constants, args.misid, 
                               args.cuda, args.maxeval, args.maxtime, global_algorithm)

                # Queues to manage input and output
                in_queue, out_queue = Queue(), Queue()
                # Create workers
                workers = [Process(target=_worker_func, args=(infer_global_opt, in_queue, out_queue, worker_args)) for ii in range(args.threads)]
                # Put the tasks to be done in the queue. 
                for ii in range(global_optimizations):
                    new_seed = np.random.randint(1,1e6)
                    in_queue.put(new_seed)
                # Start the workers
                for worker in workers:
                    worker.start()
            # Collect and process results
            from dadi_cli.BestFit import get_bestfit_params
            for _ in range(global_optimizations):
                if args.work_queue: 
                    result = q.wait().output
                else:
                    result = out_queue.get()
                # Write latest result to file
                # Check that the log-likelihood is not a weird value
                if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                    result = (-np.inf,) + result[1:]
                fid_global.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
                fid_global.flush()
                result = get_bestfit_params(path=args.output_prefix+'.global.InferDM.opts.*',
                                            lbounds=args.lbounds, ubounds=args.ubounds, output=args.output_prefix+'.global.InferDM.bestfits',
                                            delta=args.delta_ll)
                if result is not None:
                    args.force_convergence = False
                    break
            if not args.work_queue:
                # Stop the workers
                for worker in workers:
                    worker.terminate()
            from dadi_cli.utilities import get_opts_and_theta
            import os
            args.p0, _ = get_opts_and_theta(args.output_prefix+'.global.InferDM.bestfits', True)

    converged = False
    while not converged:
        if not args.force_convergence:
            converged = True
        if args.work_queue:
            import work_queue as wq
            if args.debug_wq:
                q = wq.WorkQueue(name = args.work_queue[0], debug_log = 'debug.log')
            else:
                q = wq.WorkQueue(name = args.work_queue[0])
            # Returns 1 for success, 0 for failure
            if not q.specify_password_file(args.work_queue[1]):
                raise ValueError('Work Queue password file "{0}" not found.'.format(args.work_queue[1]))

            for ii in range(args.optimizations):
                new_seed = np.random.randint(1,1e6)
                t = wq.PythonTask(infer_demography, fs, func, args.p0, args.grids, 
                                  args.ubounds, args.lbounds, args.constants, args.misid, 
                                  args.cuda, args.maxeval, args.maxtime, new_seed)
                # If using a custom model, need to include the file from which it comes
                if args.model_file:
                    t.specify_input_file(args.model_file+'.py')
                q.submit(t)
        else:
            from multiprocessing import Process, Queue

            # Worker arguments, leave seed argmument out as it is added in as workers are created
            worker_args = (fs, func, args.p0, args.grids, args.ubounds, args.lbounds, args.constants, args.misid, 
                           args.cuda, args.maxeval, args.maxtime)

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [Process(target=_worker_func, args=(infer_demography, in_queue, out_queue, worker_args)) for ii in range(args.threads)]
            # Put the tasks to be done in the queue.
            for ii in range(args.optimizations):
                new_seed = np.random.randint(1,1e6)
                in_queue.put(new_seed)
            # Start the workers
            for worker in workers:
                worker.start()

        # Collect and process results
        from dadi_cli.BestFit import get_bestfit_params
        for _ in range(args.optimizations):
            if args.work_queue: 
                result = q.wait().output
            else:
                result = out_queue.get()
            # Write latest result to file
            # Check that the log-likelihood is not a weird value
            if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                result = (-np.inf,) + result[1:]

            fid.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
            fid.flush()
            if args.check_convergence or args.force_convergence:
                result = get_bestfit_params(path=args.output_prefix+'.InferDM.opts.*',
                                            lbounds=args.lbounds, ubounds=args.ubounds, output=args.output_prefix+'.InferDM.bestfits',
                                            delta=args.delta_ll)
                if result is not None:
                    args.force_convergence = False
                    break
        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()
    fid.close()
    # TODO: Stop the remaining work_queue workers


def run_infer_dfe(args):
    fs = dadi.Spectrum.from_file(args.fs)
    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not (fs.folded or args.nomisid)

    # # Things need to be updated for these to work
    if None not in [args.pdf1d, args.pdf2d]:
        pass
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf !=  None:
                if not args.pdf_file and args.constants != -1: args.constants, _ = _check_pdf_params(args.constants, pdf, '--constant', args.misid)
                if not args.pdf_file and args.lbounds != -1: args.lbounds, _ = _check_pdf_params(args.lbounds, pdf, '--lbounds', args.misid)
                if not args.pdf_file and args.ubounds != -1: args.ubounds, _ = _check_pdf_params(args.ubounds, pdf, '--ubounds', args.misid)

    if args.p0 == -1: args.p0 = _calc_p0_from_bounds(args.lbounds, args.ubounds)

    from dadi_cli.utilities import get_opts_and_theta
    _, theta = get_opts_and_theta(args.demo_popt) 
    theta *= args.ratio

    import pickle
    if args.cache1d != None:
        cache1d = pickle.load(open(args.cache1d, 'rb'))
    else: cache1d = args.cache1d
    if args.cache2d != None:
        cache2d = pickle.load(open(args.cache2d, 'rb'))
    else: cache2d = args.cache2d

    if args.maxeval == False: args.maxeval = max(len(args.p0)*100,1)

    from dadi_cli.InferDFE import infer_dfe
    existing_files = glob.glob(args.output_prefix+'.InferDFE.opts.*')
    try:
        newest_file_num = max([int(ele.split('.')[-1]) for ele in existing_files]) + 1
    except:
        newest_file_num = 0
    fid = open(args.output_prefix+'.InferDFE.opts.{0}'.format(newest_file_num), 'a')
    # Write command line to results file
    import sys
    fid.write('# {0}\n'.format(' '.join(sys.argv)))

    # Write column headers
    if args.mix_pdf != None:
        param_names = get_dadi_pdf_params(args.mix_pdf)
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf !=  None:
                _, param_names = _check_pdf_params(args.p0, pdf, '', args.misid)
    
    param_names = '# Log(likelihood)\t' + '\t'.join(param_names)
    if not args.nomisid: param_names += '\tmisid'
    fid.write(param_names+'\ttheta\n')

    # Randomize or set seed for starting parameter values
    if args.seed == None: 
        import time, os
        ts = time.time()
        args.seed = int(time.time()) + int(os.getpid())
    import random
    np.random.seed(args.seed)

    converged = False
    while not converged:
        if not args.force_convergence:
            converged = True
        if args.work_queue:
            import work_queue as wq
            if args.debug_wq:
                q = wq.WorkQueue(name = args.work_queue[0], debug_log = 'debug.log')
            else:
                q = wq.WorkQueue(name = args.work_queue[0])
            # Returns 1 for success, 0 for failure
            if not q.specify_password_file(args.work_queue[1]):
                raise ValueError('Work Queue password file "{0}" not found.'.format(args.work_queue[1]))

            for ii in range(args.optimizations): 
                new_seed = np.random.randint(1,1e6)
                t = wq.PythonTask(infer_dfe, fs, cache1d, cache2d, args.pdf1d, args.pdf2d, theta, 
                args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda, 
                args.maxeval, args.maxtime, new_seed)
                # # If using a custom model, need to include the file from which it comes
                # if args.pdf_file:
                #     t.specify_input_file(args.pdf_file+'.py')
                q.submit(t)
        else:
            from multiprocessing import Process, Queue
            worker_args = (fs, cache1d, cache2d, args.pdf1d, args.pdf2d, theta, 
            args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda, args.maxeval, args.maxtime)

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [Process(target=_worker_func, args=(infer_dfe, in_queue, out_queue, worker_args)) for ii in range(args.threads)]
            # Put the tasks to be done in the queue. 
            for ii in range(args.optimizations):
                new_seed = np.random.randint(1,1e6)
                in_queue.put(new_seed)
            # Start the workers
            for worker in workers:
                worker.start()

        # Collect and process results
        from dadi_cli.BestFit import get_bestfit_params
        # If fitting two population DFE, 
        # determine if Pdf is symetrical or asymetrical
        independent_selection = None
        if args.pdf2d != None:
            if 'biv_' in args.pdf2d:
                len_params = len(args.p0)
                if args.misid: len_params - 1
                if len_params == 3: independent_selection = False
                else: independent_selection = True
        for _ in range(args.optimizations):
            if args.work_queue: 
                result = q.wait().output
            else:
                result = out_queue.get()
            # Write latest result to file
            # Check that the log-likelihood is not a weird value
            if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                result = (-np.inf,) + result[1:]
            fid.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
            fid.flush()
            if args.check_convergence or args.force_convergence:
                result = get_bestfit_params(path=args.output_prefix+'.InferDFE.opts.*',
                                            lbounds=args.lbounds, ubounds=args.ubounds,
                                            output=args.output_prefix+'.InferDFE.bestfits', delta=args.delta_ll)
                if result is not None:
                    converged = True
                    break
        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()
    fid.close()


def run_bestfit(args):
    from dadi_cli.BestFit import get_bestfit_params
    get_bestfit_params(path=args.input_prefix+'.opts.*', delta=args.delta_ll, lbounds=args.lbounds, ubounds=args.ubounds, output=args.input_prefix+'.bestfits')


def run_stat_demography(args):
    from dadi_cli.Stat import godambe_stat_demograpy

    # Extract model function, from custom model_file if necessary
    func = get_model(args.model, args.model_file)

    godambe_stat_demograpy(fs=args.fs, func=func, bootstrap_dir=args.bootstrapping_dir, grids=args.grids,
                           nomisid=args.nomisid, demo_popt=args.demo_popt, fixed_params=args.constants,
                           logscale=args.logscale, output=args.output)


def run_stat_dfe(args):
    from dadi_cli.Stat import godambe_stat_dfe

    godambe_stat_dfe(fs=args.fs, bootstrap_non_dir=args.bootstrapping_non_dir, 
                     bootstrap_syn_dir=args.bootstrapping_syn_dir, 
                     cache1d=args.cache1d, cache2d=args.cache2d, 
                     sele_dist=args.pdf1d, sele_dist2=args.pdf2d,
                     nomisid=args.nomisid, dfe_popt=args.dfe_popt,
                     fixed_params=args.constants,
                     logscale=args.logscale, output=args.output)


def run_plot(args):
    from dadi_cli.Plot import plot_comparison, plot_fitted_demography, plot_fitted_dfe, plot_single_sfs, plot_mut_prop
   
    if args.fs == None:
        if args.ratio == False:
            raise Exception("Need to pass value to --ratio option")
        plot_mut_prop(dfe_popt=args.dfe_popt, pdf1d=args.pdf1d, nomisid=args.nomisid, mut_rate=args.mut_rate, seq_len=args.seq_len, ratio=args.ratio, output=args.output)
    elif args.dfe_popt != None:
        plot_fitted_dfe(fs=args.fs, cache1d=args.cache1d, cache2d=args.cache2d, pdf=args.pdf1d, pdf2=args.pdf2d, nomisid=args.nomisid,
                        demo_popt=args.demo_popt, sele_popt=args.dfe_popt, vmin=args.vmin, resid_range=args.resid_range,
                        projections=args.projections, output=args.output)
    elif args.demo_popt != None:
        plot_fitted_demography(fs=args.fs, model=args.model, popt=args.demo_popt, vmin=args.vmin,
                               projections=args.projections, nomisid=args.nomisid, resid_range=args.resid_range, output=args.output)
    elif args.fs2 == None:
        plot_single_sfs(fs=args.fs, projections=args.projections, output=args.output, vmin=args.vmin)
    else:
        plot_comparison(fs=args.fs, fs2=args.fs2, projections=args.projections, output=args.output, vmin=args.vmin, resid_range=args.resid_range)


def run_model(args):
    if args.names == None:
        print_built_in_models()
    else:
        print_built_in_model_details(args.names)


def run_pdf(args):
    from dadi_cli.Pdfs import print_available_pdfs, print_pdf_details
    if args.names == None:
        print_available_pdfs()
    else:
        print_pdf_details(args.names)


def add_output_argument(parser):
    parser.add_argument('--output', type=str, required=True, help='Name of the output file')


def add_cuda_argument(parser):
    parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')


def add_bounds_argument(parser):
    parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='Lower bounds of the optimized parameters')
    parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='Upper bounds of the optimized parameters')


def add_demo_popt_argument(parser):
    parser.add_argument('--demo-popt', type=str, required=True, help='File contains the bestfit parameters for the demographic model', dest='demo_popt')


def add_grids_argument(parser):
    parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='Sizes of grids. Default: None')


def add_misid_argument(parser):
    # Note that the code previously had a --misid function that did the opposite, but this ia more sensible default.
    parser.add_argument('--nomisid', default=False, action='store_true', help='Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized.')


def add_model_argument(parser):
    parser.add_argument('--model', type=str, required=True, help='Name of the demographic model. To check available demographic models, please use `dadi-cli Model`')


def add_fs_argument(parser):
    parser.add_argument('--fs', type=str, required=True, help='Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`')


def add_seed_argument(parser):
    parser.add_argument('--seed', type=_check_positive_int, help='Random seed')


def add_constant_argument(parser):
    parser.add_argument('--constants', default=-1, type=float, nargs='+', help='Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None')


def add_delta_ll_argument(parser):
    parser.add_argument('--delta-ll', type=_check_positive_num, required=False, dest='delta_ll', default=0.0001, help='When using --check-convergence argument in InferDM or InferDFE modules or the BestFits module, set the max percentage difference for log-likliehoods compared to the best optimization log-likliehood to be consider convergent (with 1 being 100%% difference to the best optimization\'s log-likelihood). Default: 0.0001')


def add_popt_argument(parser):
    parser.add_argument('--demo-popt', type=str, dest='demo_popt', help='File contains the bestfit demographic parameters, generated by `dadi-cli BestFit`')
    parser.add_argument('--dfe-popt', type=str, dest='dfe_popt', help='File contains the bestfit DFE parameters, generated by `dadi-cli BestFit`')


def add_dfe_argument(parser):
    parser.add_argument('--cache1d', type=str, help='File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`')
    parser.add_argument('--cache2d', type=str, help='File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`')
    parser.add_argument('--pdf1d', type=str, help='1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`')
    parser.add_argument('--pdf2d', type=str, help='2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`')
    parser.add_argument('--mix-pdf', dest='mix_pdf', type=str, default=None, help='If you are using a model that is a mixture of probability density function for the joint DFE inference pass in the model name. To check available probability density functions, please use `dadi-cli Pdf`')


def add_inference_argument(parser):
    parser.add_argument('--p0', default=-1, type=float, nargs='+', required=False, help='Initial parameter values for inference.')
    parser.add_argument('--output-prefix', type=str, required=True, dest='output_prefix', help='Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).')
    parser.add_argument('--optimizations', default=3, type=_check_positive_int, help='Number of optimizations to run in parallel. Default: 3.')
    parser.add_argument('--check-convergence', default=False, action='store_true', dest='check_convergence', help='Stop optimization runs when convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Default: False')
    parser.add_argument('--force-convergence', default=False, action='store_true', dest='force_convergence', help='Only stop optimization once convergence criteria is reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Default: False')
    parser.add_argument('--work-queue', nargs=2, default=[], action='store', dest='work_queue', help='Enable Work Queue. Additional arguments are the WorkQueue project name and the name of the password file.')
    parser.add_argument('--debug-wq', default=False, action='store_true', dest='debug_wq', help='Store debug information from WorkQueue to a file called "debug.log". Default: False')
    parser.add_argument('--maxeval', type=_check_positive_int, default=False, help='Max number of parameter set evaluations tried for optimizing demography. Default: Number of parameters multiplied by 100')
    parser.add_argument('--maxtime', type=_check_positive_int, default=np.inf, help='max amount of time for optimizing demography. Default: infinite')
    parser.add_argument('--threads', type=_check_positive_int, default=multiprocessing.cpu_count(), help='number of threads using in multiprocessing. Default: All available threads')


def add_simulation_argument(parser):
    parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='Sizes of grids. Default: None')
    parser.add_argument('--misid', dest='misid', default=False, action='store_true', help='Enable to include a parameter modeling ancestral state misidentification when data are polarized ; Default: False')
    parser.add_argument('--p0', type=float, nargs='+', required=True, help='Parameters for simulated demography or dfe.')


def dadi_cli_parser():
    top_parser = argparse.ArgumentParser()
    subparsers = top_parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    parser = subparsers.add_parser('GenerateFs', help='Generate frequency spectrum from VCF files')
    parser.add_argument('--polarized', default=False, action='store_true', help='Determine whether the resulting frequency spectrum is polarized or not; Default: False')
    parser.add_argument('--pop-ids', type=str, nargs='+', required=True, help='Population names for the samples', dest='pop_ids')
    parser.add_argument('--pop-info', type=str, required=True, help='Name of the file containing the population name of each sample', dest='pop_info')
    parser.add_argument('--projections', type=_check_positive_int, nargs='+', required=True, help='Sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data')
    parser.add_argument('--vcf', type=str, required=True, help='Name of the VCF file for generating frequency spectrum')
    parser.add_argument('--bootstrap', type=_check_positive_int, help='Times to perform bootstrapping')
    parser.add_argument('--chunk-size', type=_check_positive_int, help='Chunk size to divide the genomes for bootstrapping', dest='chunk_size')
    parser.add_argument('--subsample', default=False, action='store_true', dest='subsample', help='Subsample from the VCF when generating the fs using the given pop-ids and subsample calls based on the projections passed in. Default: None')
    parser.add_argument('--mask-singletons', default=False, action='store_true', dest='mask', help='Mask the singletons that are exclusive to each population. Default: None')
    parser.add_argument('--mask-shared-singletons', default=False, action='store_true', dest='mask_shared', help='Mask the singletons that are exclusive to each population and shared between populations. Default: None')
    parser.add_argument('--marginalize-pop-ids', type=str, nargs='+', help='Population names you want to marginalize (remove) from the full fs. Default: None', dest='marginalize_pops')
    add_output_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=run_generate_fs)

    parser = subparsers.add_parser('GenerateCache', help='Generate selection coefficient cache for inferring DFE')
    parser.add_argument('--additional-gammas', type=_check_positive_num, nargs='+', default=[], help='Additional positive population-scaled selection coefficients to cache for. Default: []', dest='additional_gammas')
    parser.add_argument('--gamma-bounds', type=_check_positive_num, nargs=2, default=[1e-4, 2000], help='Range of population-scaled selection coefficients to cache. Default: [1e-4, 2000]', dest='gamma_bounds')
    parser.add_argument('--gamma-pts', type=_check_positive_int, default=50, help='Number of gamma grid points over which to integrate. Default: 50', dest='gamma_pts')
    parser.add_argument('--mp', default=False, action='store_true', help='Determine whether generating cache with multiprocess or not; Default: False')
    parser.add_argument('--sample-sizes', type=_check_positive_int, nargs='+', required=True, help='Sample sizes of populations', dest='sample_sizes')
    parser.add_argument('--dimensionality', type=int, default=1, help='Determine whether using demographic model plus selection with the same gamma in both the two populations or not. Default: 1', dest='dimensionality')
    parser.add_argument('--model-file', type=str, required=False, dest='model_file', help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    add_output_argument(parser)
    add_cuda_argument(parser)
    add_demo_popt_argument(parser)
    add_grids_argument(parser)
    add_model_argument(parser)
    parser.set_defaults(runner=run_generate_cache)

    parser = subparsers.add_parser('SimulateDM', help='Generate frequency spectrum based on a demographic history')
    add_model_argument(parser)
    parser.add_argument('--sample-sizes', dest='ns', type=_check_positive_int, nargs='+', required=True, help='Sample sizes for simulated populations')
    parser.add_argument('--model-file', type=str, required=False, dest='model_file', help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    add_simulation_argument(parser)
    parser.add_argument('--inference-file', dest='inference_file', default=False, action='store_true', help='Make an output file like you would get for running InferDM to pass into GenerateCache to make caches with your simulated demographic model. Will be the same name and path as output + ".SimulateFs.pseudofit"; Default: False')
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_dm)

    parser = subparsers.add_parser('SimulateDFE', help='Generate frequency spectrum based on a DFE')
    add_dfe_argument(parser)
    parser.add_argument('--ratio', type=float, required=True, help='Ratio for the nonsynonymous mutations to the synonymous mutations')
    add_simulation_argument(parser)
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_dfe)

    parser = subparsers.add_parser('SimulateDemes', help='Generate frequency spectrum based on a Demes .yml file')
    parser.add_argument('--demes-file', type=str, required=True, dest='demes_file', help='Name of Demes .yml file that contains model to simulate.')
    parser.add_argument('--pop-ids', default=True, type=str, nargs='+', required=False, help='Population names for the samples, required for Demes', dest='pop_ids')
    add_simulation_argument(parser)
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_demes)

    parser = subparsers.add_parser('InferDM', help='Infer a demographic models from an allele frequency spectrum')
    add_fs_argument(parser)
    add_inference_argument(parser)
    add_delta_ll_argument(parser)
    add_cuda_argument(parser)
    add_model_argument(parser)
    parser.add_argument('--model-file', type=str, required=False, dest='model_file', help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    add_grids_argument(parser)
    add_misid_argument(parser)
    add_constant_argument(parser)
    add_bounds_argument(parser)
    parser.add_argument('--global-optimization', default=False, action='store_true', dest='global_optimization', help='Use global optimization before doing local optimization. Default: False')
    add_seed_argument(parser)
    parser.set_defaults(runner=run_infer_dm)

    parser = subparsers.add_parser('InferDFE', help='Infer distribution of fitness effects from frequency spectrum')
    add_fs_argument(parser)
    parser.add_argument('--demo-popt', type=str, dest='demo_popt', help='File contains the bestfit parameters for the demographic model')
    add_dfe_argument(parser)
    parser.add_argument('--ratio', type=float, required=True, help='Ratio for the nonsynonymous mutations to the synonymous mutations')
    parser.add_argument('--pdf-file', type=str, required=False, dest='pdf_file', help='Name of python probability density function module file (not including .py) that contains custom probability density functions to use. Default: None')
    add_inference_argument(parser)
    add_delta_ll_argument(parser)
    add_cuda_argument(parser)
    add_misid_argument(parser)
    add_constant_argument(parser)
    add_bounds_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=run_infer_dfe)

    parser = subparsers.add_parser('Plot', help='Plot 1D/2D frequency spectrum')
    add_fs_argument(parser)
    parser.add_argument('--fs2', type=str, help='Name of the second frequency spectrum for comparison, generated by `dadi-cli GenerateFs`')
    add_popt_argument(parser)
    add_model_argument(parser)
    add_dfe_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    parser.add_argument('--mut-rate', type=float, dest='mut_rate', help='Mutation rate for estimating the ancestral population size')
    parser.add_argument('--seq-len', type=int, dest='seq_len', help='Sequence length for estimating the ancestral population size')
    parser.add_argument('--projections', type=int, nargs='+', help='Sample sizes after projection')
    parser.add_argument('--resid-range', type=float, dest='resid_range', help='Ranges of the residual plots')
    parser.add_argument('--vmin', type=float, default=0.1, help='Minimum value to be plotted in the frequency spectrum, default: 0.1')
    parser.add_argument('--ratio', type=float, default=False, required=False, help='Ratio for the nonsynonymous mutations to the synonymous mutations')
    parser.set_defaults(runner=run_plot)

    parser = subparsers.add_parser('StatDM', help='Perform statistical tests using Godambe Information Matrix for demographic models')
    add_fs_argument(parser)
    add_model_argument(parser)
    add_grids_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    add_constant_argument(parser)
    parser.add_argument('--demo-popt', type=str, dest='demo_popt', help='File contains the bestfit demographic parameters, generated by `dadi-cli BestFit`')
    parser.add_argument('--model-file', type=str, required=False, dest='model_file', help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    parser.add_argument('--bootstrapping-dir', type=str, required=True, help='Directory containing boostrapping spectra', dest='bootstrapping_dir')
    parser.add_argument('--logscale', default=False, action='store_true', help='Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False')
    parser.set_defaults(runner=run_stat_demography)

    parser = subparsers.add_parser('StatDFE', help='Perform statistical tests using Godambe Information Matrix for DFEs')
    add_fs_argument(parser)
    add_dfe_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    add_constant_argument(parser)
    parser.add_argument('--dfe-popt', type=str, dest='dfe_popt', help='File contains the bestfit DFE parameters, generated by `dadi-cli BestFit`')
    parser.add_argument('--bootstrapping-nonsynonymous-dir', type=str, required=True, help='Directory containing boostrapping spectra', dest='bootstrapping_non_dir')
    parser.add_argument('--bootstrapping-synonymous-dir', type=str, required=True, help='Directory containing boostrapping spectra, required to adjust nonsynonymous theta for differences in synonymous theta', dest='bootstrapping_syn_dir')
    parser.add_argument('--logscale', default=False, action='store_true', help='Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False')
    parser.set_defaults(runner=run_stat_dfe)

    parser = subparsers.add_parser('BestFit', help='Obtain the best fit parameters')
    parser.add_argument('--input-prefix', type=str, required=True, dest='input_prefix', help='Prefix for input files, which is named <input-prefix ending with ".InferDM">.opts.<N> or <input-prefix ending with "InferDFE">.opts.<N>, containing the inferred demographic or DFE parameters')
    add_bounds_argument(parser)
    add_delta_ll_argument(parser)
    parser.set_defaults(runner=run_bestfit)

    parser = subparsers.add_parser('Model', help='display available demographic models')
    parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='display the details of a given model for demographic inference')
    parser.set_defaults(runner=run_model)

    parser = subparsers.add_parser('Pdf', help='display available probability density functions for distribution of fitness effects')
    parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='display the details of a given probability density distribution for DFE inference')
    parser.set_defaults(runner=run_pdf)

    return top_parser


# helper functions for reading, parsing, and validating parameters from command line or files
def _check_params(params, model, option, misid):
    input_params_len = len(params)
    model_params_len = len(get_dadi_model_params(model, None))
    if misid: input_params_len = input_params_len - 1
    if input_params_len != model_params_len:
        raise Exception("\nFound " + str(input_params_len) + " demographic parameters from the option " + option + 
                        "; however, " + str(model_params_len) + " demographic parameters are required from the " + model + " model" +
                        "\nYou might be using the wrong model or need to add --nomisid if you did not use ancestral allele information to polarize the fs.")
    return params


def _check_pdf_params(params, pdf, option, misid):
    input_params_len = len(params)
    if misid: input_params_len = input_params_len - 1
    if pdf == 'biv_lognormal' or pdf == 'biv_ind_gamma': 
        if input_params_len in [2,3]: 
            mod='_sym'
        else: 
            mod='_asym'
        pdf=pdf.replace('biv','biv'+mod)
    model_params_len = len(get_dadi_pdf_params(pdf))
    param_names = get_dadi_pdf_params(pdf)
    if input_params_len != model_params_len:
        raise Exception("Found " + str(input_params_len) + " pdf parameters from the option " + option + 
                        "; however, " + str(model_params_len) + " pdf parameters are required from the " + pdf + " pdf")
    return params, param_names


def _check_positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("only accepts postive integers; %s is an invalid value" % value)
    return ivalue


def _check_positive_num(value):
    fvalue = float(value)
    if fvalue <= 0:
        raise argparse.ArgumentTypeError("only accepts postive numbers; %s is an invalid value" % value)
    return fvalue


def _calc_p0_from_bounds(lb, ub):
    p0 = []
    for l, u in zip(lb, ub):
        if l == 0:
            p0.append((l+u)/2)
        else:
            p0.append(np.sqrt(l*u))
    return p0


def _check_dir(path):
    parent_dir = os.path.dirname(path)
    if not os.path.isdir(parent_dir):
        raise argparse.ArgumentTypeError("directory %s does not exist" % parent_dir)
    return path


# Main function
def main(arg_list=None):
    set_sigpipe_handler()
    parser = dadi_cli_parser()
    args = parser.parse_args(arg_list)
    args.runner(args)
