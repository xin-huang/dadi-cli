import argparse, multiprocessing, sys
import numpy as np
from dadi_cli.parsers.argument_validation import *


def add_output_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an output file argument to a parser.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The argparse.ArgumentParser object to which the output file argument will be added.

    """
    parser.add_argument(
        "--output", type=str, required=True, help="Name of the output file."
    )


def add_bounds_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds lower and upper bounds arguments to a parser, conditional on the model type and options.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the bounds arguments will be added.

    """
    # Check that the model is not a standard neutral model
    if 'snm_1d' not in sys.argv and 'snm_2d' not in sys.argv:
        boundary_req = True
    else:
        if '--nomisid' in sys.argv:
            boundary_req = False
        else:
            boundary_req = True

    parser.add_argument(
        "--lbounds",
        type=float,
        nargs="+",
        required=boundary_req,
        help="Lower bounds of the optimized parameters.",
    )

    parser.add_argument(
        "--ubounds",
        type=float,
        nargs="+",
        required=boundary_req,
        help="Upper bounds of the optimized parameters.",
    )


def add_demo_popt_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds a demographic optimization parameter file argument to a parser, conditional on the model type.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the demographic optimization parameter file argument will be added.

    """
    # Check that the model is not a standard neutral model
    bestfit_req = False
    if 'equil' not in sys.argv:
        bestfit_req = True

    parser.add_argument(
        "--demo-popt",
        type=existed_file,
        required=bestfit_req,
        help="File containing the bestfit parameters for the demographic model.",
        dest="demo_popt",
    )


def add_grids_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds a grids argument to a parser to specify the sizes of grids used in computations.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the grid sizes argument will be added.

    """
    parser.add_argument(
        "--grids",
        type=positive_int,
        nargs=3,
        help="Sizes of grids. Default is based on sample size.",
    )


def add_misid_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to the parser to control the inclusion of a parameter for modeling ancestral state misidentification.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the misidentification control argument will be added.

    """
    # Note that the code previously had a --misid function that did the opposite, but this ia more sensible default.
    parser.add_argument(
        "--nomisid",
        default=False,
        action="store_true",
        help="Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized.",
    )


def add_model_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds model-related arguments to a parser for specifying demographic models in a command-line interface.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the model name and model file arguments will be added.

    """
    # Because most of the functions for Plot
    # do not require a model, we make it
    # conditionally required.
    req_model_arg = True
    if 'Plot' in sys.argv:
        req_model_arg = False

    parser.add_argument(
        "--model",
        type=str,
        required=req_model_arg,
        help="Name of the demographic model. To check available demographic models, please use `dadi-cli Model`.",
    )
    parser.add_argument(
        "--model-file",
        type=existed_file,
        required=False,
        dest="model_file",
        help="Name of python module file (not including .py) that contains custom models to use. Can be an HTML link. Default: None.",
    )


def add_fs_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify the frequency spectrum file used for demographic inference.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the frequency spectrum file argument will be added.

    """
    parser.add_argument(
        "--fs",
        type=existed_file,
        required=True,
        help="Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link.",
    )


def add_seed_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify a random seed for ensuring reproducibility.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the random seed argument will be added.

    """
    parser.add_argument("--seed", type=positive_int, help="Random seed.")


def add_constant_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify constant parameters for inference or Godambe analysis.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the constants argument will be added.

    """
    parser.add_argument(
        "--constants",
        default=-1,
        type=float,
        nargs="+",
        help="Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None.",
    )


def add_delta_ll_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify the maximum permissible percentage difference in log-likelihoods for convergence checks.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the delta log-likelihood argument will be added.

    """
    parser.add_argument(
        "--delta-ll",
        type=positive_num,
        required=False,
        dest="delta_ll",
        default=0.0001,
        help="When using --check-convergence argument in InferDM or InferDFE modules or the BestFits module, set the max percentage difference for log-likliehoods compared to the best optimization log-likliehood to be consider convergent (with 1 being 100%% difference to the best optimization's log-likelihood). Default: 0.0001.",
    )


def add_sample_sizes_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify the sample sizes of populations for demographic analysis.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the sample sizes argument will be added.

    """
    parser.add_argument(
        "--sample-sizes",
        type=positive_int,
        nargs="+",
        required=True,
        help="Sample sizes of populations.",
        dest="sample_sizes",
    )


def add_eps_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser to specify the step sizes for Godambe analysis.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the epsilon (step sizes) argument will be added.

    """
    parser.add_argument(
        "--eps",
        default=[0.1, 0.01, 0.001],
        type=positive_num,
        nargs="+",
        required=False,
        help="Step sizes to try for Godambe analysis. Default: [0.1, 0.01, 0.001]",
    )


def add_popt_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds arguments to a parser for specifying files containing best-fit parameters for demographic and DFE models.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the best-fit parameter file arguments will be added.

    """
    parser.add_argument(
        "--demo-popt",
        type=existed_file,
        dest="demo_popt",
        help="File containing the bestfit demographic parameters, generated by `dadi-cli BestFit`.",
    )

    parser.add_argument(
        "--dfe-popt",
        type=existed_file,
        dest="dfe_popt",
        help="File containing the bestfit DFE parameters, generated by `dadi-cli BestFit`.",
    )


def add_dfe_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds arguments to a parser for specifying cache files and probability density functions used in DFE (Distribution of Fitness Effects) analysis.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the DFE cache and PDF arguments will be added.

    """
    parser.add_argument(
        "--cache1d",
        type=existed_file,
        help="File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`.",
    )

    parser.add_argument(
        "--cache2d",
        type=existed_file,
        help="File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`.",
    )

    parser.add_argument(
        "--pdf1d",
        type=str,
        help="1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`.",
    )

    parser.add_argument(
        "--pdf2d",
        type=str,
        help="2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`.",
    )


# Currently this command is only needed for param_names.
def add_mix_pdf_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds an argument to a parser for specifying a mixed probability density function (PDF) model name used in joint DFE inference.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which the mixed PDF model name argument will be added.

    """
    parser.add_argument(
        "--mix-pdf",
        dest="mix_pdf",
        type=str,
        default=None,
        help="If you are using a model that is a mixture of probability density function for the joint DFE inference pass in the model name. To check available probability density functions, please use `dadi-cli Pdf`.",
    )


def add_inference_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds a series of arguments to a parser related to inference configurations for demographic models,
    including initial parameters, output file naming, convergence criteria, and computational settings.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser object to which all inference-related arguments will be added.

    """
    parser.add_argument(
        "--p0",
        default=-1,
        type=float,
        nargs="+",
        required=False,
        help="Initial parameter values for inference.",
    )

    parser.add_argument(
        "--output-prefix",
        type=str,
        required=True,
        dest="output_prefix",
        help="Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files).",
    )

    parser.add_argument(
        "--optimizations",
        default=100,
        type=positive_int,
        help="Total number of optimizations to run. Default: 100.",
    )

    parser.add_argument(
        "--check-convergence",
        default=0,
        type=positive_int,
        dest="check_convergence",
        help="Start checking for convergence after a chosen number of optimizations. Optimization runs will stop early if convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default.",
    )

    parser.add_argument(
        "--force-convergence",
        default=0,
        type=positive_int,
        dest="force_convergence",
        help="Start checking for convergence after a chosen number of optimizations. Optimization runs will continue until convergence criteria is reached (--optimizations flag will be ignored). BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default.",
    )

    parser.add_argument(
        "--work-queue",
        nargs=2,
        default=[],
        action="store",
        dest="work_queue",
        help="Enable Work Queue. Additional arguments are the WorkQueue project name, the name of the password file.",
    )

    parser.add_argument(
        "--port",
        default=9123,
        type=positive_int,
        dest="port",
        help="Choose a specific port for Work Queue communication. Default 9123.",
    )

    parser.add_argument(
        "--debug-wq",
        default=False,
        action="store_true",
        dest="debug_wq",
        help='Store debug information from WorkQueue to a file called "debug.log". Default: False.',
    )

    parser.add_argument(
        "--maxeval",
        type=positive_int,
        default=False,
        help="Max number of parameter set evaluations tried for optimizing demography. Default: Number of parameters multiplied by 100.",
    )

    parser.add_argument(
        "--maxtime",
        type=positive_int,
        default=np.inf,
        help="Max amount of time for optimizing demography. Default: infinite.",
    )

    parser.add_argument(
        "--cpus",
        type=positive_int,
        default=multiprocessing.cpu_count(),
        help="Number of CPUs to use in multiprocessing. Default: All available CPUs.",
    )

    parser.add_argument(
        "--gpus",
        type=nonnegative_int,
        default=0,
        help="Number of GPUs to use in multiprocessing. Default: 0.",
    )

    parser.add_argument(
        "--bestfit-p0-file", 
        type=existed_file, 
        dest="bestfit_p0", 
        help="Pass in a .bestfit or .opt.<N> file name to cycle --p0 between up to the top 10 best fits for each optimization."
    )


def add_p0_argument(parser: argparse.ArgumentParser) -> None:
    """
    Adds the '--p0' command line argument to an argparse.ArgumentParser instance,
    which is conditionally required based on the presence of specific command line arguments.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser to which the '--p0' argument should be added. This parser configures
        the command line arguments for a script or application.

    """
    p0_req = False
    if 'snm_1d' not in sys.argv and 'snm_2d' not in sys.argv:
        p0_req = True
    else:
        if '--nomisid' not in sys.argv:
            p0_req = True

    parser.add_argument(
        "--p0",
        type=float,
        nargs="+",
        required=p0_req,
        help="Parameters for simulated demography or dfe.",
    )


def make_dir(path: str) -> None:
    """
    Ensures that the directory for the given path exists. If the directory does not exist,
    it is created.

    Parameters
    ----------
    path : str
        The file system path for which the parent directory needs to be ensured. This path
        can be to a file or a directory; if it is to a file, the parent directory is targeted.

    """
    parent_dir = os.path.dirname(path)
    if parent_dir != '':
        os.makedirs(parent_dir, exist_ok=True)
