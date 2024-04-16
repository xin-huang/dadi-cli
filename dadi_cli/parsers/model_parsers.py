import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.Models import *


def _run_model(args: argparse.Namespace) -> None:
    """
    Runs model operations based on user input, either listing available built-in models or
    providing detailed information about specific models.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object that contains all the command-line arguments provided to the function.
        The relevant attributes in this namespace include:
        - names (list of str or None): A list of model names for which details are requested.
          If this is None, the function will simply list all available models.

    """
    if args.names is None:
        print_built_in_models()
    else:
        print_built_in_model_details(args.names)


def add_model_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a subparser for the 'Model' command to an existing collection of subparsers. This command
    allows users to either view a list of all available demographic models or to get detailed information
    about a specific model if the model name is provided.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object from an ArgumentParser to which the 'Model' command subparser will be added.
        This allows for handling specific arguments dedicated to displaying demographic models.

    """
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

    parser.set_defaults(runner=_run_model)
