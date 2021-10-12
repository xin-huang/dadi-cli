import argparse, glob, os.path, sys
import os.path
import dadi

from src.InferDM import infer_demography
from src.InferDFE import infer_dfe
from src.Models import get_dadi_model_params
from src.Pdfs import get_dadi_pdf_params

# Worker functions for multiprocessing with demography/DFE inference
def worker_InferDM(in_queue, out_queue, args):
    while True:
        in_queue.get()
        results = infer_demography(*args)
        out_queue.put(results)

def worker_InferDFE(in_queue, out_queue, args):
    while True:
        in_queue.get()
        results = infer_dfe(*args)
        out_queue.put(results)


# Main function
def main():
    
    # helper functions for reading, parsing, and validating parameters from command line or files
    def _check_params(params, model, option, misid):
        input_params_len = len(params)
        model_params_len = len(get_dadi_model_params(model))
        if misid: input_params_len = input_params_len - 1
        if input_params_len != model_params_len:
            raise Exception("Found " + str(input_params_len) + " demographic parameters from the option " + option + 
                            "; however, " + str(model_params_len) + " demographic parameters are required from the " + model + " model")
        return params

    def _check_pdf_params(params, pdf, option, misid):
        input_params_len = len(params)
        model_params_len = len(get_dadi_pdf_params(pdf))
        if misid: input_params_len = input_params_len - 1
        if input_params_len != model_params_len:
            raise Exception("Found " + str(input_params_len) + " pdf parameters from the option " + option + 
                            "; however, " + str(model_params_len) + " pdf parameters are required from the " + pdf + " pdf")
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
    generate_cache_parser.add_argument('--additional-gammas', type=_check_positive_num, nargs='+', default=[], help='Additional positive population-scaled selection coefficients to cache for. Default: []', dest='additional_gammas')
    generate_cache_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not. Default: False')
    #generate_cache_parser.add_argument('--demo-popt', type=float, required=True, nargs='+', default=[], help='The bestfit parameters for the demographic model; Default: []', dest='demo_popt')
    generate_cache_parser.add_argument('--demo-popt', type=str, required=True, help='File contains the bestfit parameters for the demographic model', dest='demo_popt')
    generate_cache_parser.add_argument('--gamma-bounds', type=_check_positive_num, nargs=2, default=[1e-4, 2000], help='Range of population-scaled selection coefficients to cache. Default: [1e-4, 2000]', dest='gamma_bounds')
    generate_cache_parser.add_argument('--gamma-pts', type=_check_positive_int, default=50, help='Number of gamma grid points over which to integrate. Default: 50', dest='gamma_pts')
    generate_cache_parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='Sizes of grids. Default: None')
    generate_cache_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether the parameter for ancestral state misidentification exists in the bestfit parameters. Default: False')
    generate_cache_parser.add_argument('--model', type=str, required=True, help='Name of the demographic model with selection. To check available demographic models, please use `dadi-cli Model`')
    generate_cache_parser.add_argument('--mp', default=False, action='store_true', help='Determine whether generating cache with multiprocess or not; Default: False')
    generate_cache_parser.add_argument('--output', type=str, required=True, help='Name of the output file')
    generate_cache_parser.add_argument('--sample-sizes', type=_check_positive_int, nargs='+', required=True, help='Sample sizes of populations', dest='sample_sizes')
    generate_cache_parser.add_argument('--single-gamma', default=False, action='store_true', help='Determine whether using demographic model plus selection with the same gamma in both the two populations or not. Default: False', dest='single_gamma')


    # subparser for inferring demography
    infer_demo_parser = subparsers.add_parser('InferDM', help='Infer a demographic models from an allele frequency spectrum')
    # TODO: Need to workout how to do this well for parallel execution. Don't want multiple workers competing for limited GPUs
    infer_demo_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
    infer_demo_parser.add_argument('--fs', type=str, required=True, help='Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    infer_demo_parser.add_argument('--constants', type=float, nargs='+', help='Fixed parameters during the inference. Use -1 to indicate a parameter is NOT fixed. Default: None')
    infer_demo_parser.add_argument('--grids', type=_check_positive_int, nargs=3, help='Integration grid sizes. Default: (int(n*1.1)+2, int(n*1.2)+4, int(n*1.3)+6)')
    infer_demo_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='Lower bounds for parameter inference. Use -1 to indicate a parameter without lower bound.')
    infer_demo_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='Upper bounds for parameter inference. Use -1 to indicate a parameter without upper bound.')
    infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='Add a parameter for ancestral state misidentification. Default: False')
    infer_demo_parser.add_argument('--model', type=str, required=True, help='Name of the demographic model. To check built-in demographic models, use `dadi-cli Model`.')
    infer_demo_parser.add_argument('--model-file', type=str, required=False, dest='model_file', help='Name of python module file (not including .py) that contains custom models to use. Default: None')
    infer_demo_parser.add_argument('--p0', type=str, nargs='+', required=True, help='Initial parameter values for inference.')
    infer_demo_parser.add_argument('--output-prefix', type=str, required=True, dest='output_prefix', help='Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).')
    infer_demo_parser.add_argument('--optimization', default=1, type=_check_positive_int, help='Number of optimizations to run in parallel. Default: 1.')
    infer_demo_parser.add_argument('--check-convergence', default=False, action='store_true', dest='check_convergence', help='Stop optimization runs when convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Default: False')
    infer_demo_parser.add_argument('--work-queue', nargs=2, default=[], action='store', dest='work_queue', help='Enable Work Queue. Additional arguments are the WorkQueue project name and the name of the password file.')


    # subparser for inferring DFE
    infer_dfe_parser = subparsers.add_parser('InferDFE', help='Infer distribution of fitness effects from frequency spectrum')
    infer_dfe_parser.add_argument('--cache1d', type=str, help='File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`')
    infer_dfe_parser.add_argument('--cache2d', type=str, help='File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`')
    infer_dfe_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not. Default: False')
    infer_dfe_parser.add_argument('--constants', type=float, nargs='+', help='Fixed parameters during the inference. Use -1 to indicate a parameter is NOT fixed. Default: None')
    infer_dfe_parser.add_argument('--demo-popt', type=str, dest='demo_popt', help='The bestfit parameters for the demographic model')
    infer_dfe_parser.add_argument('--fs', type=str, required=True, help='Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`')
    infer_dfe_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='Lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
    infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not. Default: False')
    #infer_dfe_parser.add_argument('--nlopt', default=False, action='store_true', help='Determine whether using nlopt or not; Default: False')
    infer_dfe_parser.add_argument('--p0', type=float, nargs='+', required=True, help='Initial parameters for inference')
    infer_dfe_parser.add_argument('--pdf1d', type=str, help='1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`')
    infer_dfe_parser.add_argument('--pdf2d', type=str, help='2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`')
    infer_dfe_parser.add_argument('--ratio', type=float, required=True, help='Ratio for the nonsynonymous mutations to the synonymous mutations')
    infer_dfe_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='Upper bounds of the inferred parameters, please use -1 to indicate a parameter with no upper bound, please use -1 to indicate a parameter without upper bound')
    infer_dfe_parser.add_argument('--output-prefix', type=str, required=True, dest='output_prefix', help='Prefix for output files, which will be named <output_prefix>.InferDFE.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).')
    infer_dfe_parser.add_argument('--optimization', default=1, type=_check_positive_int, help='Number of optimizations to run in parallel. Default: 1.')
    infer_dfe_parser.add_argument('--check-convergence', default=False, action='store_true', dest='check_convergence', help='Stop optimization runs when convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDFE.bestfits. Default: False')
    infer_dfe_parser.add_argument('--pdf-file', type=str, required=False, dest='pdf_file', help='Name of python probability density function module file (not including .py) that contains custom probability density functions to use. Default: None')
    infer_dfe_parser.add_argument('--work-queue', nargs=2, default=[], action='store', dest='work_queue', help='Enable Work Queue. Additional arguments are the WorkQueue project name and the name of the password file.')


    # subparser for plotting
    plot_parser = subparsers.add_parser('Plot', help='Plot 1D/2D frequency spectrum')
    plot_parser.add_argument('--demo-popt', type=str, dest='demo_popt', help='file contains the bestfit demographic parameters, generated by `dadi-cli BestFit`')
    plot_parser.add_argument('--dfe-popt', type=str, dest='dfe_popt', help='file contains the bestfit DFE parameters, generated by `dadi-cli BestFit`')
    plot_parser.add_argument('--cache1d', type=str, help='name of the 1D DFE cache, generated by `dadi-cli GenerateCache`')
    plot_parser.add_argument('--cache2d', type=str, help='name of the 2D DFE cache, generated by `dadi-cli GenerateCache`')
    plot_parser.add_argument('--fs', type=str, help='name of the frequency spectrum, generated by `dadi-cli GenerateFs`')
    plot_parser.add_argument('--fs2', type=str, help='name of the second frequency spectrum for comparison, generated by `dadi-cli GenerateFs`')
    plot_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
    plot_parser.add_argument('--mut-rate', type=float, dest='mut_rate', help='mutation rate for estimating the ancestral population size')
    plot_parser.add_argument('--seq-len', type=int, dest='seq_len', help='sequence length for estimating the ancestral population size')
    plot_parser.add_argument('--demo-model', type=str, dest='model', help='name of the demographic model; please use `dadi-cli Model` to check available demographic models')
    plot_parser.add_argument('--ratio', type=float, help='ratio for nonsynonymous to synonymous mutations')
    plot_parser.add_argument('--output', type=str, help='name of the output file')
    plot_parser.add_argument('--projections', type=int, nargs='+', help='sample sizes after projection')
    plot_parser.add_argument('--resid-range', type=float, dest='resid_range', help='ranges of the residual plots')
    plot_parser.add_argument('--pdf1d', type=str, help='1D probability density function for the DFE inference; please use `dadi-cli Pdf` to check available probability density functions')
    plot_parser.add_argument('--pdf2d', type=str, help='2D probability density function for the joint DFE inference; please use `dadi-cli Pdf`to check available probability density function')
    plot_parser.add_argument('--vmin', type=float, default=0.1, help='minimum value to be plotted in the frequency spectrum, default: 0.1')


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
    bestfit_parser = subparsers.add_parser('BestFit', help='obtain the best fit parameters')
    bestfit_parser.add_argument('--input-prefix', type=str, required=True, dest='input_prefix', help='prefix for input files, which is named <input_prefix>.InferDM.opts.<N> or <input_prefix>.InferDFE.opts.<N>, containing the inferred demographic or DFE parameters')
    bestfit_parser.add_argument('--model', type=str, help='name of the demographic model')
    bestfit_parser.add_argument('--pdf', type=str, help='name of the DFE model')
    bestfit_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='lower bounds of the optimized parameters, please use -1 to indicate a parameter without lower bound')
    bestfit_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='upper bounds of the optimized parameters, please use -1 to indicate a parameter without upper bound')
    bestfit_parser.add_argument('--misid', default=False, action='store_true', help='determine whether the parameter for misidentifying ancestral alleles is used or not; default: False')


    # subparser for getting the available demographic models in dadi
    model_parser = subparsers.add_parser('Model', help='display available demographic models')
    model_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='display the details of a given model for demographic inference')


    # subparser for getting the available probability distribution for DFE in dadi
    dist_parser = subparsers.add_parser('Pdf', help='display available probability density functions for distribution of fitness effects')
    dist_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='display the details of a given probability density distribution for DFE inference')


    args = parser.parse_args()


    # assign task from subcommand
    if args.subcommand == 'GenerateFs':

        from src.GenerateFs import generate_fs
        generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size,
                    pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

    elif args.subcommand == 'GenerateCache':
        from src.GenerateCache import generate_cache
        #args.demo_popt = _read_opt_params_from_file(args.demo_popt, args.model, '--model', False)

        generate_cache(model=args.model, grids=args.grids, popt=args.demo_popt, misid=args.misid,
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

            for ii in range(args.optimization): 
                t = wq.PythonTask(infer_demography, fs, func, args.p0, args.grids, 
                                  args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)
                # If using a custom model, need to include the file from which it comes
                if args.model_file:
                    t.specify_input_file(args.model_file+'.py')
                q.submit(t)
        else:
            import multiprocessing; from multiprocessing import Process, Queue

            worker_args = (fs, func, args.p0, args.grids, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [Process(target=worker_InferDM, args=(in_queue, out_queue, worker_args)) for ii in range(multiprocessing.cpu_count())]
            # Put the tasks to be done in the queue. 
            for ii in range(args.optimization):
                in_queue.put(ii)
            # Start the workers
            for worker in workers:
                worker.start()

        existing_files = glob.glob(args.output_prefix+'.InferDM.opts.*')
        fid = open(args.output_prefix+'.InferDM.opts.{0}'.format(len(existing_files)), 'a')
        # Write command line to results file
        fid.write('# {0}\n'.format(' '.join(sys.argv)))
        # Collect and process results
        from src.BestFit import get_bestfit_params
        for _ in range(args.optimization):
            if args.work_queue: 
                result = q.wait().output
            else:
                result = out_queue.get()
            # Write latest result to file
            fid.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
            fid.flush()
            if args.check_convergence:
                result = get_bestfit_params(path=args.output_prefix+'.InferDM.opts.*', model_name=args.model, misid=args.misid,
                                            lbounds=args.lbounds, ubounds=args.ubounds, output=args.output_prefix+'.InferDM.bestfits')
                if result is not None:
                    break
        fid.close()

        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()
        # TODO: Stop the remaining work_queue workers

    elif args.subcommand == 'InferDFE':
        # Things need to be updated for these to work
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf !=  None:
                if not args.pdf_file and args.constants != None: args.constants = _check_pdf_params(args.constants, pdf, '--constant', args.misid)
                if not args.pdf_file and args.lbounds != None: args.lbounds = _check_pdf_params(args.lbounds, pdf, '--lbounds', args.misid)
                if not args.pdf_file and args.ubounds != None: args.ubounds = _check_pdf_params(args.ubounds, pdf, '--ubounds', args.misid)

        from src.InferDFE import infer_dfe
        if args.work_queue:
            import work_queue as wq
            q = wq.WorkQueue(name = args.work_queue[0])
            # Returns 1 for success, 0 for failure
            if not q.specify_password_file(args.work_queue[1]):
                raise ValueError('Work Queue password file "{0}" not found.'.format(args.work_queue[1]))

            for ii in range(args.optimization): 
                t = wq.PythonTask(infer_dfe, args.fs, args.cache1d, args.cache2d, args.pdf1d, args.pdf2d, 
                                args.ratio, args.demo_popt, args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)
                # # If using a custom model, need to include the file from which it comes
                # if args.pdf_file:
                #     t.specify_input_file(args.pdf_file+'.py')
                q.submit(t)
        else:
            import multiprocessing; from multiprocessing import Process, Queue

            #worker_args = (fs, func, args.p0, args.grids, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)
            worker_args = (args.fs, args.cache1d, args.cache2d, args.pdf1d, args.pdf2d, args.ratio, args.demo_popt, args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda)

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [Process(target=worker_InferDFE, args=(in_queue, out_queue, worker_args)) for ii in range(multiprocessing.cpu_count())]
            # Put the tasks to be done in the queue. 
            for ii in range(args.optimization):
                in_queue.put(ii)
            # Start the workers
            for worker in workers:
                worker.start()
        
        existing_files = glob.glob(args.output_prefix+'.InferDFE.opts.*')
        fid = open(args.output_prefix+'.InferDFE.opts.{0}'.format(len(existing_files)), 'a')
        # Write command line to results file
        fid.write('# {0}\n'.format(' '.join(sys.argv)))
        # Collect and process results
        from src.BestFit import get_bestfit_params
        for _ in range(args.optimization):
            if args.work_queue: 
                result = q.wait().output
            else:
                result = out_queue.get()
            # Write latest result to file
            fid.write('{0}\t{1}\t{2}\n'.format(result[0], '\t'.join(str(_) for _ in result[1]), result[2]))
            fid.flush()
            if args.check_convergence:
                result = get_bestfit_params(path=args.output_prefix+'.InferDFE.opts.*', lbounds=args.lbounds, ubounds=args.ubounds, output=args.output_prefix+'.InferDFE.bestfits')
                if result is not None:
                    break
        fid.close()

        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()
        # TODO: Stop the remaining work_queue workers
            
            #from multiprocessing import Manager, Process, Queue
            #with Manager() as manager:
            #    pool = []
            #    for i in range(args.optimization):
            #        p = Process(target=infer_dfe,
            #                    args=(args.non_fs, args.output+'.run'+str(i), args.cache1d, args.cache2d, args.pdf1d, args.pdf2d, 
            #                          args.ratio, args.demo_popt, args.p0, args.ubounds, args.lbounds, args.constants, args.misid, args.cuda))
            #        p.start()
            #        pool.append(p)

            #    for p in pool:
            #        p.join()

    elif args.subcommand == 'Plot':

        from src.Plot import plot_comparison, plot_fitted_demography, plot_fitted_dfe, plot_single_sfs, plot_mut_prop
   
        if args.fs == None:
            plot_mut_prop(dfe_popt=args.dfe_popt, pdf1d=args.pdf1d, misid=args.misid, mut_rate=args.mut_rate, seq_len=args.seq_len, ratio=args.ratio, output=args.output)
        elif args.dfe_popt != None:
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
        # XXX: Need to automatically try different eps settings.
        from src.Stat import godambe_stat
        godambe_stat(fs=args.fs, model=args.model, bootstrap_dir=args.bootstrapping_dir, grids=args.grids,
                     cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf1d, ns_s=args.ratio,
                     sele_dist2=args.pdf2d, dfe_popt=args.dfe_popt, misid=args.misid, demo_popt=args.demo_popt,
                     logscale=args.logscale, output=args.output)

    elif args.subcommand == 'BestFit':
        #args.lbounds = check_params(args.lbounds)
        #args.ubounds = check_params(args.ubounds)

        from src.BestFit import get_bestfit_params
        get_bestfit_params(path=args.input_prefix+'.opts.*', model_name=args.model, pdf_name=args.pdf, misid=args.misid, lbounds=args.lbounds, ubounds=args.ubounds, output=args.input_prefix+'.bestfits')

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
