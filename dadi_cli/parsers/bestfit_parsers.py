import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.BestFit import get_bestfit_params


def _run_bestfit(args: argparse.Namespace) -> None:
    """
    Processes a series of optimization files to find and save the best-fit parameters based
    on log-likelihood differences.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object that holds all input arguments necessary for finding the best-fit
        parameters. The expected attributes are:
        - input_prefix (str): Prefix for the input files containing the optimization results.
          This is used to construct the search pattern for the input files.
        - delta_ll (float): The acceptable deviation in log-likelihood from the best log-likelihood
          found. Only parameters with a log-likelihood within this range are considered.
        - lbounds (list of float): Lower bounds for each parameter, used to validate the
          parameters being considered.
        - ubounds (list of float): Upper bounds for each parameter, used to validate the
          parameters being considered.
        - output (str): Path for the output file where the best-fit parameters will be saved.
          This is derived from the input prefix by appending ".bestfits".

    """
    get_bestfit_params(
        path=args.input_prefix + ".opts.*",
        delta=args.delta_ll,
        lbounds=args.lbounds,
        ubounds=args.ubounds,
        output=args.input_prefix + ".bestfits",
    )


def add_bestfit_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a command-line argument parser for the 'BestFit' command to an existing collection
    of subparsers. This setup allows the user to specify inputs for obtaining the best-fit
    parameters from a series of optimization results.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        The subparsers object from an ArgumentParser to which the 'BestFit' command
        subparser will be added. This object manages multiple commands within a larger
        command-line interface.

    """
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
    parser.set_defaults(runner=_run_bestfit)
