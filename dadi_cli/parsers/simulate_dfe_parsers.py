import argparse, pickle
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.SimulateFs import simulate_dfe


def _run_simulate_dfe(args: argparse.Namespace) -> None:
    """
    Simulates allele frequency spectra based on specified distribution of fitness effects (DFE) models.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace from argparse that contains all necessary parameters for the DFE simulation.
        The function expects the following attributes:
        - cache1d : str or None
            Path or URL to the cache file for 1D computation. If provided via URL, the cache is
            downloaded and used for simulation.
        - cache2d : str or None
            Path or URL to the cache file for 2D computation. If provided via URL, the cache is
            downloaded and used for simulation.
        - misid : bool, optional
            Indicates whether misidentification corrections are to be considered.
        - output : str
            The directory path where the simulation results will be saved.
        - p0 : list of float
            Initial parameter values for the DFE simulation.
        - pdf1d : str
            The 1D probability distribution function name for the DFE.
        - pdf2d : str, optional
            The 2D probability distribution function name for the DFE.
        - ratio : float
            Ratio for adjusting the selection parameters, typically used to scale between different
            types of mutations or fitness effects.
        - nomisid : bool
            Flag to not consider misidentification, which is converted internally to `misid`.

    """
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
    make_dir(args.output)
    simulate_dfe(
        p0=args.p0,
        cache1d=cache1d,
        cache2d=cache2d,
        sele_dist=args.pdf1d,
        sele_dist2=args.pdf2d,
        ratio=args.ratio,
        misid=args.misid,
        output=args.output,
    )


def add_simulate_dfe_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a parser for the "SimulateDFE" command to the subparsers collection. This function
    configures command-line arguments for simulating allele frequency spectra based on a
    specified distribution of fitness effects (DFE).

    The setup includes specifying parameters for DFE, the ratio of nonsynonymous to synonymous
    mutations, initial parameters for the simulation, options for misidentification error handling,
    and output directory configuration.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "SimulateDFE", help="Generate frequency spectrum based on a DFE."
    )
    add_dfe_argument(parser)
    parser.add_argument(
        "--ratio",
        type=positive_num,
        dest="ratio",
        required=True,
        help="Ratio for the nonsynonymous mutations to the synonymous mutations.",
    )
    add_p0_argument(parser)
    add_misid_argument(parser)
    add_output_argument(parser)
    parser.set_defaults(runner=_run_simulate_dfe)
