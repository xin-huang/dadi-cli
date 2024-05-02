import argparse, multiprocessing
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.GenerateCache import *
from dadi_cli.Models import *


def _run_generate_cache(args: argparse.Namespace) -> None:
    """
    Executes the cache generation for demographic models or selection models based on specified parameters.
    This function handles the loading of models from either a local file or a URL, setting up the output directory,
    and initiating the cache generation process with specified options.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object containing all the necessary parameters to configure the cache generation.
        Expected attributes include:
        - model : str
            The name of the model to use, which should be a function defined in `dadi.DFE.DemogSelModels`.
        - model_file : str, optional
            The path or URL to a Python file defining additional models. If provided, the model
            specified in `model` will be loaded from this file.
        - demo_popt : str
            The path or URL to the best fit parameters file.
        - grids : list
            List specifying the size of the grid points for numerical integration.
        - gamma_bounds : tuple
            Bounds for gamma values used in the cache generation.
        - gamma_pts : int
            Number of points for gamma values within the specified bounds.
        - additional_gammas : list, optional
            Additional gamma values to include in the cache generation.
        - output : str
            Directory to store the generated cache files.
        - sample_sizes : list
            List of sample sizes for which to generate the cache.
        - cpus : int
            Number of CPU cores to use for computation.
        - gpus : int
            Number of GPU devices to use for computation, if applicable.
        - dimensionality : int
            The dimensionality of the demographic model.

    """
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
    make_dir(args.output)

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


def add_generate_cache_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a subparser for the 'GenerateCache' command to an existing collection of subparsers.
    This function configures the necessary command-line arguments to generate a selection
    coefficient cache, which is used for inferring the distribution of fitness effects (DFE).

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        The subparsers object from an ArgumentParser to which the 'GenerateCache' command
        subparser will be added. This allows for handling specific arguments dedicated to
        the cache generation process.

    """
    parser = subparsers.add_parser(
        "GenerateCache", help="Generate selection coefficient cache for inferring DFE."
    )

    parser.add_argument(
        "--additional-gammas",
        type=positive_num,
        nargs="+",
        default=[],
        help="Additional positive population-scaled selection coefficients to cache for. Default: [].",
        dest="additional_gammas",
    )

    parser.add_argument(
        "--gamma-bounds",
        type=positive_num,
        nargs=2,
        default=[1e-4, 2000],
        help="Range of population-scaled selection coefficients to cache. Default: [1e-4, 2000].",
        dest="gamma_bounds",
    )

    parser.add_argument(
        "--gamma-pts",
        type=positive_int,
        default=50,
        help="Number of gamma grid points over which to integrate. Default: 50.",
        dest="gamma_pts",
    )

    parser.add_argument(
        "--cpus",
        type=positive_int,
        default=multiprocessing.cpu_count(),
        help="Number of CPUs to use in multiprocessing. Default: All available CPUs.",
    )

    parser.add_argument(
        "--gpus",
        type=nonnegative_int,
        default=0,
        help="Number of GPUs to use in multiprocessing. Default: 0.",
    )

    parser.add_argument(
        "--dimensionality",
        type=positive_int,
        default=1,
        help="Determine whether using demographic model plus selection with the same gamma in both the two populations or not. Default: 1.",
        dest="dimensionality",
    )

    add_sample_sizes_argument(parser)
    add_output_argument(parser)
    add_demo_popt_argument(parser)
    add_grids_argument(parser)
    add_model_argument(parser)
    parser.set_defaults(runner=_run_generate_cache)
