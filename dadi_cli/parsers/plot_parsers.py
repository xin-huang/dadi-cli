import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.Plot import *


def _run_plot(args: argparse.Namespace) -> None:
    """
    Executes plotting functions based on the provided arguments to visualize demographic
    and distribution of fitness effects (DFE) models alongside allele frequency spectra.

    Parameters
    ----------
    args : Namespace
        A namespace from argparse that contains all necessary parameters for plotting.
        The function expects the following attributes:
        - output : str
            The directory path where plots will be saved.
        - fs : str, optional
            Path to the file containing the allele frequency spectrum.
        - fs2 : str, optional
            Path to a second file containing the allele frequency spectrum, used for
            comparative plots.
        - model_file : str, optional
            Path or URL to a Python script containing demographic model definitions.
        - model : str, optional
            The demographic model to use for plotting.
        - demo_popt : str, optional
            Path to the file containing optimized parameters for demographic models.
        - dfe_popt : str, optional
            Path to the file containing optimized parameters for DFE models.
        - pdf1d : str, optional
            The 1D probability density function name for DFE plotting.
        - pdf2 : str, optional
            The 2D probability density function name for DFE plotting.
        - cache1d : str, optional
            Path to a cache file for 1D computation.
        - cache2d : str, optional
            Path to a cache file for 2D computation.
        - vmin : float, optional
            Minimum value for plotting scale.
        - resid_range : tuple, optional
            Range of residuals for plotting.
        - projections : tuple, optional
            Projections for frequency spectrum summarization.
        - nomisid : bool, optional
            Whether misidentification corrections are to be considered.
        - interactive: bool, optional
            Whether displaying the plot in an interactive window.

    """
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

    make_dir(args.output)

    if args.fs is None:
        plot_mut_prop(
            pdf=args.pdf1d,
            dfe_popt=args.dfe_popt,
            output=args.output,
            show=args.interactive,
        )
    elif args.dfe_popt is not None:
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
            show=args.interactive,
        )
    elif args.demo_popt is not None:
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
            show=args.interactive,
        )
    elif args.fs2 is None:
        plot_single_sfs(
            fs=args.fs, 
            projections=args.projections, 
            output=args.output, 
            vmin=args.vmin,
            show=args.interactive,
        )
    else:
        plot_comparison(
            fs=args.fs,
            fs2=args.fs2,
            projections=args.projections,
            output=args.output,
            vmin=args.vmin,
            resid_range=args.resid_range,
            show=args.interactive,
        )


def add_plot_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Add a parser for the "Plot" command to the subparsers collection. This function
    configures command-line arguments for generating plots from frequency spectra and
    model outputs. It supports plotting of 1D, 2D, and comparison plots.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser("Plot", help="Plot 1D/2D/3D frequency spectrum.")
    parser.add_argument(
        "--fs",
        type=existed_file,
        help="Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link.",
    )
    parser.add_argument(
        "--fs2",
        type=existed_file,
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
        type=positive_num,
        default=False,
        required=False,
        help="Ratio for the nonsynonymous mutations to the synonymous mutations.",
    )
    parser.add_argument(
        "--interactive",
        default=False,
        action="store_true",
        required=False,
        help="Display plots in matplotlib window.",
    )
    parser.add_argument(
        "--show",
        default=False,
        action="store_true",
        required=False,
        help="Display plots in matplotlib window.",
    )
    parser.set_defaults(runner=_run_plot)
