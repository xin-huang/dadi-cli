import glob, sys
import numpy as np
import dadi
import demes
from dadi_cli.Models import get_model
from dadi_cli.utilities import get_opts_and_theta


def generate_demes_file(
    model: str,
    model_file: str,
    demo_popt: str,
    Na: float, 
    generation_time: float,
    pop_num: int,
    output: str,

) -> None:
    """
    Obtains best-fit parameters from optimization results, filters them based on log-likelihood
    differences, boundaries, and ranks them, finally outputs the results to a specified file.

    Parameters
    ----------
    model : str
        Model name.
    model_file : str
        Path + name of file with custom models.
    demo_popt : str
        Path + name of file with inferred parameters.
    Na : float
        Ancestral population size.
    generation_time : float
        Number of years per generation.
    pop_num : int
        Number of populations. Currently dadi/dadi-cli doesn't have an automatic way to get number of populations.
    output : str
        Name of output Demes file.

    Returns
    -------
    str | None
        Demes file.

    Raises
    ------
    ValueError
        If no files are found at the specified path or if an incorrect path naming convention is used.
    """
    func, param_names = get_model(model, model_file)

    # gen_cache=True, because misid is not required to generate Demes file
    demo_popt, theta = get_opts_and_theta(demo_popt, gen_cache=True)

    ns = [4] * pop_num
    grid = 10

    func(demo_popt, ns, grid)

    # Generate Demes file
    g = dadi.Demes.output(Nref=Na, generation_time=generation_time)#, 
    #deme_mapping={'ancestral':['d1_1'], 'pre_split': ['d2_1'], 'Mmd_IRA':['d3_1'], 'Mmd_FRA':['d3_2']})
    g.description = ''
    demes.dump(g, output)






























