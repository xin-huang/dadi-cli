import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.SimulateFs import simulate_demography


def _run_simulate_dm(args: argparse.Namespace) -> None:
    """
    Simulates allele frequency spectra based on a specified demographic model.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace from argparse that contains all necessary parameters for the
        demographic simulation. The function expects the following attributes:
        - misid : bool
            Automatically set based on `nomisid`; indicates whether misidentification
            corrections are to be considered.
        - model_file : str, optional
            Path or URL to a Python script containing demographic model definitions.
            If provided via URL, the script is downloaded and used for simulation.
        - model : str
            The demographic model to use for simulation.
        - p0 : list of float
            Initial parameter values for the demographic simulation.
        - sample_sizes : list of int
            List of sample sizes for which to simulate the frequency spectra.
        - grids : list of int
            List of grid sizes to use in the simulation for numerical accuracy.
        - output : str
            The directory path where the simulation results will be saved.
        - inference_file : str, optional
            Path to a file that contains additional inference parameters or data.
        - nomisid : bool
            Flag to indicate that misidentification should not be considered, used
            to set `misid`.

    """
    # Due to development history, much of the code expects a args.misid variable, so create it.
    args.misid = not args.nomisid
    if args.model_file is not None:
        if "://" in args.model_file:
            import urllib.request
            model_fi = open("dadi_models.py","w")
            with urllib.request.urlopen(args.model_file) as f:
                model_fi.write(f.read().decode('utf-8'))
            model_fi.close()
            args.model_file = "dadi_models"

    make_dir(args.output)

    simulate_demography(
        model=args.model,
        model_file=args.model_file,
        p0=args.p0,
        ns=args.sample_sizes,
        pts_l=args.grids,
        misid=args.misid,
        output=args.output,
        inference_file=args.inference_file,
    )


def add_simulate_dm_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds a parser for the "SimulateDM" command to the subparsers collection. This function
    configures command-line arguments for simulating allele frequency spectra based on a
    specified demographic model.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        A special action object from argparse that holds subparsers. This is
        typically obtained from a call to `add_subparsers()` on an `ArgumentParser` object.

    """
    parser = subparsers.add_parser(
        "SimulateDM", help="Generate frequency spectrum based on a demographic history."
    )
    add_model_argument(parser)
    add_sample_sizes_argument(parser)
    add_p0_argument(parser)
    add_misid_argument(parser)
    add_grids_argument(parser)

    parser.add_argument(
        "--inference-file",
        dest="inference_file",
        default=False,
        action="store_true",
        help='Make an output file like you would get for running InferDM to pass into GenerateCache to make caches with your simulated demographic model. Will be the same name and path as output + ".SimulateFs.pseudofit"; Default: False.',
    )
    add_output_argument(parser)
    parser.set_defaults(runner=_run_simulate_dm)
