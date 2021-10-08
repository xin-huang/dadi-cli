import os, time
import numpy as np
import dadi, nlopt

def pts_l_func(fs):
    """
    Plausible pts_l for modeling an fs
    """
    n = max(fs.sample_sizes)
    return (int(n*1.1)+2, int(n*1.2)+4, int(n*1.3)+6)

def infer_demography(fs, func, p0, pts_l, upper_bounds, lower_bounds, 
                     fixed_params, misid, cuda):
    # TODO: Need to consider appropriate rtol & atol values, and whether these maxeval are appropriate
    if cuda:
        dadi.cuda_enabled(True)

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)

    # Randomize starting parameter values
    seed = int(time.time()) + int(os.getpid())
    np.random.seed(seed)
    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)

    # First, global optimization in which sample sizes are at most 20 per axis
    # TODO: Need option to disable this if modeling inbreeding
    proj_ns = np.minimum(fs.sample_sizes, 20)
    fs_proj = fs.project(proj_ns)
    pts_l_proj = pts_l_func(fs_proj)
    popt_global, _ = dadi.Inference.opt(p0, fs_proj, func_ex, pts_l_proj,
                                        lower_bound=lower_bounds,
                                        upper_bound=upper_bounds, fixed_params=fixed_params,
                                        algorithm=nlopt.GN_MLSL,
                                        local_optimizer=nlopt.LN_BOBYQA, maxeval=100)

    # Now local optimization
    if pts_l is None:
        pts_l = pts_l_func(fs)
    # If global optimization ended on boundary, this will pull parameters back into domain
    p0 = dadi.Misc.perturb_params(popt_global, fold=0, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)
    popt, _ = dadi.Inference.opt(popt_global, fs, func_ex, pts_l,
                                 lower_bound=lower_bounds,
                                 upper_bound=upper_bounds, fixed_params=fixed_params,
                                 algorithm=nlopt.LN_BOBYQA, maxeval=100)

    # Calculate the best-fit model to get ll and theta
    model = func_ex(popt, fs.sample_sizes, pts_l)
    ll_model = dadi.Inference.ll_multinom(model, fs)
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)

    return ll_model, popt, theta