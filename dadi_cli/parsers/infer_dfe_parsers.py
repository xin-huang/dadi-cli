import argparse, glob, pickle, os, random, sys, time, warnings
from multiprocessing import Process, Queue
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.utilities import *
from dadi_cli.InferDFE import *
from dadi_cli.BestFit import *
from dadi_cli.Pdfs import *


def _run_infer_dfe(args: argparse.Namespace) -> None:
    """
    Run the inference of the distribution of fitness effects (DFE) from genetic data.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object from argparse containing all the necessary settings for the
        analysis. Expected keys include:
        - fs : str
            Path or URL to the frequency spectrum data file.
        - misid : bool
            Whether misidentification corrections are to be applied.
        - output_prefix : str
            Prefix for all output files generated by this function.
        - pdf1d : str or None
            The 1D probability distribution function name.
        - pdf2d : str or None
            The 2D probability distribution function name.
        - pdf_file : bool
            Flag indicating whether a custom PDF file is used.
        - constants : list or int
            List of constants for the PDFs or -1 if not using constants.
        - lbounds : list or None
            Lower bounds for parameter optimization.
        - ubounds : list or None
            Upper bounds for parameter optimization.
        - p0 : list or int
            Initial parameters for optimization or -1 to automatically generate.
        - demo_popt : str
            Path or URL to the file containing optimized demographic parameters.
        - ratio : float
            Scaling factor for theta.
        - cache1d : str or None
            Path or URL to cache file for 1D computation.
        - cache2d : str or None
            Path or URL to cache file for 2D computation.
        - maxeval : int
            Maximum number of evaluations for the optimizer.
        - seed : int or None
            Seed for random number generation for reproducibility.
        - optimizations : int
            Number of optimization iterations to perform.
        - check_convergence : int
            The number of optimizations to perform before checking for convergence.
        - force_convergence : bool
            Force the process to continue until convergence is achieved.
        - delta_ll : float
            Log-likelihood threshold for convergence.
        - work_queue : list or None
            Configuration for distributed computing using Work Queue.
        - debug_wq : bool
            Enable debugging for Work Queue operations.
        - port : int
            Network port to use for Work Queue operations.
        - cpus : int
            Number of CPU cores to allocate for local parallel processing.
        - gpus : int
            Number of GPU units to allocate for local parallel processing.
        - bestfit_p0 : str or None
            Path or URL to the file with best fit parameters.
        - nomisid : bool
            Flag to indicate that misidentification should not be considered.
        - cov_args : list
            Dictionary that contains the data dictionary with coverage information 
            and total number of sample sequenced in each population for coverage correction.
        - cov_inbreeding : list
            Inbreeding parameter for each population from 0 to 1, see dadi manual for more information.
        - mix_pdf : str or None
            The mixed PDF model if applicable.

    """
    # Make sure flags are used:
    if args.pdf1d == None and args.pdf2d == None:
        raise ValueError("Require --pdf1d and/or --pdf2d depending on DFE model")
    if args.cache1d == None and agrs.cache2d == None:
        raise ValueError("cache1d --pdf1d and/or --cache2d depending on DFE model")
    if "://" in args.fs:
        import urllib.request
        sfs_fi = open("sfs.fs","w")
        with urllib.request.urlopen(args.fs) as f:
            sfs_fi.write(f.read().decode('utf-8'))
        sfs_fi.close()
        args.fs ="sfs.fs"

    fs = dadi.Spectrum.from_file(args.fs)
    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not (fs.folded or args.nomisid)

    if args.cov_args != []:
        args.cov_args[0] = pickle.load(open(args.cov_args[0], 'rb'))

    make_dir(args.output_prefix)

    # Converts str to float and None string to None value
    args.lbounds, args.ubounds, args.constants = convert_bounds_and_constants(args.lbounds, args.ubounds, args.constants)

    # # Things need to be updated for these to work
    if None not in [args.pdf1d, args.pdf2d]:
        pass
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf != None:
                if not args.pdf_file and args.constants != -1:
                    args.constants, _ = check_pdf_params(
                        args.constants, pdf, "--constant", args.misid
                    )
                if not args.pdf_file and args.lbounds != -1:
                    args.lbounds, _ = check_pdf_params(
                        args.lbounds, pdf, "--lbounds", args.misid
                    )
                if not args.pdf_file and args.ubounds != -1:
                    args.ubounds, _ = check_pdf_params(
                        args.ubounds, pdf, "--ubounds", args.misid
                    )

    if args.p0 == -1:
        args.p0 = calc_p0_from_bounds(args.lbounds, args.ubounds)


    if "://" in args.demo_popt:
        import urllib.request
        popt_fi = open("demo-popt.bestfits","w")
        with urllib.request.urlopen(args.demo_popt) as f:
            popt_fi.write(f.read().decode('utf-8'))
        popt_fi.close()
        args.demo_popt = "demo-popt.bestfits"

    _, theta = get_opts_and_theta(args.demo_popt)
    theta *= args.ratio

    if args.cache1d != None:
        if "://" in args.cache1d:
            from urllib.request import urlopen
            cache1d = pickle.load(urlopen(args.cache1d))
        else:
            cache1d = pickle.load(open(args.cache1d, "rb"))
        cache_ns = cache1d.ns
    else:
        cache1d = args.cache1d

    if args.cache2d != None:
        if "://" in args.cache2d:
            from urllib.request import urlopen
            cache2d = pickle.load(urlopen(args.cache2d))
        else:
            cache2d = pickle.load(open(args.cache2d, "rb"))
        cache_ns = cache2d.ns
    else:
        cache2d = args.cache2d

    if not np.all(cache_ns == fs.sample_sizes):
        raise ValueError('Cache and frequencey spectrum do not have the same sample sizes')

    if args.maxeval == False:
        args.maxeval = max(len(args.p0) * 100, 1)


    existing_files = glob.glob(args.output_prefix + ".InferDFE.opts.*")
    try:
        newest_file_num = max([int(ele.split(".")[-1]) for ele in existing_files]) + 1
    except:
        newest_file_num = 0
    results_file = args.output_prefix + ".InferDFE.opts.{0}".format(newest_file_num)
    fid = open(results_file, "a")
    # Write command line to results file

    fid.write("# {0}\n".format(" ".join(sys.argv)))

    # Write column headers
    if args.mix_pdf != None:
        param_names = get_dadi_pdf_params(args.mix_pdf)
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf != None:
                _, param_names = check_pdf_params(args.p0, pdf, "", args.misid)

    param_names = "# Log(likelihood)\t" + "\t".join(param_names)
    if args.misid:
        param_names += "\tmisid"
    fid.write(param_names + "\ttheta\n")

    # Randomize or set seed for starting parameter values
    if args.seed == None:
        ts = time.time()
        args.seed = int(time.time()) + int(os.getpid())

    np.random.seed(args.seed)

    # Keep track of number of optimizations before checking convergence
    num_opts = 0

    # Keep track when optimization happens with force-convergence
    converged = False

    # Raise warning if --check-convergence larger than --optimizations
    # This isn't required for --force-convergence, as it optimizes until convergence occures.
    if args.optimizations < args.check_convergence:
        warnings.warn("WARNING: Number of optimizations is less than the number requested before checking convergence. Convergence will not be checked. \n" +
            "Note: if using --global-optimization, ~25% of requested optimizations are used for the gloabal optimization.\n")

    while not converged:
        if not args.force_convergence:
            converged = True

        # Check if we can get a list of top fits
        if args.bestfit_p0 is not None:
            if "://" in args.bestfit_p0:
                import urllib.request
                best_fi = open("bestfits_file.bestfits","w")
                with urllib.request.urlopen(args.bestfit_p0) as f:
                    best_fi.write(f.read().decode('utf-8'))
                best_fi.close()
                args.bestfit_p0 = "bestfits_file.bestfits"
            bestfits = top_opts(args.bestfit_p0)
        else:
            bestfits = None

        if args.work_queue:
            try:
                import ndcctools.work_queue as wq
            except ModuleNotFoundError:
                raise ValueError("Work Queue could not be loaded.")

            if args.debug_wq:
                q = wq.WorkQueue(name=args.work_queue[0], debug_log="debug.log", port=args.port)
            else:
                q = wq.WorkQueue(name=args.work_queue[0], port=args.port)
            # Returns 1 for success, 0 for failure
            if not q.specify_password_file(args.work_queue[1]):
                raise ValueError(
                    'Work Queue password file "{0}" not found.'.format(
                        args.work_queue[1]
                    )
                )

            for ii in range(args.optimizations):
                new_seed = np.random.randint(1, 1e6)
                t = wq.PythonTask(
                    infer_dfe,
                    fs,
                    cache1d,
                    cache2d,
                    args.pdf1d,
                    args.pdf2d,
                    theta,
                    args.p0,
                    args.ubounds,
                    args.lbounds,
                    args.constants,
                    args.misid,
                    args.cov_args,
                    args.cov_inbreeding,
                    None,
                    args.maxeval,
                    args.maxtime,
                    bestfits,
                    new_seed,
                )
                # # If using a custom model, need to include the file from which it comes
                # if args.pdf_file:
                #     t.specify_input_file(args.pdf_file+'.py')
                q.submit(t)
        else:
            worker_args = (
                fs,
                cache1d,
                cache2d,
                args.pdf1d,
                args.pdf2d,
                theta,
                args.p0,
                args.ubounds,
                args.lbounds,
                args.constants,
                args.misid,
                args.cov_args,
                args.cov_inbreeding,
                None,
                args.maxeval,
                args.maxtime,
                bestfits,
            )

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [
                Process(
                    target=worker_func,
                    args=(infer_dfe, in_queue, out_queue, worker_args)
                )
                for ii in range(args.cpus)
            ]
            workers.extend([
                Process(target=worker_func,
                    args=(infer_dfe, in_queue, out_queue, worker_args, True))
                for ii in range(args.gpus)
            ])
            # Put the tasks to be done in the queue.
            for ii in range(args.optimizations):
                new_seed = np.random.randint(1, 1e6)
                in_queue.put(new_seed)
            # Start the workers
            for worker in workers:
                worker.start()

        # Collect and process results

        # If fitting two population DFE,
        # determine if Pdf is symetrical or asymetrical
        independent_selection = None
        if args.pdf2d != None:
            if "biv_" in args.pdf2d:
                len_params = len(args.p0)
                if args.misid:
                    len_params - 1
                if len_params == 3:
                    independent_selection = False
                else:
                    independent_selection = True

        for _ in range(args.optimizations):
            if args.work_queue:
                result = q.wait().output
            else:
                result = out_queue.get()
            num_opts += 1
            # Write latest result to file
            # Check that the log-likelihood is not a weird value
            # print('\n\n\n\n\n\nCACHE LL:',float(result[0]),'\n\n\n\n\n')
            if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                result = (-np.inf,) + result[1:]
            fid.write(
                "{0}\t{1}\t{2}\n".format(
                    result[0], "\t".join(str(_) for _ in result[1]), result[2]
                )
            )
            fid.flush()
            if (args.check_convergence or args.force_convergence) and num_opts >= (args.check_convergence or args.force_convergence):
                results_file = args.output_prefix + ".InferDFE.bestfits"
                result = get_bestfit_params(
                    path=args.output_prefix + ".InferDFE.opts.*",
                    lbounds=args.lbounds,
                    ubounds=args.ubounds,
                    output=args.output_prefix + ".InferDFE.bestfits",
                    delta=args.delta_ll,
                )
                if result is not None:
                    converged = True
                    break
        if not args.work_queue:
            # Stop the workers
            for worker in workers:
                worker.terminate()
    fid.close()


def add_infer_dfe_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds parser for the "InferDFE" command to the subparsers collection. This function
    sets up command-line arguments specific to inferring the distribution of fitness
    effects (DFE) from allele frequency spectra.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "InferDFE",
        help="Infer distribution of fitness effects from frequency spectrum.",
    )
    add_fs_argument(parser)
    parser.add_argument(
        "--demo-popt",
        type=existed_file,
        dest="demo_popt",
        help="File contains the bestfit parameters for the demographic model.",
    )
    add_dfe_argument(parser)
    add_mix_pdf_argument(parser)
    parser.add_argument(
        "--ratio",
        type=positive_num,
        required=True,
        help="Ratio for the nonsynonymous mutations to the synonymous mutations.",
    )
    parser.add_argument(
        "--pdf-file",
        type=str,
        required=False,
        dest="pdf_file",
        help="Name of python probability density function module file (not including .py) that contains custom probability density functions to use. Default: None.",
    )
    add_inference_argument(parser)
    add_delta_ll_argument(parser)
    add_misid_argument(parser)
    add_coverage_model_argument(parser)
    add_constant_argument(parser)
    add_bounds_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=_run_infer_dfe)
