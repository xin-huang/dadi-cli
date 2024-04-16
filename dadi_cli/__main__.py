import argparse
from dadi_cli.parsers.generate_fs_parsers import add_generate_fs_parsers
from dadi_cli.parsers.generate_cache_parsers import add_generate_cache_parsers
from dadi_cli.parsers.simulate_dm_parsers import add_simulate_dm_parsers
from dadi_cli.parsers.simulate_dfe_parsers import add_simulate_dfe_parsers
from dadi_cli.parsers.simulate_demes_parsers import add_simulate_demes_parsers
from dadi_cli.parsers.infer_dm_parsers import add_infer_dm_parsers
from dadi_cli.parsers.infer_dfe_parsers import add_infer_dfe_parsers
from dadi_cli.parsers.plot_parsers import add_plot_parsers
from dadi_cli.parsers.stat_dm_parsers import add_stat_dm_parsers
from dadi_cli.parsers.stat_dfe_parsers import add_stat_dfe_parsers
from dadi_cli.parsers.bestfit_parsers import add_bestfit_parsers
from dadi_cli.parsers.model_parsers import add_model_parsers
from dadi_cli.parsers.pdf_parsers import add_pdf_parsers


def _set_sigpipe_handler() -> None:
    """
    Sets the signal handler for SIGPIPE signals on POSIX systems.

    """
    import os, signal
    if os.name == "posix":
        # Set signal handler for SIGPIPE to quietly kill the program.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def _dadi_cli_parser() -> argparse.ArgumentParser:
    """
    Initializes and configures the command-line interface parser
    for dadi-cli.

    Returns
    -------
    top_parser : argparse.ArgumentParser
        A configured command-line interface parser.

    """
    top_parser = argparse.ArgumentParser()
    subparsers = top_parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    add_generate_fs_parsers(subparsers)
    add_generate_cache_parsers(subparsers)
    add_simulate_dm_parsers(subparsers)
    add_simulate_dfe_parsers(subparsers)
    add_simulate_demes_parsers(subparsers)
    add_infer_dm_parsers(subparsers)
    add_infer_dfe_parsers(subparsers)
    add_plot_parsers(subparsers)
    add_stat_dm_parsers(subparsers)
    add_stat_dfe_parsers(subparsers)
    add_bestfit_parsers(subparsers)
    add_model_parsers(subparsers)
    add_pdf_parsers(subparsers)

    return top_parser


def main(arg_list: list = None) -> None:
    """
    Main entry for dadi-cli.

    Parameters
    ----------
    arg_list : list, optional
        A list containing arguments for dadi-cli. Default: None.

    """
    _set_sigpipe_handler()
    parser = _dadi_cli_parser()
    args = parser.parse_args(arg_list)
    args.runner(args)
