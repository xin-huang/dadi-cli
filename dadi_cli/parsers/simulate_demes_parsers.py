import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.SimulateFs import simulate_demes


def _run_simulate_demes(args: argparse.Namespace) -> None:
    """
    Simulates allele frequency spectra based on a demographic model defined in a demes-format file.

    Parameters
    ----------
    args : Namespace
        A namespace from argparse that contains all necessary parameters for the simulation.
        The function expects the following attributes:
        - demes_file : str
            Path or URL to the file in demes format which describes the demographic model.
        - output : str
            The directory path where the simulation results will be saved.
        - sample_sizes : list of int
            List of sample sizes for which to simulate the frequency spectra.
        - grids : list of int
            List of grid sizes to use in the simulation for numerical accuracy.
        - pop_ids : list of str
            List of population identifiers corresponding to the populations in the demes file.

    """
    if "://" in args.demes_file:
        import urllib.request
        model_fi = open("demes_file.yml","w")
        with urllib.request.urlopen(args.demes_file) as f:
            model_fi.write(f.read().decode('utf-8'))
        model_fi.close()
        args.demes_file = "demes_file.yml"

    make_dir(args.output)
    simulate_demes(
        demes_file=args.demes_file, 
        ns=args.sample_sizes, 
        pts_l=args.grids, 
        pop_ids=args.pop_ids, 
        output=args.output
    )


def add_simulate_demes_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a parser for the "SimulateDemes" command to the subparsers collection. This function
    configures command-line arguments for simulating allele frequency spectra from demographic
    models specified in a Demes format YAML file.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "SimulateDemes", help="Generate frequency spectrum based on a Demes .yml file."
    )
    parser.add_argument(
        "--demes-file",
        type=existed_file,
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
    parser.set_defaults(runner=_run_simulate_demes)
