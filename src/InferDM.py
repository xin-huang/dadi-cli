import dadi
import nlopt
import os, time
import numpy as np
from src.Models import get_dadi_model_func

def infer_demography(fs, func, grids, p0, output,
                     upper_bounds, lower_bounds, fixed_params, misid, cuda):
    if cuda:
        dadi.cuda_enabled(True)

    seed = int(time.time()) + int(os.getpid())
    np.random.seed(seed)
    
    fs = dadi.Spectrum.from_file(fs)
    ns = fs.sample_sizes
    if grids is None:
        grids = [int(ns[0]+10), int(ns[0]+20), int(ns[0]+30)]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)

    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)

    # First, a global optimization in which sample sizes are at most 20 per axis
    # XXX: Need option to disable this if modeling inbreeding
    proj_ns = np.mininum(ns, 20)
    fs_proj = fs.project(proj_ns)

    ns_proj = fs_proj.sample_sizes
    grids_proj = [ns_proj.max()+10, ns_proj.max()+20, ns_proj.max()+30]

    popt_global, _ = dadi.Inference.opt(p0, fs_proj, func_ex, grids_proj,
                                        lower_bound=lower_bounds,
                                        upper_bound=upper_bounds, fixed_params=fixed_params,
                                        algorithm=nlopt.GN_MLSL_LDS,
                                        local_optimizer=nlopt.LN_BOBYQA, maxeval=400)
    popt, LLopt = dadi.Inference.opt(popt_global, fs, func_ex, grids,
                                     lower_bound=lower_bounds,
                                     upper_bound=upper_bounds, fixed_params=fixed_params,
                                     algorithm=nlopt.LN_BOBYQA, maxeval=600)

    # Calculate the best-fit model to get ll, and theta
    model = func_ex(popt, ns, grids)
    ll_model = dadi.Inference.ll_multinom(model, fs)
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)

    return ll_model, popt, theta
