import dadi
import dadi.NLopt_mod
import nlopt
import os, time
import numpy as np
from src.Models import get_dadi_model_func

def infer_demography(fs, func, grids, p0, output,
                     upper_bounds, lower_bounds, fixed_params, misid, cuda):
    
    if cuda:
        dadi.cuda_enabled(True)

    ts = time.time()
    seed = int(ts) + int(os.getpid())
    np.random.seed(seed)
    
    fs = dadi.Spectrum.from_file(fs)
    ns = fs.sample_sizes
    if grids == None:
        grids = [int(ns[0]+10), int(ns[0]+20), int(ns[0]+30)]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)

    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)

    # Optimization
    if len(ns) == 1:
        if ns > 20:
            fs_proj = fs.project([20])
        else: fs_proj = fs
    if len(ns) == 2:
        if (ns[0] > 20) and (ns[1] > 20):
            fs_proj = fs.project([20, 20])
        elif (ns[0] > 20) and (ns[1] <= 20):
            fs_proj = fs.project([20, ns[1]])
        elif (ns[0] <= 20) and (ns[1] > 20):
            fs_proj = fs.project([ns[0], 20])
        else:
            fs_proj = fs
    ns_proj = fs_proj.sample_sizes
    grids_proj = [ns_proj.max()+10, ns_proj.max()+20, ns_proj.max()+30]

    popt_global, LLopt_global = dadi.NLopt_mod.opt(p0, fs_proj, func_ex, grids_proj,
                                                   lower_bound=lower_bounds,
                                                   upper_bound=upper_bounds, fixed_params=fixed_params,
                                                   verbose=0, algorithm=nlopt.GN_MLSL_LDS,
                                                   local_optimizer=nlopt.LN_BOBYQA, maxeval=400)
    popt, LLopt = dadi.NLopt_mod.opt(popt_global, fs, func_ex, grids,
                                     lower_bound=lower_bounds,
                                     upper_bound=upper_bounds, fixed_params=fixed_params,
                                     verbose=0, algorithm=nlopt.LN_BOBYQA, maxeval=600)
    #print('Optimized parameters: {0}'.format(popt))

    # Calculate the best-fit model AFS.
    model = func_ex(popt, ns, grids)
    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll_multinom(model, fs)
    #print('Maximum log composite likelihood: {0}'.format(ll_model))
    # The optimal value of theta given the model.
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)
    #print('Optimal value of theta: {0}'.format(theta))

    #with open(output, 'w') as f:
    #    f.write(str(ll_model))
    #    for p in popt:
    #        f.write("\t")
    #        f.write(str(p))
    #    f.write("\t" + str(theta) + "\n")

    return ll_model, popt, theta