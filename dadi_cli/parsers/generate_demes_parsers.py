import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.GenerateDemes import generate_demes_file


def _run_generate_demes_file(args: argparse.Namespace) -> None:
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
    generate_demes_file(
        model = args.model,
        model_file = args.model_file,
        demo_popt = args.demo_popt, 
        Na = args.Na, 
        generation_time = args.generation_time,
        pop_num = args.pop_num, 
        output = args.output,
    )


def add_generate_demes_parsers(subparsers: argparse.ArgumentParser) -> None:
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
    parser = subparsers.add_parser("GenerateDemes", help="Generate a Demes file using a InferDM output file.")

    add_model_argument(parser)
    add_demo_popt_argument(parser)

    parser.add_argument(
        "--Na", 
        type=positive_num, 
        dest="Na", 
        required=True, 
        help="Ancestral population size."
    )

    parser.add_argument(
        "--generation-time", 
        type=positive_num, 
        dest="generation_time", 
        required=False, 
        default=1, 
        help="Years per generation. Default: 1."
    )

    parser.add_argument(
        "--pop-num", 
        type=positive_int, 
        dest="pop_num", 
        required=True, 
        help="Number of populations (integer) for the model."
    )

    # # If users want custom names for populations, ancestral is always a population
    # # So names will always be ancestral + other populations
    # # or --pop-num + 1
    # pop_args = int(sys.argv[sys.argv.index("--pop-num")+1])
    # parser.add_argument(
    #     "--pop-names", 
    #     type=list, 
    #     dest="pop_num", 
    #     required=False, 
    #     nargs=pop_args,
    #     help="Number of populations (integer) for the model."
    # )

    add_output_argument(parser)
    parser.set_defaults(runner=_run_generate_demes_file)

















