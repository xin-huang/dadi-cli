import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.Pdfs import *


def _run_pdf(args: argparse.Namespace) -> None:
    """
    Executes display commands for probability distribution functions (PDFs) based on user input.
    This function determines whether to list all available PDFs or to provide detailed information
    about specific PDFs.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object that holds all the command-line arguments provided to the function.
        The relevant attributes in this namespace include:
        - names (list of str or None): A list of PDF names for which details are requested.
          If this is None, the function will simply list all available PDFs.

    """
    if args.names is None:
        print_available_pdfs()
    else:
        print_pdf_details(args.names)


def add_pdf_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a subparser for the 'Pdf' command to an existing collection of subparsers. This command
    allows users to either view a list of all available probability density functions (PDFs) or to get
    detailed information about a specific PDF if the name is provided.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object from an ArgumentParser to which the 'Pdf' command subparser will be added.
        This allows for handling specific arguments dedicated to displaying information about PDFs.

    """
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

    parser.set_defaults(runner=_run_pdf)
