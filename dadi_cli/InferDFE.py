import dadi
import dadi.DFE
import nlopt
import os, time
import numpy as np
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import convert_to_None


def infer_dfe(
    fs,
    cache1d,
    cache2d,
    sele_dist,
    sele_dist2,
    theta,
    p0,
    upper_bounds,
    lower_bounds,
    fixed_params,
    misid,
    cuda,
    maxeval,
    maxtime,
    bestfits=None,
    seed=None,
):
    """
    Description:
        DFE inference.

    Arguments:
        fs dadi.Spectrum: Frequency spectrum.
        cache1d dadi.DFE.Cache1D_mod: Caches of 1d frequency spectra for DFE inference.
        cache2d dadi.DFE.Cache2D_mod: Caches of 2d frequency spectra for DFE inference.
        sele_dist str: Name of the 1d PDF function for modeling DFEs.
        sele_dist2 str: Name of the 2d PDF function for modeling DFEs.
        theta float: Population-scaled mutation rate inferred from the demographic model without selection.
        p0 list: Initial parameter values for inference.
        upper_bounds list: Upper bounds of the optimized parameters.
        lower_bounds list: Lower bounds of the optimized parameters.
        fixed_params list: Fixed parameters during the inference.
        misid bool: If True, add a parameter for modeling ancestral state misidentification when data are polarized.
        cuda bool: If True, use GPU to speed up calculation;
                   Otherwise, use CPU to do calculation.
        maxeval int: Max number of parameter set evaluations tried for optimizing demography.
        maxtime int: Max amount of time for optimizing demography.
        seed int: Seed for generating random numbers.

    Returns:
        ll_model float: Log(likelihood) of the inferred model.
        popt list: Optimized parameters.
        theta float: Population-scaled mutation rate inferred from the demographic model with selection.
    """

    # Randomize starting parameter values
    if seed != None:
        np.random.seed(seed)

    if bestfits != None:
        p0 = bestfits[np.random.randint(len(bestfits))%10]

    if cache1d != None:
        func = cache1d.integrate
    if cache2d != None:
        func = cache2d.integrate

    if sele_dist != None:
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 != None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if (sele_dist == None) and (sele_dist2 != None):
        sele_dist = sele_dist2

    if (cache1d != None) and (cache2d != None):
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
    if (cache1d != None) and (cache2d != None):
        model = func(popt, None, cache1d, cache2d, sele_dist, sele_dist2, theta, None)
    else:
        model = func(popt, None, sele_dist, theta, None)

    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll(model, fs)

    return ll_model, popt, theta
