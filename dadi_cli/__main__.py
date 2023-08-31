import argparse, glob, os.path, sys, signal, warnings
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
def _worker_func(func, in_queue, out_queue, args, use_gpu=False):
    dadi.cuda_enabled(use_gpu)
    while True:
        new_seed = in_queue.get()
        np.random.seed(new_seed)
        results = func(*args)
        out_queue.put(results)


def run_generate_fs(args):
    if args.mask_shared:
        mask = "shared"
    elif args.mask:
        mask = "singletons"
    else:
        mask = ""
    _make_dir(args.output)
    generate_fs(
        vcf=args.vcf,
        output=args.output,
        bootstrap=args.bootstrap,
        chunk_size=args.chunk_size,
        seed=args.seed,
        pop_ids=args.pop_ids,
        pop_info=args.pop_info,
        projections=args.projections,
        polarized=args.polarized,
        marginalize_pops=args.marginalize_pops,
        subsample=args.subsample,
        masking=mask,
    )


def run_generate_cache(args):
    if args.model_file is None and args.model not in [m[0] for m in getmembers(DFE.DemogSelModels, isfunction)]:
        raise ValueError(f"{args.model} is not in dadi.DFE.DemogSelModels, did you mean to include _sel or _single_sel in the model name or specify a --model-file?")

    if args.model_file is not None:
        if "://" in args.model_file:
            import urllib.request
            model_fi = open("dadi_models.py","w")
            with urllib.request.urlopen(args.model_file) as f:
                model_fi.write(f.read().decode('utf-8'))
            model_fi.close()
            args.model_file = "dadi_models"

    if "://" in args.demo_popt:
        import urllib.request
        popt_fi = open("demo-popt.bestfits","w")
        with urllib.request.urlopen(args.demo_popt) as f:
            popt_fi.write(f.read().decode('utf-8'))
        popt_fi.close()
        args.demo_popt = "demo-popt.bestfits"

    func, _ = get_model(args.model, args.model_file)
    _make_dir(args.output)
    generate_cache(
        func=func,
        grids=args.grids,
        popt=args.demo_popt,
        gamma_bounds=args.gamma_bounds,
        gamma_pts=args.gamma_pts,
        additional_gammas=args.additional_gammas,
        output=args.output,
        sample_sizes=args.sample_sizes,
        cpus=args.cpus,
        gpus=args.gpus,
        dimensionality=args.dimensionality,
    )


def run_simulate_dm(args):
    from dadi_cli.SimulateFs import simulate_demography
    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not args.nomisid
    if args.model_file is not None:
        if "://" in args.model_file:
            import urllib.request
            model_fi = open("dadi_models.py","w")
            with urllib.request.urlopen(args.model_file) as f:
                model_fi.write(f.read().decode('utf-8'))
            model_fi.close()
            args.model_file = "dadi_models"
    _make_dir(args.output)
    simulate_demography(
        args.model,
        args.model_file,
        args.p0,
        args.sample_sizes,
        args.grids,
        args.misid,
        args.output,
        args.inference_file,
    )


def run_simulate_dfe(args):
    from dadi_cli.SimulateFs import simulate_dfe

    import pickle

    if args.cache1d != None:
        if "://" in args.cache1d:
            from urllib.request import urlopen
            cache1d = pickle.load(urlopen(args.cache1d))
        else:
            cache1d = pickle.load(open(args.cache1d, "rb"))
    else:
        cache1d = args.cache1d

    if args.cache2d != None:
        if "://" in args.cache2d:
            from urllib.request import urlopen
            cache2d = pickle.load(urlopen(args.cache2d))
        else:
            cache2d = pickle.load(open(args.cache2d, "rb"))
    else:
        cache2d = args.cache2d

    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not args.nomisid
    _make_dir(args.output)
    simulate_dfe(
        args.p0,
        cache1d,
        cache2d,
        args.pdf1d,
        args.pdf2d,
        args.ratio,
        args.misid,
        args.output,
    )


def run_simulate_demes(args):
    from dadi_cli.SimulateFs import simulate_demes
    if "://" in args.demes_file:
        import urllib.request
        model_fi = open("demes_file.yml","w")
        with urllib.request.urlopen(args.demes_file) as f:
            model_fi.write(f.read().decode('utf-8'))
        model_fi.close()
        args.demes_file = "demes_file.yml"
    _make_dir(args.output)
    simulate_demes(args.demes_file, args.sample_sizes, args.grids, args.pop_ids, args.output)


def run_infer_dm(args):

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

    _make_dir(args.output_prefix)

    # Because basic standard neutral models do not need to optimized
    # we can calculate the log-likelihood and theta
    if args.model in ['snm_1d', 'snm_2d'] and args.p0 == -1 and args.lbounds == None and args.ubounds == None:
        fid = open(args.output_prefix + ".InferDM.bestfits", "w")
        # Write command line to results file
        import sys
        fid.write("# {0}\n".format(" ".join(sys.argv)))

        # Extract model function and parameter names, from custom model_file if necessary
        func, param_names = get_model(args.model, args.model_file)
        if args.grids is None:
            args.grids = pts_l_func(fs.sample_sizes)

        fid.write("# Log(likelihood)\t" + "\t".join(param_names) + "\ttheta\n")
        from sys import exit
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
        args.constants = _check_params(
            args.constants, args.model, "--constant", args.misid
        )
    if not args.model_file and args.lbounds != -1:
        args.lbounds = _check_params(args.lbounds, args.model, "--lbounds", args.misid)
    if not args.model_file and args.ubounds != -1:
        args.ubounds = _check_params(args.ubounds, args.model, "--ubounds", args.misid)

    if args.p0 == -1:
        args.p0 = _calc_p0_from_bounds(args.lbounds, args.ubounds)

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
    import sys

    fid.write("# {0}\n".format(" ".join(sys.argv)))

    # Write column headers
    if not args.nomisid:
        param_names += ["misid"]
    fid.write("# Log(likelihood)\t" + "\t".join(param_names) + "\ttheta\n")

    # Check if demographic function uses inbreeding, need to be done before wrapping
    import inspect

    if "from_phi_inbreeding" in inspect.getsource(func):
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
            import nlopt

            if args.seed == None:
                global_algorithm = nlopt.GN_MLSL
            else:
                global_algorithm = nlopt.GN_MLSL_LDS
            if args.work_queue:
                import work_queue as wq

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
                from multiprocessing import Process, Queue

                worker_args = (
                    fs,
                    func,
                    args.p0,
                    args.grids,
                    args.ubounds,
                    args.lbounds,
                    args.constants,
                    args.misid,
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
                        target=_worker_func,
                        args=(infer_global_opt, in_queue, out_queue, worker_args)
                    )
                    for ii in range(args.cpus)
                ]
                workers.extend([
                    Process(target=_worker_func,
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
            from dadi_cli.utilities import get_opts_and_theta
            import os

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
            bestfits = _top_opts(args.bestfit_p0)
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
                       None,
                       args.maxeval,
                       args.maxtime,
                       bestfits]

        if args.work_queue:
            import work_queue as wq

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
            from multiprocessing import Process, Queue

            # Queues to manage input and output
            in_queue, out_queue = Queue(), Queue()
            # Create workers
            workers = [
                Process(
                    target=_worker_func,
                    args=(infer_demography, in_queue, out_queue, worker_args)
                )
                for ii in range(args.cpus)
            ]
            workers.extend([
                Process(target=_worker_func,
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
        from dadi_cli.BestFit import get_bestfit_params

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


def run_infer_dfe(args):
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

    _make_dir(args.output_prefix)

    # # Things need to be updated for these to work
    if None not in [args.pdf1d, args.pdf2d]:
        pass
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf != None:
                if not args.pdf_file and args.constants != -1:
                    args.constants, _ = _check_pdf_params(
                        args.constants, pdf, "--constant", args.misid
                    )
                if not args.pdf_file and args.lbounds != -1:
                    args.lbounds, _ = _check_pdf_params(
                        args.lbounds, pdf, "--lbounds", args.misid
                    )
                if not args.pdf_file and args.ubounds != -1:
                    args.ubounds, _ = _check_pdf_params(
                        args.ubounds, pdf, "--ubounds", args.misid
                    )

    if args.p0 == -1:
        args.p0 = _calc_p0_from_bounds(args.lbounds, args.ubounds)

    from dadi_cli.utilities import get_opts_and_theta

    if "://" in args.demo_popt:
        import urllib.request
        popt_fi = open("demo-popt.bestfits","w")
        with urllib.request.urlopen(args.demo_popt) as f:
            popt_fi.write(f.read().decode('utf-8'))
        popt_fi.close()
        args.demo_popt = "demo-popt.bestfits"

    _, theta = get_opts_and_theta(args.demo_popt)
    theta *= args.ratio

    import pickle


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

    from dadi_cli.InferDFE import infer_dfe

    existing_files = glob.glob(args.output_prefix + ".InferDFE.opts.*")
    try:
        newest_file_num = max([int(ele.split(".")[-1]) for ele in existing_files]) + 1
    except:
        newest_file_num = 0
    results_file = args.output_prefix + ".InferDFE.opts.{0}".format(newest_file_num)
    fid = open(results_file, "a")
    # Write command line to results file
    import sys

    fid.write("# {0}\n".format(" ".join(sys.argv)))

    # Write column headers
    if args.mix_pdf != None:
        param_names = get_dadi_pdf_params(args.mix_pdf)
    else:
        for pdf in [args.pdf1d, args.pdf2d]:
            if pdf != None:
                _, param_names = _check_pdf_params(args.p0, pdf, "", args.misid)

    param_names = "# Log(likelihood)\t" + "\t".join(param_names)
    if not args.nomisid:
        param_names += "\tmisid"
    fid.write(param_names + "\ttheta\n")

    # Randomize or set seed for starting parameter values
    if args.seed == None:
        import time, os

        ts = time.time()
        args.seed = int(time.time()) + int(os.getpid())
    import random

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
            bestfits = _top_opts(args.bestfit_p0)
        else:
            bestfits = None

        if args.work_queue:
            import work_queue as wq

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
            from multiprocessing import Process, Queue

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
                    target=_worker_func,
                    args=(infer_dfe, in_queue, out_queue, worker_args)
                )
                for ii in range(args.cpus)
            ]
            workers.extend([
                Process(target=_worker_func,
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
        from dadi_cli.BestFit import get_bestfit_params

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

def run_bestfit(args):
    from dadi_cli.BestFit import get_bestfit_params

    get_bestfit_params(
        path=args.input_prefix + ".opts.*",
        delta=args.delta_ll,
        lbounds=args.lbounds,
        ubounds=args.ubounds,
        output=args.input_prefix + ".bestfits",
    )


def run_stat_demography(args):
    from dadi_cli.Stat import godambe_stat_demograpy

    # # Code kept just in case user requests functionality if the future
    # if args.fs is not None:
    #     if "://" in args.fs:
    #         import urllib.request
    #         sfs_fi = open("sfs.fs","w")
    #         with urllib.request.urlopen(args.fs) as f:
    #             sfs_fi.write(f.read().decode('utf-8'))
    #         sfs_fi.close()
    #         args.fs ="sfs.fs"
    # if args.model_file is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("dadi_models.py","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "dadi_models"
    # if args.demo_popt is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("demo_popt.bestfits","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "demo_popt.bestfits"

    # Extract model function, from custom model_file if necessary
    func, _ = get_model(args.model, args.model_file)

    _make_dir(args.output)

    godambe_stat_demograpy(
        fs=args.fs,
        func=func,
        bootstrap_dir=args.bootstrapping_dir,
        grids=args.grids,
        nomisid=args.nomisid,
        demo_popt=args.demo_popt,
        fixed_params=args.constants,
        logscale=args.logscale,
        output=args.output,
        eps_l=args.eps,
    )


def run_stat_dfe(args):
    from dadi_cli.Stat import godambe_stat_dfe

    # # Code kept just in case user requests functionality if the future
    # if args.fs is not None:
    #     if "://" in args.fs:
    #         import urllib.request
    #         sfs_fi = open("sfs.fs","w")
    #         with urllib.request.urlopen(args.fs) as f:
    #             sfs_fi.write(f.read().decode('utf-8'))
    #         sfs_fi.close()
    #         args.fs ="sfs.fs"
    # if args.dfe_popt is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("dfe_popt.bestfits","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "dfe_popt.bestfits"

    _make_dir(args.output)

    godambe_stat_dfe(
        fs=args.fs,
        bootstrap_non_dir=args.bootstrapping_non_dir,
        bootstrap_syn_dir=args.bootstrapping_syn_dir,
        cache1d=args.cache1d,
        cache2d=args.cache2d,
        sele_dist=args.pdf1d,
        sele_dist2=args.pdf2d,
        nomisid=args.nomisid,
        dfe_popt=args.dfe_popt,
        fixed_params=args.constants,
        logscale=args.logscale,
        output=args.output,
        eps_l=args.eps,
    )


def run_plot(args):
    from dadi_cli.Plot import (
        plot_comparison,
        plot_fitted_demography,
        plot_fitted_dfe,
        plot_single_sfs,
        plot_mut_prop,
    )

    # # Code kept just in case user requests functionality if the future
    # if args.fs is not None:
    #     if "://" in args.fs:
    #         import urllib.request
    #         sfs_fi = open("sfs.fs","w")
    #         with urllib.request.urlopen(args.fs) as f:
    #             sfs_fi.write(f.read().decode('utf-8'))
    #         sfs_fi.close()
    #         args.fs ="sfs.fs"
    # if args.model_file is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("dadi_models.py","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "dadi_models"
    # if args.demo_popt is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("demo_popt.bestfits","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "demo_popt.bestfits"
    # if args.dfe_popt is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("dfe_popt.bestfits","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "dfe_popt.bestfits"

    _make_dir(args.output)

    if args.fs == None:
        plot_mut_prop(
            pdf=args.pdf1d,
            dfe_popt=args.dfe_popt,
            output=args.output,
        )
    elif args.dfe_popt != None:
        plot_fitted_dfe(
            fs=args.fs,
            cache1d=args.cache1d,
            cache2d=args.cache2d,
            pdf=args.pdf1d,
            pdf2=args.pdf2d,
            nomisid=args.nomisid,
            sele_popt=args.dfe_popt,
            vmin=args.vmin,
            resid_range=args.resid_range,
            projections=args.projections,
            output=args.output,
        )
    elif args.demo_popt != None:
        if args.model is None:
            raise ValueError("--model is missing")
        func, _ = get_model(args.model, args.model_file)
        plot_fitted_demography(
            fs=args.fs,
            func=func,
            popt=args.demo_popt,
            vmin=args.vmin,
            projections=args.projections,
            nomisid=args.nomisid,
            resid_range=args.resid_range,
            output=args.output,
        )
    elif args.fs2 == None:
        plot_single_sfs(
            fs=args.fs, projections=args.projections, output=args.output, vmin=args.vmin
        )
    else:
        plot_comparison(
            fs=args.fs,
            fs2=args.fs2,
            projections=args.projections,
            output=args.output,
            vmin=args.vmin,
            resid_range=args.resid_range,
        )


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
    parser.add_argument(
        "--output", type=str, required=True, help="Name of the output file."
    )

def add_bounds_argument(parser):
    # Check that the model is not a standard neutral model
    if 'snm_1d' not in sys.argv and 'snm_2d' not in sys.argv:
        boundary_req = True
    else:
        if '--nomisid' in sys.argv:
            boundary_req = False
        else:
            boundary_req = True
    parser.add_argument(
        "--lbounds",
        type=float,
        nargs="+",
        required=boundary_req,
        help="Lower bounds of the optimized parameters.",
    )
    parser.add_argument(
        "--ubounds",
        type=float,
        nargs="+",
        required=boundary_req,
        help="Upper bounds of the optimized parameters.",
    )


def add_demo_popt_argument(parser):
    # Check that the model is not a standard neutral model
    bestfit_req = False
    if 'equil' not in sys.argv:
        bestfit_req = True
    parser.add_argument(
        "--demo-popt",
        type=str,
        required=bestfit_req,
        help="File containing the bestfit parameters for the demographic model.",
        dest="demo_popt",
    )


def add_grids_argument(parser):
    parser.add_argument(
        "--grids",
        type=_check_positive_int,
        nargs=3,
        help="Sizes of grids. Default is based on sample size.",
    )


def add_misid_argument(parser):
    # Note that the code previously had a --misid function that did the opposite, but this ia more sensible default.
    parser.add_argument(
        "--nomisid",
        default=False,
        action="store_true",
        help="Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized.",
    )


def add_model_argument(parser):
    # Because most of the functions for Plot
    # do not require a model, we make it
    # conditionally required.
    req_model_arg = True
    if 'Plot' in sys.argv:
        req_model_arg = False
    parser.add_argument(
        "--model",
        type=str,
        required=req_model_arg,
        help="Name of the demographic model. To check available demographic models, please use `dadi-cli Model`.",
    )
    parser.add_argument(
        "--model-file",
        type=str,
        required=False,
        dest="model_file",
        help="Name of python module file (not including .py) that contains custom models to use. Can be an HTML link. Default: None.",
    )


def add_fs_argument(parser):
    parser.add_argument(
        "--fs",
        type=str,
        required=True,
        help="Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link.",
    )


def add_seed_argument(parser):
    parser.add_argument("--seed", type=_check_positive_int, help="Random seed.")


def add_constant_argument(parser):
    parser.add_argument(
        "--constants",
        default=-1,
        type=float,
        nargs="+",
        help="Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None.",
    )


def add_delta_ll_argument(parser):
    parser.add_argument(
        "--delta-ll",
        type=_check_positive_num,
        required=False,
        dest="delta_ll",
        default=0.0001,
        help="When using --check-convergence argument in InferDM or InferDFE modules or the BestFits module, set the max percentage difference for log-likliehoods compared to the best optimization log-likliehood to be consider convergent (with 1 being 100%% difference to the best optimization's log-likelihood). Default: 0.0001.",
    )


def add_sample_sizes_argument(parser):
    parser.add_argument(
        "--sample-sizes",
        type=_check_positive_int,
        nargs="+",
        required=True,
        help="Sample sizes of populations.",
        dest="sample_sizes",
    )
def add_eps_argument(parser):
    parser.add_argument(
        "--eps",
        default=[0.1, 0.01, 0.001],
        type=_check_nonnegative_float,
        nargs="+",
        required=False,
        help="Step sizes to try for Godambe analysis. Default: [0.1, 0.01, 0.001]",
    )

def add_popt_argument(parser):
    parser.add_argument(
        "--demo-popt",
        type=str,
        dest="demo_popt",
        help="File containing the bestfit demographic parameters, generated by `dadi-cli BestFit`.",
    )
    parser.add_argument(
        "--dfe-popt",
        type=str,
        dest="dfe_popt",
        help="File containing the bestfit DFE parameters, generated by `dadi-cli BestFit`.",
    )


def add_dfe_argument(parser):
    parser.add_argument(
        "--cache1d",
        type=str,
        help="File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`.",
    )
    parser.add_argument(
        "--cache2d",
        type=str,
        help="File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`.",
    )
    parser.add_argument(
        "--pdf1d",
        type=str,
        help="1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`.",
    )
    parser.add_argument(
        "--pdf2d",
        type=str,
        help="2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`.",
    )


# Currently this command is only needed for param_names.
def add_mix_pdf_argument(parser):
    parser.add_argument(
        "--mix-pdf",
        dest="mix_pdf",
        type=str,
        default=None,
        help="If you are using a model that is a mixture of probability density function for the joint DFE inference pass in the model name. To check available probability density functions, please use `dadi-cli Pdf`.",
    )


def add_inference_argument(parser):
    parser.add_argument(
        "--p0",
        default=-1,
        type=float,
        nargs="+",
        required=False,
        help="Initial parameter values for inference.",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        required=True,
        dest="output_prefix",
        help="Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).",
    )
    parser.add_argument(
        "--optimizations",
        default=100,
        type=_check_positive_int,
        help="Total number of optimizations to run. Default: 100.",
    )
    parser.add_argument(
        "--check-convergence",
        default=0,
        type=_check_positive_int,
        dest="check_convergence",
        help="Start checking for convergence after a chosen number of optimizations. Stop optimization runs when convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default.",
    )
    parser.add_argument(
        "--force-convergence",
        default=0,
        type=_check_positive_int,
        dest="force_convergence",
        help="Start checking for convergence after a chosen number of optimizations. Only stop optimization once convergence criteria is reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default.",
    )
    parser.add_argument(
        "--work-queue",
        nargs=2,
        default=[],
        action="store",
        dest="work_queue",
        help="Enable Work Queue. Additional arguments are the WorkQueue project name, the name of the password file.",
    )
    parser.add_argument(
        "--port",
        default=9123,
        type=_check_positive_int,
        dest="port",
        help="Choose a specific port for Work Queue communication. Default 9123.",
    )
    parser.add_argument(
        "--debug-wq",
        default=False,
        action="store_true",
        dest="debug_wq",
        help='Store debug information from WorkQueue to a file called "debug.log". Default: False.',
    )
    parser.add_argument(
        "--maxeval",
        type=_check_positive_int,
        default=False,
        help="Max number of parameter set evaluations tried for optimizing demography. Default: Number of parameters multiplied by 100.",
    )
    parser.add_argument(
        "--maxtime",
        type=_check_positive_int,
        default=np.inf,
        help="Max amount of time for optimizing demography. Default: infinite.",
    )
    parser.add_argument(
        "--cpus",
        type=_check_nonnegative_int,
        default=multiprocessing.cpu_count(),
        help="Number of CPUs to use in multiprocessing. Default: All available CPUs.",
    )
    parser.add_argument(
        "--gpus",
        type=_check_nonnegative_int,
        default=0,
        help="Number of GPUs to use in multiprocessing. Default: 0.",
    )
    parser.add_argument(
        "--bestfit-p0-file", 
        type=str, 
        dest="bestfit_p0", 
        help="Pass in a .bestfit or .opt.<N> file name to cycle --p0 between up to the top 10 best fits for each optimization."
    )

def add_p0_argument(parser):
    p0_req = False
    if 'snm_1d' not in sys.argv and 'snm_2d' not in sys.argv:
        p0_req = True
    else:
        if '--nomisid' not in sys.argv:
            p0_req = True

    parser.add_argument(
        "--p0",
        type=float,
        nargs="+",
        required=p0_req,
        help="Parameters for simulated demography or dfe.",
    )


def dadi_cli_parser():
    top_parser = argparse.ArgumentParser()
    subparsers = top_parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    parser = subparsers.add_parser(
        "GenerateFs", help="Generate frequency spectrum from VCF files."
    )
    parser.add_argument(
        "--polarized",
        default=False,
        action="store_true",
        help="Determine whether the resulting frequency spectrum is polarized or not; Default: False.",
    )
    parser.add_argument(
        "--pop-ids",
        type=str,
        nargs="+",
        required=True,
        help="Population names for the samples.",
        dest="pop_ids",
    )
    parser.add_argument(
        "--pop-info",
        type=str,
        required=True,
        help="Name of the file containing the population name of each sample.",
        dest="pop_info",
    )
    parser.add_argument(
        "--projections",
        type=_check_positive_int,
        nargs="+",
        required=True,
        help="Sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data.",
    )
    parser.add_argument(
        "--vcf",
        type=str,
        required=True,
        help="Name of the VCF file for generating frequency spectrum.",
    )
    parser.add_argument(
        "--bootstrap", type=_check_positive_int, help="Times to perform bootstrapping."
    )
    parser.add_argument(
        "--chunk-size",
        type=_check_positive_int,
        help="Chunk size to divide the genomes for bootstrapping.",
        dest="chunk_size",
    )
    parser.add_argument(
        "--subsample",
        default=False,
        action="store_true",
        dest="subsample",
        help="Subsample from the VCF when generating the fs using the given pop-ids and subsample calls based on the projections passed in. Default: None.",
    )
    parser.add_argument(
        "--mask-singletons",
        default=False,
        action="store_true",
        dest="mask",
        help="Mask the singletons that are exclusive to each population. Default: None.",
    )
    parser.add_argument(
        "--mask-shared-singletons",
        default=False,
        action="store_true",
        dest="mask_shared",
        help="Mask the singletons that are exclusive to each population and shared between populations. Default: None.",
    )
    parser.add_argument(
        "--marginalize-pop-ids",
        type=str,
        nargs="+",
        help="Population names you want to marginalize (remove) from the full fs. Default: None.",
        dest="marginalize_pops",
    )
    add_output_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=run_generate_fs)

    parser = subparsers.add_parser(
        "GenerateCache", help="Generate selection coefficient cache for inferring DFE."
    )
    parser.add_argument(
        "--additional-gammas",
        type=_check_positive_num,
        nargs="+",
        default=[],
        help="Additional positive population-scaled selection coefficients to cache for. Default: [].",
        dest="additional_gammas",
    )
    parser.add_argument(
        "--gamma-bounds",
        type=_check_positive_num,
        nargs=2,
        default=[1e-4, 2000],
        help="Range of population-scaled selection coefficients to cache. Default: [1e-4, 2000].",
        dest="gamma_bounds",
    )
    parser.add_argument(
        "--gamma-pts",
        type=_check_positive_int,
        default=50,
        help="Number of gamma grid points over which to integrate. Default: 50.",
        dest="gamma_pts",
    )
    parser.add_argument(
        "--cpus",
        type=_check_nonnegative_int,
        default=multiprocessing.cpu_count(),
        help="Number of CPUs to use in multiprocessing. Default: All available CPUs.",
    )
    parser.add_argument(
        "--gpus",
        type=_check_nonnegative_int,
        default=0,
        help="Number of GPUs to use in multiprocessing. Default: 0.",
    )
    parser.add_argument(
        "--dimensionality",
        type=int,
        default=1,
        help="Determine whether using demographic model plus selection with the same gamma in both the two populations or not. Default: 1.",
        dest="dimensionality",
    )
    add_sample_sizes_argument(parser)
    add_output_argument(parser)
    add_demo_popt_argument(parser)
    add_grids_argument(parser)
    add_model_argument(parser)
    parser.set_defaults(runner=run_generate_cache)

    parser = subparsers.add_parser(
        "SimulateDM", help="Generate frequency spectrum based on a demographic history."
    )
    add_model_argument(parser)
    add_sample_sizes_argument(parser)
    add_p0_argument(parser)
    add_misid_argument(parser)
    add_grids_argument(parser)
    parser.add_argument(
        "--inference-file",
        dest="inference_file",
        default=False,
        action="store_true",
        help='Make an output file like you would get for running InferDM to pass into GenerateCache to make caches with your simulated demographic model. Will be the same name and path as output + ".SimulateFs.pseudofit"; Default: False.',
    )
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_dm)

    parser = subparsers.add_parser(
        "SimulateDFE", help="Generate frequency spectrum based on a DFE."
    )
    add_dfe_argument(parser)
    parser.add_argument(
        "--ratio",
        type=float,
        dest="ratio",
        required=True,
        help="Ratio for the nonsynonymous mutations to the synonymous mutations.",
    )
    add_p0_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_dfe)

    parser = subparsers.add_parser(
        "SimulateDemes", help="Generate frequency spectrum based on a Demes .yml file."
    )
    parser.add_argument(
        "--demes-file",
        type=str,
        required=True,
        dest="demes_file",
        help="Name of Demes .yml file that contains model to simulate.",
    )
    parser.add_argument(
        "--pop-ids",
        default=True,
        type=str,
        nargs="+",
        required=False,
        help="Population names for the samples, required for Demes.",
        dest="pop_ids",
    )
    add_sample_sizes_argument(parser)
    add_grids_argument(parser)
    add_output_argument(parser)
    parser.set_defaults(runner=run_simulate_demes)

    parser = subparsers.add_parser(
        "InferDM", help="Infer a demographic models from an allele frequency spectrum."
    )
    add_fs_argument(parser)
    add_inference_argument(parser)
    add_delta_ll_argument(parser)
    add_model_argument(parser)
    add_grids_argument(parser)
    add_misid_argument(parser)
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
    parser.set_defaults(runner=run_infer_dm)

    parser = subparsers.add_parser(
        "InferDFE",
        help="Infer distribution of fitness effects from frequency spectrum.",
    )
    add_fs_argument(parser)
    parser.add_argument(
        "--demo-popt",
        type=str,
        dest="demo_popt",
        help="File contains the bestfit parameters for the demographic model.",
    )
    add_dfe_argument(parser)
    add_mix_pdf_argument(parser)
    parser.add_argument(
        "--ratio",
        type=float,
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
    add_constant_argument(parser)
    add_bounds_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=run_infer_dfe)

    parser = subparsers.add_parser("Plot", help="Plot 1D/2D frequency spectrum.")
    parser.add_argument(
        "--fs",
        type=str,
        help="Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link.",
    )
    parser.add_argument(
        "--fs2",
        type=str,
        help="Name of the second frequency spectrum for comparison, generated by `dadi-cli GenerateFs`.",
    )
    add_popt_argument(parser)
    add_model_argument(parser)
    add_dfe_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    parser.add_argument(
        "--projections", type=int, nargs="+", help="Sample sizes after projection."
    )
    parser.add_argument(
        "--resid-range",
        type=float,
        dest="resid_range",
        help="Ranges of the residual plots.",
    )
    parser.add_argument(
        "--vmin",
        type=float,
        default=0.1,
        help="Minimum value to be plotted in the frequency spectrum, default: 0.1.",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=False,
        required=False,
        help="Ratio for the nonsynonymous mutations to the synonymous mutations.",
    )
    parser.set_defaults(runner=run_plot)

    parser = subparsers.add_parser(
        "StatDM",
        help="Perform statistical tests using Godambe Information Matrix for demographic models.",
    )
    add_fs_argument(parser)
    add_model_argument(parser)
    add_grids_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    add_constant_argument(parser)
    add_eps_argument(parser)
    parser.add_argument(
        "--demo-popt",
        type=str,
        dest="demo_popt",
        help="File contains the bestfit demographic parameters, generated by `dadi-cli BestFit`.",
    )
    parser.add_argument(
        "--bootstrapping-dir",
        type=str,
        required=True,
        help="Directory containing boostrapping spectra.",
        dest="bootstrapping_dir",
    )
    parser.add_argument(
        "--logscale",
        default=False,
        action="store_true",
        help="Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False.",
    )

    parser.set_defaults(runner=run_stat_demography)

    parser = subparsers.add_parser(
        "StatDFE",
        help="Perform statistical tests using Godambe Information Matrix for DFEs.",
    )
    add_fs_argument(parser)
    add_dfe_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    add_constant_argument(parser)
    add_eps_argument(parser)
    parser.add_argument(
        "--dfe-popt",
        type=str,
        dest="dfe_popt",
        help="File containing the bestfit DFE parameters, generated by `dadi-cli BestFit`.",
    )
    parser.add_argument(
        "--bootstrapping-nonsynonymous-dir",
        type=str,
        required=True,
        help="Directory containing boostrapping spectra.",
        dest="bootstrapping_non_dir",
    )
    parser.add_argument(
        "--bootstrapping-synonymous-dir",
        type=str,
        required=True,
        help="Directory containing boostrapping spectra, required to adjust nonsynonymous theta for differences in synonymous theta.",
        dest="bootstrapping_syn_dir",
    )
    parser.add_argument(
        "--logscale",
        default=False,
        action="store_true",
        help="Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False.",
    )
    parser.set_defaults(runner=run_stat_dfe)

    parser = subparsers.add_parser("BestFit", help="Obtain the best fit parameters.")
    parser.add_argument(
        "--input-prefix",
        type=str,
        required=True,
        dest="input_prefix",
        help='Prefix for input files, which is named <input-prefix ending with ".InferDM">.opts.<N> or <input-prefix ending with "InferDFE">.opts.<N>, containing the inferred demographic or DFE parameters.',
    )
    parser.add_argument(
        "--lbounds",
        type=float,
        nargs="+",
        required=False,
        help="Lower bounds of the optimized parameters.",
    )
    parser.add_argument(
        "--ubounds",
        type=float,
        nargs="+",
        required=False,
        help="Upper bounds of the optimized parameters.",
    )
    add_delta_ll_argument(parser)
    parser.set_defaults(runner=run_bestfit)

    parser = subparsers.add_parser(
        "Model", help="Display available demographic models."
    )
    parser.add_argument(
        "--names",
        type=str,
        nargs="?",
        default=None,
        required=True,
        help="Display the details of a given model for demographic inference.",
    )
    parser.set_defaults(runner=run_model)

    parser = subparsers.add_parser(
        "Pdf",
        help="Display available probability density functions for distribution of fitness effects.",
    )
    parser.add_argument(
        "--names",
        type=str,
        nargs="?",
        default=None,
        required=True,
        help="Display the details of a given probability density distribution for DFE inference.",
    )
    parser.set_defaults(runner=run_pdf)

    return top_parser


# helper functions for reading, parsing, and validating parameters from command line or files
def _check_params(params, model, option, misid):
    input_params_len = len(params)
    _, model_params_len = get_model(model, None)
    model_params_len = len(model_params_len)
    if misid:
        input_params_len = input_params_len - 1
    if input_params_len != model_params_len:
        raise Exception(
            "\nFound "
            + str(input_params_len)
            + " demographic parameters from the option "
            + option
            + "; however, "
            + str(model_params_len)
            + " demographic parameters are required from the "
            + model
            + " model"
            + "\nYou might be using the wrong model or need to add --nomisid if you did not use ancestral allele information to polarize the fs."
        )
    return params


def _check_pdf_params(params, pdf, option, misid):
    input_params_len = len(params)
    if misid:
        input_params_len = input_params_len - 1
    if pdf == "biv_lognormal" or pdf == "biv_ind_gamma":
        if input_params_len in [2, 3]:
            mod = "_sym"
        else:
            mod = "_asym"
        pdf = pdf.replace("biv", "biv" + mod)
    model_params_len = len(get_dadi_pdf_params(pdf))
    param_names = get_dadi_pdf_params(pdf)
    if input_params_len != model_params_len:
        raise Exception(
            "Found "
            + str(input_params_len)
            + " pdf parameters from the option "
            + option
            + "; however, "
            + str(model_params_len)
            + " pdf parameters are required from the "
            + pdf
            + " pdf"
        )
    return params, param_names


def _check_positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "only accepts postive integers; %s is an invalid value" % value
        )
    return ivalue

def _check_nonnegative_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            "only accepts nonnegative integers; %s is an invalid value" % value
        )
    return ivalue


def _check_positive_num(value):
    fvalue = float(value)
    if fvalue <= 0:
        raise argparse.ArgumentTypeError(
            "only accepts postive numbers; %s is an invalid value" % value
        )
    return fvalue

def _check_nonnegative_float(value):
    # for value in values:
    fvalue = float(value)
    if fvalue < 0:
        raise argparse.ArgumentTypeError(
            "only accepts postive numbers; %s is an invalid value" % value
        )
    return fvalue

def _calc_p0_from_bounds(lb, ub):
    p0 = []
    for l, u in zip(lb, ub):
        if l == 0:
            p0.append((l + u) / 2)
        elif l*u > 0:
            p0.append(np.sqrt(l * u))
        else:
            p0.append((l+u) / 2)

    return p0


def _make_dir(path):
    parent_dir = os.path.dirname(path)
    if parent_dir != '':
        os.makedirs(parent_dir, exist_ok=True)


def _top_opts(filename):
    """
    Description:
        Obtains optimized parameters and theta.

    Arguments:
        filename str: Name of the file.

    Returns:
        opts list: Optimized parameters.
        theta float: Population-scaled mutation rate.
    """
    fid = open(filename, 'r')
    for line in fid.readlines():
        if line.startswith('# Log'):
            # Reset opts variable to avoid repeating entries.
            opts = []
            continue
        elif line.startswith('#'):
            continue
        else:
            try:
                opts.append([float(_) for _ in line.rstrip().split("\t")])
            except ValueError:
                pass
    fid.close()

    try:
        # Sort entries by log-likelihood
        opts = np.array(sorted(opts, reverse=True))
        # Remove log-likelihood and theta
        opts = [opt[1:-1] for opt in opts]
    except UnboundLocalError: 
        raise ValueError(f"Fits not found in file {filename}.")

    return opts


# Main function
def main(arg_list=None):
    set_sigpipe_handler()
    parser = dadi_cli_parser()
    args = parser.parse_args(arg_list)
    args.runner(args)
