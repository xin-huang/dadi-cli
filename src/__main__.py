import argparse, glob, os.path, sys
import os.path
import dadi

def main():
    
    from src.Models import get_dadi_model_params

    # helper functions for reading, parsing, and validating parameters from command line or files
    def _check_params(params, model, option, misid):
        input_params_len = len(params)
        model_params_len = len(get_dadi_model_params(model))
        if misid: input_params_len = input_params_len - 1
        if input_params_len != model_params_len:
            raise Exception("Found " + str(input_params_len) + " demographic parameters from the option " + option + 
                            "; however, " + str(model_params_len) + " demographic parameters are required from the " + model + " model")
        return params

    def _read_opt_params_from_file(path, model, option, misid):
        new_params = []
        line = open(path, 'r').readline().rstrip().split()
        for p in line:
            new_params.append(float(p))
        # the first parameter is the likelihood
        # the second parameter is theta
        # the last parameter is misid
        new_params = new_params[2:-1]
        _check_params(new_params, model, option, misid)
        return new_params

    def _parse_params_from_command(params, model, option, misid):
        new_params = []
        for p in params:
            if p == 'None': new_params.append(None)
            else: new_params.append(float(p))
        _check_params(new_params, model, option, misid)
        return new_params

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

    def _check_dir(path):
        parent_dir = os.path.dirname(path)
        if not os.path.isdir(parent_dir):
            raise argparse.ArgumentTypeError("directory %s does not exist" % parent_dir)
        return path

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='Commands', dest='subcommand')
    subparsers.required = True

    # subparser for generating frequency spectrum
    generate_fs_parser = subparsers.add_parser('GenerateFs', help='Generate frequency spectrum from VCF files')
    generate_fs_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
    generate_fs_parser.add_argument('--polarized', default=False, action='store_true', help='Determine whether the resulting frequency spectrum is polarized or not; Default: False')
    generate_fs_parser.add_argument('--pop-ids', type=str, nargs='+', required=True, help='The population names for the samples', dest='pop_ids')
    generate_fs_parser.add_argument('--pop-info', type=str, required=True, help='The name of the file containing the population name of each sample', dest='pop_info')
    generate_fs_parser.add_argument('--projections', type=_check_positive_int, nargs='+', required=True, help='The sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data')
    generate_fs_parser.add_argument('--vcf', type=str, required=True, help='The VCF file for generating frequency spectrum')
    generate_fs_parser.add_argument('--bootstrap', type=_check_positive_int, help='The times to perform bootstrapping')
    generate_fs_parser.add_argument('--chunk-size', type=_check_positive_int, help='The chunk size to divide the genomes for bootstrapping', dest='chunk_size')

    # subparser for generating cache
    generate_cache_parser = subparsers.add_parser('GenerateCache', help='Generate selection coefficient cache for inferring DFE')
    generate_cache_parser.add_argument('--additional-gammas', type=_check_positive_num, nargs='+', default=[], help='The additional positive population-scaled selection coefficients to cache for; Default: []', dest='additional_gammas')
    generate_cache_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
    generate_cache_parser.add_argument('--demo-popt', type=str, required=True, help='The bestfit parameters for the demographic model; Default: []', dest='demo_popt')
    generate_cache_parser.add_argument('--gamma-bounds', type=_check_positive_num, nargs=2, default=[1e-4, 2000], help='The range of population-scaled selection coefficients to cache; Default: [1e-4, 2000]', dest='gamma_bounds')
    generate_cache_parser.add_argument('--gamma-pts', type=_check_positive_int, default=50, help='The number of gamma grid points over which to integrate; Default: 50', dest='gamma_pts')
    generate_cache_parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='The sizes of grids; Default: None')
    generate_cache_parser.add_argument('--model', type=str, required=True, help='The name of the demographic model with selection; To check available demographic models, please use `dadi-cli Model`')
    generate_cache_parser.add_argument('--mp', default=False, action='store_true', help='Determine whether generating cache with multiprocess or not; Default: False')
    generate_cache_parser.add_argument('--output', type=_check_dir, required=True, help='The name of the output file')
    generate_cache_parser.add_argument('--sample-sizes', type=_check_positive_int, nargs='+', required=True, help='The sample sizes of populations', dest='sample_sizes')
    generate_cache_parser.add_argument('--single-gamma', default=False, action='store_true', help='Determine whether using demographic model plus selection with the same gamma in both the two populations or not; Default: False', dest='single_gamma')

    # subparser for inferring demography
    infer_demo_parser = subparsers.add_parser('InferDM', help='Infer a demographic models from an allele frequency spectrum')
    # TODO: Need to workout how to do this well for parallel execution. Don't want multiple workers competing for limited GPUs
    infer_demo_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
    infer_demo_parser.add_argument('--fs', type=str, required=True, help='The frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    infer_demo_parser.add_argument('--constants', type=float, nargs='+', help='Fixed parameters during the inference. Use -1 to indicate a parameter is NOT fixed. Default: None')
    infer_demo_parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='Integration grid sizes. Default: (int(n*1.1)+2, int(n*1.2)+4, int(n*1.3)+6)')
    infer_demo_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='Lower bounds for parameter inference. Use -1 to indicate a parameter without lower bound.')
    infer_demo_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='Upper bounds for parameter inference. Use -1 to indicate a parameter without upper bound.')
    infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='Add a parameter for ancestral state misidentification. Default: False')
    infer_demo_parser.add_argument('--model', type=str, required=True, help='Name of the demographic model. To check built-in demographic models, use `dadi-cli Model`.')
    infer_demo_parser.add_argument('--model_file', type=str, required=False, help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    infer_demo_parser.add_argument('--p0', type=str, nargs='+', required=True, help='Initial parameter values for inference.')
    infer_demo_parser.add_argument('--output_prefix', type=str, required=True, help='Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).')
    infer_demo_parser.add_argument('--jobs', default=1, type=_check_positive_int, help='Number of optimization jobs to run in parallel. Default: 1.')
    infer_demo_parser.add_argument('--check_convergence', default=False, action='store_true', help='Stop optimization runs when convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Default: False')
    infer_demo_parser.add_argument('--work_queue', nargs=2, default=[], action='store', help='Enable Work Queue. Additional arguments are the WorkQueue project name and the name of the password file.')

    # subparser for inferring DFE
    infer_dfe_parser = subparsers.add_parser('InferDFE', help='Infer distribution of fitness effects from frequency spectrum')
    infer_dfe_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    infer_dfe_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    infer_dfe_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
    infer_dfe_parser.add_argument('--constants', type=float, nargs='+', help='The fixed parameters during the inference, please use -1 to indicate a parameter is NOT fixed; Default: None')
    infer_dfe_parser.add_argument('--demo-popt', type=str, help='The bestfit parameters for the demographic model', dest='demo_popt')
    infer_dfe_parser.add_argument('--syn-fs', type=str, help='The frequency spectrum of the synonymous mutations; To generate the frequency spectrum, please use `dadi-cli GenerateFs`', dest='syn_fs')
    infer_dfe_parser.add_argument('--non-fs', type=str, required=True, help='The frequency spectrum of the non-synonymous mutations; To generate the frequency spectrum, please use `dadi-cli GenerateFs`', dest='non_fs')
    infer_dfe_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
    infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
    infer_dfe_parser.add_argument('--nlopt', default=False, action='store_true', help='Determine whether using nlopt or not; Default: False')
    infer_dfe_parser.add_argument('--p0', type=float, nargs='+', required=True, help='The initial parameters for inference')
    infer_dfe_parser.add_argument('--pdf1d', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-cli Pdf`')
    infer_dfe_parser.add_argument('--pdf2d', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-cli Pdf`')
    infer_dfe_parser.add_argument('--ratio', type=float, help='The ratio for the nonsynonymous mutations vs. the synonymous mutations')
    infer_dfe_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the inferred parameters, please use -1 to indicate a parameter with no upper bound, please use -1 to indicate a parameter without upper bound')
    infer_dfe_parser.add_argument('--output', type=str, help='The name of the output file')
    infer_dfe_parser.add_argument('--jobs', default=1, type=_check_positive_int, help='The number of jobs to run optimization parrallelly')

    # subparser for plotting
    plot_parser = subparsers.add_parser('Plot', help='Plot 1D/2D frequency spectrum')
    plot_parser.add_argument('--demo-popt', type=str, help='The file containing the bestfit parameters for the demographic model, generated by `dadi-cli Bestfit`', dest='demo_popt')
    plot_parser.add_argument('--dfe-popt', type=str, help='The file containing the bestfit parameters for the distribution of fitness effects, generated by `dadi-cli Bestfit`', dest='dfe_popt')
    plot_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    plot_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    plot_parser.add_argument('--fs', type=str, required=True, help='The name of the frequency spectrum; To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    plot_parser.add_argument('--fs2', type=str, help='The name of the second frequency spectrum for comparison; To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    plot_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
    plot_parser.add_argument('--demo-model', type=str, help='The name of the demographic model; To check available demographic models, please use `dadi-cli Model`', dest='model')
    plot_parser.add_argument('--ratio', type=float, help='The ratio for nonsynonymous to synonymous mutations')
    plot_parser.add_argument('--output', type=str, help='The name of the output file')
    plot_parser.add_argument('--projections', type=int, nargs='+', help='The sample sizes after projection')
    plot_parser.add_argument('--resid-range', type=float, help='The ranges of the residual plots', dest='resid_range')
    plot_parser.add_argument('--pdf1d', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-cli Pdf`')
    plot_parser.add_argument('--pdf2d', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-cli Pdf')
    plot_parser.add_argument('--vmin', type=float, default=0.1, help='The minimum value to be plotted in the frequency spectrum; Default: 0.1')

    # subparser for statistics and uncertainty analysis
    stat_parser = subparsers.add_parser('Stat', help='Perform statistical tests using Godambe Information Matrix')
    stat_parser.add_argument('--fs', type=str, required=True, help='The name of the frequency spectrum; To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    stat_parser.add_argument('--demo-model', type=str, help='The name of the demographic model; To check available demographic models, please use `dadi-cli Model`', dest='model')
    stat_parser.add_argument('--grids', type=int, nargs=3, default=[40, 50, 60], help='The sizes of the grids; Default: [40, 50, 60]')
    stat_parser.add_argument('--misid',  default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
    stat_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    stat_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-cli GenerateCache`')
    stat_parser.add_argument('--bootstrapping-dir', type=str, required=True, help='The Directory containing boostrapping spectra', dest='bootstrapping_dir')
    stat_parser.add_argument('--pdf1d', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-cli Pdf`')
    stat_parser.add_argument('--pdf2d', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-cli Pdf')
    stat_parser.add_argument('--demo-popt', type=str, required=True, help='The file containing the best fit parameters for the demographic model, generated by `dadi-cli Bestfit`', dest='demo_popt')
    stat_parser.add_argument('--dfe-popt', type=str, help='The file containing the best fit parameters for the DFE, generated by `dadi-cli Bestfit`', dest='dfe_popt')
    stat_parser.add_argument('--ratio', type=float, help='The ratio for nonsynonymous to synonymous mutations')
    stat_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
    stat_parser.add_argument('--logscale', default=False, action='store_true', help='Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False')

    # subparser for getting the best fit parameters
    bestfit_parser = subparsers.add_parser('BestFit', help='Obtain the best fit parameters')
    bestfit_parser.add_argument('--dir', type=str, required=True, help='The directory containing the inferred demographic/dfe parameters')
    bestfit_parser.add_argument('--output', type=str, required=True, help='The name of the ouput file')
    bestfit_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the optimized parameters, please use -1 to indicate a parameter without lower bound')
    bestfit_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the optimized parameters, please use -1 to indicate a parameter without upper bound')

    # subparser for getting the available demographic models in dadi
    model_parser = subparsers.add_parser('Model', help='Display available demographic models')
    model_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='Show the details of a given model')

    # subparser for getting the available probability distribution for DFE in dadi
    dist_parser = subparsers.add_parser('Pdf', help='Display available probability density functions for distribution of fitness effects')
    dist_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='Show the details of a given probability density distribution')

    args = parser.parse_args()

    # assign task from subcommand
    if args.subcommand == 'GenerateFs':

        from src.GenerateFs import generate_fs
        generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size,
                    pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

    elif args.subcommand == 'GenerateCache':
        from src.GenerateCache import generate_cache
        args.demo_popt = _read_opt_params_from_file(args.demo_popt, args.model, '--model', False)

        generate_cache(model=args.model, grids=args.grids, popt=args.demo_popt,
                       gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                       output=args.output, sample_sizes=args.sample_sizes, mp=args.mp, cuda=args.cuda, single_gamma=args.single_gamma)

    elif args.subcommand == 'InferDM':
        if not args.model_file and args.constants != None: args.constants = _check_params(args.constants, args.model, '--constant', args.misid)
        if not args.model_file and args.lbounds != None: args.lbounds = _check_params(args.lbounds, args.model, '--lbounds', args.misid)
        if not args.model_file and args.ubounds != None: args.ubounds = _check_params(args.ubounds, args.model, '--ubounds', args.misid)

        if len(args.p0) == 1: 
            args.p0 = float(args.p0)
        else: 
            args.p0 = [float(_) for _ in args.p0]

        from src.InferDM import infer_demography
        fs = dadi.Spectrum.from_file(args.fs)

        # Extract model function, from custom model_file if necessary
        from src.Models import get_dadi_model_func
        if not args.model_file:
            func = get_dadi_model_func(args.model)
        else:
            import importlib
            func = getattr(importlib.import_module(args.model_file), args.model)

        if args.work_queue:
            import work_queue as wq
            q = wq.WorkQueue(name = args.work_queue[0])
            # Returns 1 for success, 0 for failure
            if not q.specify_password_file(args.work_queue[1]):
                raise ValueError('Work Queue password file "{0}" not found.'.format(args.work_queue[1]))

            for ii in range(args.jobs): 
                t = wq.PythonTask(infer_demography, fs, func, args.p0, args.grids, 
                               args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)
                # If using a custom model, need to include the file from which it comes
                if args.model_file:
                    t.specify_input_file(args.model_file+'.py')
                q.submit(t)
        else:
            import multiprocessing; from multiprocessing import Process, Queue
            from src.InferDM import infer_demography

            def todo(in_queue, out_queue):
                while True:
                    i = in_queue.get()
                    results = infer_demography(fs, func, args.p0, args.grids,
                                     args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)
                    out_queue.put(results)

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [Process(target=todo, args=(in_queue, out_queue)) for ii in range(multiprocessing.cpu_count())]
            # Put the tasks to be done in the queue. 
            for ii in range(args.jobs):
                in_queue.put(ii)
            # Start the workers
            for worker in workers:
                worker.start()

        existing_files = glob.glob(args.output_prefix+'.InferDM.opts.*')
        fid = open(args.output_prefix+'.InferDM.opts.{0}'.format(len(existing_files)), 'a')
        # Write command line to results file
        fid.write('#{0}\n'.format(' '.join(sys.argv)))
        # Collect and process results
        from src.BestFit import get_bestfit_params
        for _ in range(args.jobs):
            if args.work_queue: 
                result = q.wait().output
            else:
                result = out_queue.get()
            # Write latest result ot file
            fid.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
            fid.flush()
            if args.check_convergence:
                result = get_bestfit_params(path=args.output_prefix+'.InferDM.opts.*', lbounds=args.lbounds, ubounds=args.ubounds, output=args.output_prefix+'.InferDM.bestfits')
                if result is not None:
                    break
        fid.close()

        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()

    elif args.subcommand == 'InferDFE':
   
        if args.constants != None: args.constants = check_params(args.constants)
        if args.lbounds != None: args.lbounds = check_params(args.lbounds)
        if args.ubounds != None: args.ubounds = check_params(args.ubounds)

        from multiprocessing import Manager, Process, Queue
        from src.InferDFE import infer_dfe
        with Manager() as manager:

            pool = []
            for i in range(args.jobs):
                p = Process(target=infer_dfe,
                            args=(args.non_fs, args.output+'.run'+str(i), args.cache1d, args.cache2d, args.pdf1d, args.pdf2d, 
                                  args.ratio, args.demo_popt, args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda))
                p.start()
                pool.append(p)

            for p in pool:
                p.join()

    elif args.subcommand == 'Plot':

        from src.Plot import plot_comparison, plot_fitted_demography, plot_fitted_dfe, plot_single_sfs
    
        if args.dfe_popt != None:
            plot_fitted_dfe(fs=args.fs, cache1d=args.cache1d, cache2d=args.cache2d, pdf=args.pdf1d, pdf2=args.pdf2d, misid=args.misid,
                            demo_popt=args.demo_popt, sele_popt=args.dfe_popt, vmin=args.vmin, resid_range=args.resid_range,
                            ns_s=args.ratio, projections=args.projections, output=args.output)
        elif args.demo_popt != None:
            if len(args.demo_popt) == 1: 
                args.demo_popt = read_demo_params(args.demo_popt[0])
            if args.misid: args.demo_popt = args.demo_popt[:-1]
            else: args.demo_popt = parse_demo_params(args.demo_popt)
            plot_fitted_demography(fs=args.fs, model=args.model, popt=args.demo_popt, vmin=args.vmin,
                                   projections=args.projections, misid=args.misid, resid_range=args.resid_range, output=args.output)
        elif args.fs2 == None:
            plot_single_sfs(fs=args.fs, projections=args.projections, output=args.output, vmin=args.vmin)
        else:
            plot_comparison(fs=args.fs, fs2=args.fs2, projections=args.projections, output=args.output, vmin=args.vmin, resid_range=args.resid_range)

    elif args.subcommand == 'Stat':

        from src.Stat import godambe_stat
        godambe_stat(fs=args.fs, model=args.model, bootstrap_dir=args.bootstrapping_dir, grids=args.grids,
                     cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf1d, ns_s=args.ratio,
                     sele_dist2=args.pdf2d, dfe_popt=args.dfe_popt, misid=args.misid, demo_popt=args.demo_popt,
                     logscale=args.logscale, output=args.output)

    elif args.subcommand == 'BestFit':
        #args.lbounds = check_params(args.lbounds)
        #args.ubounds = check_params(args.ubounds)

        from src.BestFit import get_bestfit_params
        get_bestfit_params(path=args.dir+'.opts.*', lbounds=args.lbounds, ubounds=args.ubounds, output=args.dir+'.bestfits')

    elif args.subcommand == 'Model':
    
        from src.Models import print_available_models, print_model_details
        if args.names == None:
            print_available_models()
        else:
            print_model_details(args.names)

    elif args.subcommand == 'Pdf':

        from src.Pdfs import print_available_pdfs, print_pdf_details
        if args.names == None:
            print_available_pdfs()
        else:
            print_pdf_details(args.names)
