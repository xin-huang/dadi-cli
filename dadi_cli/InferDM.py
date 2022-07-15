import os, time, inspect
import numpy as np
import dadi, nlopt
from dadi_cli.utilities import pts_l_func, convert_to_None

def infer_demography(fs, func, p0, pts_l, upper_bounds, lower_bounds, 
                     fixed_params, misid, cuda, maxeval, maxtime, bestfits=None, seed=None):

    # Set seed for starting parameter values when using WorkQueue
    if seed != None:
        np.random.seed(seed)

    # TODO: Need to consider appropriate rtol & atol values, and whether these maxeval are appropriate
    if cuda:
        dadi.cuda_enabled(True)

    if bestfits != None:
        p0 = bestfits[np.random.randint(len(bestfits))%10]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    
    func_ex = dadi.Numerics.make_extrap_func(func)
    p0_len = len(p0)
    lower_bounds = convert_to_None(lower_bounds, p0_len)
    upper_bounds = convert_to_None(upper_bounds, p0_len)
    fixed_params = convert_to_None(fixed_params, p0_len)

    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)
    if pts_l is None:
        pts_l = pts_l_func(fs.sample_sizes)

    popt, _ = dadi.Inference.opt(p0, fs, func_ex, pts_l,
                                 lower_bound=lower_bounds,
                                 upper_bound=upper_bounds, fixed_params=fixed_params,
                                 algorithm=nlopt.LN_BOBYQA, maxeval=maxeval, maxtime=maxtime, verbose=0)

    # Calculate the best-fit model to get ll and theta
    model = func_ex(popt, fs.sample_sizes, pts_l)
    ll_model = dadi.Inference.ll_multinom(model, fs)
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)

    return ll_model, popt, theta

def infer_global_opt(fs, func, p0, pts_l, upper_bounds, lower_bounds, 
                     fixed_params, misid, cuda, maxeval, maxtime, global_algorithm, seed=None):

    # Randomize starting parameter values
    if seed != None: 
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

    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)

    # First, global optimization in which sample sizes are at most 20 per axis
    proj_ns = np.minimum(fs.sample_sizes, 20)
    fs_proj = fs.project(proj_ns)
    pts_l_proj = pts_l_func(fs_proj.sample_sizes)
    popt, ll_global = dadi.Inference.opt(p0, fs_proj, func_ex, pts_l_proj,
                                        lower_bound=lower_bounds,
                                        upper_bound=upper_bounds, fixed_params=fixed_params,
                                        algorithm=global_algorithm,
                                        local_optimizer=nlopt.LN_BOBYQA, maxeval=maxeval, maxtime=maxtime, verbose=0)

    # If global optimization ended on boundary, this will pull parameters back into domain
    popt = dadi.Misc.perturb_params(popt, fold=0, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)
    return ll_global, popt, 0
