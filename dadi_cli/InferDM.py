import os, time, inspect
import numpy as np
import dadi, nlopt
from dadi_cli.utilities import pts_l_func, convert_to_None


def infer_demography(
    fs: dadi.Spectrum,
    func: callable,
    p0: list[float],
    pts_l: tuple[int],
    upper_bounds: list[float],
    lower_bounds: list[float],
    fixed_params: list[float],
    misid: bool,
    cuda: bool,
    maxeval: int,
    maxtime: int,
    bestfits: list[float] = None,
    seed: int = None,
) -> tuple[float, list[float], float]:
    """
    Performs demographic inference using a frequency spectrum and a demographic model.

    Parameters
    ----------
    fs : dadi.Spectrum
        Frequency spectrum for demographic inference.
    func : callable
        Demographic model function used for modeling.
    p0 : list[float]
        Initial parameter values for inference.
    pts_l : tuple[int], optional
        Grid sizes used in the demographic model.
    upper_bounds : list[float]
        Upper bounds of the optimized parameters.
    lower_bounds : list[float]
        Lower bounds of the optimized parameters.
    fixed_params : list[float]
        Parameters that are held fixed during the inference.
    misid : bool
        If True, incorporates a parameter to model ancestral state misidentification.
    cuda : bool
        If True, uses GPU acceleration for calculations; otherwise, uses CPU.
    maxeval : int
        Maximum number of parameter set evaluations during optimization.
    maxtime : int
        Maximum amount of time (in seconds) allowed for optimization.
    bestfits : list[float], optional
        List of best-fit parameters from previous runs to use as initial values.
    seed : int, optional
        Seed for random number generation, affecting initial parameter perturbation.

    Returns
    -------
    float
        Log likelihood of the inferred demographic model.
    list[float]
        List of optimized parameters.
    float
        Population-scaled mutation rate (theta) inferred from the demographic model.

    Raises
    ------
    nlopt.RoundoffLimited
        If optimization fails due to roundoff errors, likely indicating issues with parameter bounds or initial values.

    """

    # Set seed for starting parameter values when using WorkQueue
    if seed is not None:
        np.random.seed(seed)

    # TODO: Need to consider appropriate rtol & atol values, and whether these maxeval are appropriate
    if cuda:
        dadi.cuda_enabled(True)

    if bestfits is not None:
        p0 = bestfits[np.random.randint(len(bestfits))%10]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    func_ex = dadi.Numerics.make_extrap_func(func)
    p0_len = len(p0)
    lower_bounds = convert_to_None(lower_bounds, p0_len)
    upper_bounds = convert_to_None(upper_bounds, p0_len)
    fixed_params = convert_to_None(fixed_params, p0_len)

    p0 = dadi.Misc.perturb_params(
        p0, fold=1, upper_bound=upper_bounds, lower_bound=lower_bounds
    )
    if pts_l is None:
        pts_l = pts_l_func(fs.sample_sizes)

    try:
        popt, _ = dadi.Inference.opt(
            p0,
            fs,
            func_ex,
            pts_l,
            lower_bound=lower_bounds,
            upper_bound=upper_bounds,
            fixed_params=fixed_params,
            algorithm=nlopt.LN_BOBYQA,
            maxeval=maxeval,
            maxtime=maxtime,
            verbose=0,
        )

        # Calculate the best-fit model to get ll and theta
        model = func_ex(popt, fs.sample_sizes, pts_l)
        ll_model = dadi.Inference.ll_multinom(model, fs)
        theta = dadi.Inference.optimal_sfs_scaling(model, fs)
    except nlopt.RoundoffLimited:
        print('nlopt.RoundoffLimited occured, other jobs still running. Users might want to adjust their boundaries or starting parameters if this message occures many times.')
        ll_model = -np.inf
        theta = np.nan
        popt = [np.nan for ele in p0]


    return ll_model, popt, theta


def infer_global_opt(
    fs: dadi.Spectrum,
    func: callable,
    p0: list[float],
    pts_l: tuple[int],
    upper_bounds: list[float],
    lower_bounds: list[float],
    fixed_params: list[float],
    misid: bool,
    cuda: bool,
    maxeval: int,
    maxtime: int,
    global_algorithm: str,
    seed: int = None,
) -> tuple[float, list[float], float]:
    """
    Performs demographic inference using global optimization techniques.

    Parameters
    ----------
    fs : dadi.Spectrum
        Frequency spectrum from which to infer demographics.
    func : callable
        Demographic model function to be fitted.
    p0 : list[float]
        Initial parameter values for the optimization.
    pts_l : tuple[int]
        Grid sizes used in the numerical integration of the demographic model.
    upper_bounds : list[float]
        Upper bounds for the parameters during optimization.
    lower_bounds : list[float]
        Lower bounds for the parameters during optimization.
    fixed_params : list[float]
        Parameters that are held fixed during the optimization; None for parameters that are free.
    misid : bool
        If True, incorporate a model for ancestral state misidentification.
    cuda : bool
        Enable GPU acceleration for calculations.
    maxeval : int
        Maximum number of evaluations for the optimizer.
    maxtime : int
        Maximum time (in seconds) allowed for optimization.
    global_algorithm : str
        Name of the global optimization algorithm to use.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    float
        Log likelihood of the best fit model.
    list[float]
        Optimized parameter values.
    float
        Population-scaled mutation rate (theta) based on the best fit model.

    """
    # Randomize starting parameter values
    if seed is not None:
        np.random.seed(seed)

    if cuda:
        dadi.cuda_enabled(True)

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    func_ex = dadi.Numerics.make_extrap_func(func)

    p0_len = len(p0)
    lower_bounds = convert_to_None(lower_bounds, p0_len)
    upper_bounds = convert_to_None(upper_bounds, p0_len)
    fixed_params = convert_to_None(fixed_params, p0_len)

    p0 = dadi.Misc.perturb_params(
        p0, fold=1, upper_bound=upper_bounds, lower_bound=lower_bounds
    )

    # First, global optimization in which sample sizes are at most 20 per axis
    proj_ns = np.minimum(fs.sample_sizes, 20)
    fs_proj = fs.project(proj_ns)
    pts_l_proj = pts_l_func(fs_proj.sample_sizes)
    popt, ll_global = dadi.Inference.opt(
        p0,
        fs_proj,
        func_ex,
        pts_l_proj,
        lower_bound=lower_bounds,
        upper_bound=upper_bounds,
        fixed_params=fixed_params,
        algorithm=global_algorithm,
        local_optimizer=nlopt.LN_BOBYQA,
        maxeval=maxeval,
        maxtime=maxtime,
        verbose=0,
    )

    # If global optimization ended on boundary, this will pull parameters back into domain
    popt = dadi.Misc.perturb_params(
        popt, fold=0, upper_bound=upper_bounds, lower_bound=lower_bounds
    )
    pts_l = pts_l_func(fs.sample_sizes)
    model = func_ex(popt, fs.sample_sizes, pts_l)
    ll_global = dadi.Inference.ll_multinom(model, fs)
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)

    return ll_global, popt, theta
