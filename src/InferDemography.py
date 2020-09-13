import dadi
import dadi.NLopt_mod
import nlopt
import matplotlib.pyplot as plt
from Models import get_dadi_model_func

def infer_demography(fs, model, grids, p0, output_dir, output_prefix,
                     upper_bounds, lower_bounds, fixed_params, misid, cuda):
    
    fs = dadi.Spectrum.from_file(fs)
    ns = fs.sample_sizes
    if grids == None:
        grids = [int(ns[0]+10), int(ns[0]+20), int(ns[0]+30)]

    func = get_dadi_model_func(model)
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)

    p0 = dadi.Misc.perturb_params(p0, fold=1, upper_bound=upper_bounds,
                                  lower_bound=lower_bounds)

    # Optimization
    if len(ns) == 1:
        fs_proj = fs.project([20])
    if len(ns) == 2:
        fs_proj = fs.project([20, 20])
    ns_proj = fs_proj.sample_sizes
    grids_proj = [ns_proj.max()+10, ns_proj.max()+20, ns_proj.max()+30]

    popt_global, LLopt_global, result_global = dadi.NLopt_mod.opt(p0, fs_proj, func_ex, grids_proj,
                                                                  lower_bound=lower_bounds,
                                                                  upper_bound=upper_bounds,
                                                                  verbose=0, algorithm=nlopt.GN_MLSL_LDS,
                                                                  local_optimizer=nlopt.LN_BOBYQA, maxeval=400)
    popt, LLopt, result = dadi.NLopt_mod.opt(popt_global, fs, func_ex, grids,
                                             lower_bound=lower_bounds,
                                             upper_bound=upper_bounds,
                                             verbose=0, algorithm=nlopt.LN_BOBYQA, maxeval=600)
    print('Optimized parameters: {0}'.format(popt))

    # Calculate the best-fit model AFS.
    model = func_ex(popt, ns, grids)
    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll_multinom(model, fs)
    print('Maximum log composite likelihood: {0}'.format(ll_model))
    # The optimal value of theta given the model.
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)
    print('Optimal value of theta: {0}'.format(theta))

    # Plot figures
    output_prefix += '_ll_%.4f_params' %tuple([ll_model])
    output_prefix += '_%.4f'*len(popt) %tuple(popt)
    output_prefix += '_theta_%.4f' %tuple([theta])

    fig = plt.figure(219033)
    fig.clear()
    if len(ns) == 1:
        dadi.Plotting.plot_1d_comp_multinom(model, fs, vmin=1)
    if len(ns) == 2:
        dadi.Plotting.plot_2d_comp_multinom(model, fs, vmin=1)
    fig.savefig(output_dir + "/" + output_prefix + '.pdf')
