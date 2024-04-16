import dadi
import dadi.DFE
import nlopt
import os, time
import numpy as np
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import convert_to_None


def infer_dfe(
    fs: dadi.Spectrum,
    cache1d: dadi.DFE.Cache1D_mod,
    cache2d: dadi.DFE.Cache2D_mod,
    sele_dist: str,
    sele_dist2: str,
    theta: float,
    p0: list[float],
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
    Performs Distribution of Fitness Effects (DFE) inference using either 1D or 2D frequency spectra, or a mixture of both.

    Parameters
    ----------
    fs : dadi.Spectrum
        Frequency spectrum from which to infer the DFE.
    cache1d : dadi.DFE.Cache1D_mod
        Caches of 1D frequency spectra for DFE inference.
    cache2d : dadi.DFE.Cache2D_mod
        Caches of 2D frequency spectra for DFE inference.
    sele_dist : str
        Identifier for the 1D Probability Density Function (PDF) used for modeling DFEs.
    sele_dist2 : str
        Identifier for the 2D PDF used for modeling DFEs.
    theta : float
        Population-scaled mutation rate inferred from the demographic model without selection.
    p0 : list[float]
        Initial parameter values for the inference.
    upper_bounds : list[float]
        Upper bounds of the parameters for optimization.
    lower_bounds : list[float]
        Lower bounds of the parameters for optimization.
    fixed_params : list[float]
        Parameters that are held fixed during the optimization. Use `None` for parameters that are free to vary.
    misid : bool
        If True, incorporates a parameter to model ancestral state misidentification.
    cuda : bool
        If True, enables GPU acceleration for calculations. Otherwise, calculations are performed using the CPU.
    maxeval : int
        Maximum number of parameter set evaluations attempted during optimization.
    maxtime : int
        Maximum time allowed for optimization, in seconds.
    bestfits : list[float], optional
        List of best-fit parameters from previous runs to use as initial values. Randomly selects from these if provided.
    seed : int, optional
        Seed for random number generation, affecting the randomization of initial parameters and any stochastic processes.

    Returns
    -------
    ll_model : float
        Log-likelihood of the inferred model.
    popt : list[float]
        Optimized parameters.
    theta : float
        Population-scaled mutation rate inferred from the demographic model with selection.

    Raises
    ------
    ValueError
        If neither `cache1d` nor `cache2d` is provided, an error is raised.

    """
    if not cache1d and not cache2d:
        raise ValueError("At least one of cache1d or cache2d must be provided.")

    # Randomize starting parameter values
    if seed is not None:
        np.random.seed(seed)

    if bestfits is not None:
        p0 = bestfits[np.random.randint(len(bestfits))%10]

    if cache1d is not None:
        func = cache1d.integrate
    if cache2d is not None:
        func = cache2d.integrate

    if sele_dist is not None:
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 is not None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if (sele_dist is None) and (sele_dist2 is not None):
        sele_dist = sele_dist2

    if (cache1d is not None) and (cache2d is not None):
        func = dadi.DFE.Cache2D_mod.mixture
        func_args = [cache1d, cache2d, sele_dist, sele_dist2, theta]
    else:
        func_args = [sele_dist, theta]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    p0_len = len(p0)
    lower_bounds = convert_to_None(lower_bounds, p0_len)
    upper_bounds = convert_to_None(upper_bounds, p0_len)
    fixed_params = convert_to_None(fixed_params, p0_len)

    # Fit a DFE to the data
    # Initial guess and bounds
    p0 = dadi.Misc.perturb_params(
        p0, lower_bound=lower_bounds, upper_bound=upper_bounds
    )
    popt, _ = dadi.Inference.opt(
        p0,
        fs,
        func,
        pts=None,
        func_args=func_args,
        fixed_params=fixed_params,
        lower_bound=lower_bounds,
        upper_bound=upper_bounds,
        maxeval=maxeval,
        maxtime=maxtime,
        multinom=False,
        verbose=0,
    )

    # Get expected SFS for MLE
    if (cache1d is not None) and (cache2d is not None):
        model = func(popt, None, cache1d, cache2d, sele_dist, sele_dist2, theta, None)
    else:
        model = func(popt, None, sele_dist, theta, None)

    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll(model, fs)

    return ll_model, popt, theta
