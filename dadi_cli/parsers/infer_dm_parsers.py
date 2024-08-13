import argparse, inspect, nlopt, os, random, sys, time, warnings
from multiprocessing import Process, Queue
from sys import exit
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.InferDM import *
from dadi_cli.utilities import *
from dadi_cli.BestFit import *
from dadi_cli.Models import *


def _run_infer_dm(args: argparse.Namespace) -> None:
    """
    Executes demographic model inference based on command line arguments provided.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace containing all command line arguments. Expected keys include:
        - fs : str
            Path or URL to the frequency spectrum data file.
        - model_file : str
            Path or URL to a Python script containing demographic model definitions.
        - output_prefix : str
            Prefix for all output files generated by this function.
        - model : str
            Name of the demographic model to use for inference.
        - p0 : list or int
            Initial parameter values for optimization or -1 to auto-generate.
        - lbounds : list or None
            Lower bounds for parameter values during optimization.
        - ubounds : list or None
            Upper bounds for parameter values during optimization.
        - grids : list or None
            Grid sizes to use in demographic calculations.
        - misid : bool
            Flag to indicate if misidentification handling should be enabled.
        - cov_args : list
            Dictionary that contains the data dictionary with coverage information 
            and total number of sample sequenced in each population for coverage correction.
        - cov_inbreeding : list
            Inbreeding parameter for each population from 0 to 1, see dadi manual for more information.
        - seed : int or None
            Seed for random number generation to ensure reproducibility.
        - maxeval : int
            Maximum number of evaluations for the optimizer.
        - constants : list or int
            Constants used in the model, or -1 if not applicable.
        - global_optimization : bool
            Flag to enable or disable global optimization.
        - optimizations : int
            Number of optimization iterations to perform.
        - work_queue : list or None
            Configuration for distributed computation using Work Queue.
        - nomisid : bool
            Flag to indicate if misidentification is not to be considered.
        - check_convergence : int
            Number of optimizations before checking for convergence.
        - bestfit_p0 : str or None
            Path or URL to the file with best fit parameters.
        - force_convergence : bool
            Flag to force convergence checks during optimization.
        - delta_ll : float
            Threshold for log-likelihood improvement considered as convergence.
        - debug_wq : bool
            Enable debugging for Work Queue.
        - port : int
            Network port to use for Work Queue operations.
        - cpus : int
            Number of CPU cores to allocate for local parallel processing.
        - gpus : int
            Number of GPU units to allocate for local parallel processing.

    """
    if "://" in args.fs:
        import urllib.request
        sfs_fi = open("sfs.fs","w")
        with urllib.request.urlopen(args.fs) as f:
            sfs_fi.write(f.read().decode('utf-8'))
        sfs_fi.close()
        args.fs ="sfs.fs"
    if args.model_file is not None:
        if "://" in args.model_file:
            model_fi = open("dadi_models.py","w")
            with urllib.request.urlopen(args.model_file) as f:
                model_fi.write(f.read().decode('utf-8'))
            model_fi.close()
            args.model_file = "dadi_models"

    fs = dadi.Spectrum.from_file(args.fs)

    make_dir(args.output_prefix)

    if args.cov_args != []:
        import pickle
        args.cov_args[0] = pickle.load(open(args.cov_args[0], 'rb'))

    # Because basic standard neutral models do not need to optimized
    # we can calculate the log-likelihood and theta
    if args.model in ['snm_1d', 'snm_2d'] and args.p0 == -1 and args.lbounds == None and args.ubounds == None:
        fid = open(args.output_prefix + ".InferDM.bestfits", "w")
        # Write command line to results file
        fid.write("# {0}\n".format(" ".join(sys.argv)))

        # Extract model function and parameter names, from custom model_file if necessary
        func, param_names = get_model(args.model, args.model_file)
        if args.grids is None:
            args.grids = pts_l_func(fs.sample_sizes)

        fid.write("# Log(likelihood)\t" + "\t".join(param_names) + "\ttheta\n")
        model = dadi.Numerics.make_extrap_func(func)([], fs.sample_sizes, args.grids)
        ll_model = dadi.Inference.ll_multinom(model, fs)
        theta = dadi.Inference.optimal_sfs_scaling(model, fs)
        fid.write('\t'.join(str(_) for _ in [ll_model, theta])+'\n')
        fid.close()
        exit()
    else:
        pass

    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not (fs.folded or args.nomisid)

    if not args.model_file and args.constants != -1:
        args.constants = check_params(
            args.constants, args.model, "--constant", args.misid
        )
    if not args.model_file and args.lbounds != -1:
        args.lbounds = check_params(args.lbounds, args.model, "--lbounds", args.misid)
    if not args.model_file and args.ubounds != -1:
        args.ubounds = check_params(args.ubounds, args.model, "--ubounds", args.misid)

    if args.p0 == -1:
        args.p0 = calc_p0_from_bounds(args.lbounds, args.ubounds)

    # Extract model function and parameter names, from custom model_file if necessary
    func, param_names = get_model(args.model, args.model_file)

    if args.maxeval == False:
        args.maxeval = max(len(args.p0) * 50, 1)

    existing_files = glob.glob(args.output_prefix + ".InferDM.opts.*")
    try:
        newest_file_num = max([int(ele.split(".")[-1]) for ele in existing_files]) + 1
    except:
        newest_file_num = 0
    results_file = args.output_prefix + ".InferDM.opts.{0}".format(newest_file_num)
    fid = open(results_file, "a")
    # Write command line to results file

    fid.write("# {0}\n".format(" ".join(sys.argv)))

    # Write column headers
    # Bugfix: use args.misid instead of args.nomisid.
    # Since args.misid can be true and args.nomisid can be false
    # due to checking for fs.folded, use args.misid for future commands.
    if args.misid:
        param_names += ["misid"]
    fid.write("# Log(likelihood)\t" + "\t".join(param_names) + "\ttheta\n")

    # Check if demographic function uses inbreeding, need to be done before wrapping

    if "from_phi_inbreeding" in inspect.getsource(func):
        inbreeding = True
    else:
        inbreeding = False

    # Randomize or set seed for starting parameter values
    if args.seed == None:
        ts = time.time()
        args.seed = int(time.time()) + int(os.getpid())

    np.random.seed(args.seed)

    if args.global_optimization:
        if inbreeding:
            warnings.warn("Warning: can't down project inbreeding data for global optimization\n")
        else:
            existing_files = glob.glob(args.output_prefix + ".global.InferDM.opts.*")
            try:
                newest_file_num = (
                    max([int(ele.split(".")[-1]) for ele in existing_files]) + 1
                )
            except:
                newest_file_num = 0
            fid_global = open(
                args.output_prefix + ".global.InferDM.opts.{0}".format(newest_file_num),
                "a",
            )
            # Write command line to global results file
            fid_global.write("# {0}\n".format(" ".join(sys.argv)))
            # Write column headers
            fid_global.write(
                "# Log(likelihood)\t" + "\t".join(param_names) + "\ttheta\n"
            )
            global_optimizations = round(args.optimizations * 0.25)
            args.optimizations -= global_optimizations
            # Determin if the global optimization algorithm is
            # one that can be seeded or random (unseeded).

            if args.seed == None:
                global_algorithm = nlopt.GN_MLSL
            else:
                global_algorithm = nlopt.GN_MLSL_LDS
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

                for ii in range(global_optimizations):
                    new_seed = np.random.randint(1, 1e6)
                    t = wq.PythonTask(
                        infer_global_opt,
                        fs,
                        func,
                        args.p0,
                        args.grids,
                        args.ubounds,
                        args.lbounds,
                        args.constants,
                        args.misid,
                        args.cov_args,
                        args.cov_inbreeding,
                        None,
                        args.maxeval,
                        args.maxtime,
                        global_algorithm,
                        new_seed,
                    )
                    # If using a custom model, need to include the file from which it comes
                    if args.model_file:
                        t.specify_input_file(args.model_file + ".py")
                    q.submit(t)
            else:

                worker_args = (
                    fs,
                    func,
                    args.p0,
                    args.grids,
                    args.ubounds,
                    args.lbounds,
                    args.constants,
                    args.misid,
                    args.cov_args,
                    args.cov_inbreeding,
                    None,
                    args.maxeval,
                    args.maxtime,
                    global_algorithm,
                )

                # Queues to manage input and output
                in_queue, out_queue = Queue(), Queue()
                # Create workers
                workers = [
                    Process(
                        target=worker_func,
                        args=(infer_global_opt, in_queue, out_queue, worker_args)
                    )
                    for ii in range(args.cpus)
                ]
                workers.extend([
                    Process(target=worker_func,
                        args=(infer_global_opt, in_queue, out_queue, worker_args, True))
                    for ii in range(args.gpus)
                ])
                # Put the tasks to be done in the queue.
                for ii in range(global_optimizations):
                    new_seed = np.random.randint(1, 1e6)
                    in_queue.put(new_seed)
                # Start the workers
                for worker in workers:
                    worker.start()
            # Collect and process results

            for _ in range(global_optimizations):
                if args.work_queue:
                    result = q.wait().output
                else:
                    result = out_queue.get()
                # Write latest result to file
                # Check that the log-likelihood is not a weird value
                if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                    result = (-np.inf,) + result[1:]
                fid_global.write(
                    "{0}\t{1}\t{2}\n".format(
                        result[0], "\t".join(str(_) for _ in result[1]), result[2]
                    )
                )
                fid_global.flush()
                result = get_bestfit_params(
                    path=args.output_prefix + ".global.InferDM.opts.*",
                    lbounds=args.lbounds,
                    ubounds=args.ubounds,
                    output=args.output_prefix + ".global.InferDM.bestfits",
                    delta=args.delta_ll,
                )
                ### Place holder if we want check convergence for global optimization
                # if result is not None:
                #    args.force_convergence = False
                #    break
            if not args.work_queue:
                # Stop the workers
                for worker in workers:
                    worker.terminate()

            args.p0, _ = get_opts_and_theta(
                args.output_prefix + ".global.InferDM.bestfits"
            )

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
            # args.p0 = bestfits[np.random.randint(len(bestfits)%10)]
        else:
            bestfits = None

        # Worker arguments, leave seed argmument out as it is added in as workers are created
        worker_args = [fs,
                       func,
                       args.p0,
                       args.grids,
                       args.ubounds,
                       args.lbounds,
                       args.constants,
                       args.misid,
                       args.cov_args,
                       args.cov_inbreeding,
                       None,
                       args.maxeval,
                       args.maxtime,
                       bestfits]

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
                raise ValueError('Work Queue password file "{0}" not found.'.format(
                    args.work_queue[1]))

            for ii in range(args.optimizations):
                new_seed = np.random.randint(1, 1e6)
                t = wq.PythonTask(infer_demography, *(worker_args+[new_seed]))
                t.specify_cores(1)
                # If using a custom model, need to include the file from which it comes
                if args.model_file:
                    t.specify_input_file(args.model_file + ".py")
                q.submit(t)
        else:
            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [
                Process(
                    target=worker_func,
                    args=(infer_demography, in_queue, out_queue, worker_args)
                )
                for ii in range(args.cpus)
            ]
            workers.extend([
                Process(target=worker_func,
                    args=(infer_demography, in_queue, out_queue, worker_args, True))
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

        for _ in range(args.optimizations):
            if args.work_queue:
                result = q.wait().output
            else:
                result = out_queue.get()
            num_opts += 1
            # Write latest result to file
            # Check that the log-likelihood is not a weird value
            if result[0] in [np.ma.core.MaskedConstant, np.inf]:
                result = (-np.inf,) + result[1:]

            fid.write(
                "{0}\t{1}\t{2}\n".format(
                    result[0], "\t".join(str(_) for _ in result[1]), result[2]
                )
            )
            fid.flush()
            if (args.check_convergence or args.force_convergence) and num_opts >= (args.check_convergence or args.force_convergence):
                results_file = args.output_prefix + ".InferDM.bestfits"
                result = get_bestfit_params(
                    path=args.output_prefix + ".InferDM.opts.*",
                    lbounds=args.lbounds,
                    ubounds=args.ubounds,
                    output=args.output_prefix + ".InferDM.bestfits",
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
    # TODO: Stop the remaining work_queue workers


def add_infer_dm_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds parser for the "InferDM" command to a subparser collection. This function
    sets up command-line arguments specific to inferring demographic models from
    allele frequency spectra.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "InferDM", help="Infer a demographic models from an allele frequency spectrum."
    )
    add_fs_argument(parser)
    add_inference_argument(parser)
    add_delta_ll_argument(parser)
    add_model_argument(parser)
    add_grids_argument(parser)
    add_misid_argument(parser)
    add_coverage_model_argument(parser)
    add_constant_argument(parser)
    add_bounds_argument(parser)
    parser.add_argument(
        "--global-optimization",
        default=False,
        action="store_true",
        dest="global_optimization",
        help="Use global optimization before doing local optimization. Default: False.",
    )
    add_seed_argument(parser)
    parser.set_defaults(runner=_run_infer_dm)
