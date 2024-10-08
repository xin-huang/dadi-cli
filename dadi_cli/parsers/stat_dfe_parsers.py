import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.Stat import godambe_stat_dfe


def _run_stat_dfe(args: argparse.Namespace) -> None:
    """
    Calculates statistical properties such as Godambe Information Matrix for
    Distribution of Fitness Effects (DFE) based on the given simulation and bootstrap samples.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace from argparse containing all necessary parameters for computing statistics
        on DFE estimates. Expected parameters include:
        - fs : str
            Path to the file containing the frequency spectrum data.
        - bootstrapping_non_dir : str
            Directory containing non-directional bootstrap resamples.
        - bootstrapping_syn_dir : str
            Directory containing directional bootstrap resamples.
        - cache1d : str
            Path to the cache file for 1D computation.
        - cache2d : str
            Path to the cache file for 2D computation.
        - pdf1d : str
            The 1D probability distribution function used for the DFE.
        - pdf2d : str
            The 2D probability distribution function used for the DFE.
        - pdf_file : str
            Name of file with custom probability density function model(s) in it.
        - dfe_popt : str
            Path to the file containing optimized parameter values for the DFE model.
        - constants : list
            List of constant parameters used in the DFE model.
        - logscale : bool
            Flag indicating whether parameters should be considered on a logarithmic scale.
        - output : str
            Directory path where the results will be saved.
        - eps : float
            A small constant for numerical stability in calculations.

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
    # if args.dfe_popt is not None:
    #     if "://" in args.model_file:
    #         model_fi = open("dfe_popt.bestfits","w")
    #         with urllib.request.urlopen(args.model_file) as f:
    #             model_fi.write(f.read().decode('utf-8'))
    #         model_fi.close()
    #         args.model_file = "dfe_popt.bestfits"

    make_dir(args.output)

    godambe_stat_dfe(
        fs=args.fs,
        bootstrap_non_dir=args.bootstrapping_non_dir,
        bootstrap_syn_dir=args.bootstrapping_syn_dir,
        cache1d=args.cache1d,
        cache2d=args.cache2d,
        sele_dist=args.pdf1d,
        sele_dist2=args.pdf2d,
        pdf_file=args.pdf_file,
        dfe_popt=args.dfe_popt,
        fixed_params=args.constants,
        logscale=args.logscale,
        output=args.output,
        eps_l=args.eps,
    )


def add_stat_dfe_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a parser for the "StatDFE" command to the subparsers collection. This function
    configures command-line arguments for performing statistical tests using the Godambe
    Information Matrix on estimates of Distribution of Fitness Effects (DFE).

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This object is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "StatDFE",
        help="Perform statistical tests using Godambe Information Matrix for DFEs.",
    )
    add_fs_argument(parser)
    add_dfe_argument(parser)
    add_output_argument(parser)
    add_constant_argument(parser)
    add_eps_argument(parser)

    parser.add_argument(
        "--dfe-popt",
        type=existed_file,
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

    parser.set_defaults(runner=_run_stat_dfe)
