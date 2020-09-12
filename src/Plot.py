import dadi
import matplotlib.pyplot as plt
 
fig = plt.figure(figsize=(8,6))

def plot_single_sfs(fs, projections, output):
    if projections != None:
        fs = fs.project(projections)
    if len(fs.sample_sizes) == 1:
        dadi.Plotting.plot_1d_sfs(fs)
    if len(fs.sample_sizes) == 2:
        dadi.Plotting.plot_single_2d_sfs(fs)
    fig.savefig(output)

def plot_comparison(fs, fs2, projections, output, vmin, resid_range):
    if projections != None:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
    if len(fs.sample_sizes) == 1:
        dadi.Plotting.plot_1d_comp_Poisson(model=fs, data=fs2)
    if len(fs.sample_sizes) == 2:
        dadi.Plotting.plot_2d_comp_Poisson(model=fs, data=fs2, vmin=vmin, resid_range=resid_range)
    fig.savefig(output)

def plot_fitted_demography(fs, model, demography_params, projections, misid, output, vmin, resid_range):
    
    from Models import get_dadi_model_func
    func = get_dadi_model_func(model)

    if projections != None:
        fs = fs.project(projections)
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)
    ns = fs.sample_sizes
    pts_l = [int(ns[0]+10), int(ns[0]+20), int(ns[0]+30)]

    model = func_ex(popt, ns, pts_l)    
    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll_multinom(model, fs)
    print('Maximum log composite likelihood: {0}'.format(ll_model))
    # The optimal value of theta given the model.
    theta = dadi.Inference.optimal_sfs_scaling(model, fs)
    print('Optimal value of theta: {0}'.format(theta))
    
    if len(ns) == 1: 
        dadi.Plotting.plot_1d_comp_multinom(model, fs)   
    if len(ns) == 2:
        dadi.Plotting.plot_2d_comp_multinom(model, fs, vmin=vmin, resid_range=resid_range)


def plot_fitted_dfe(fs, cache, selection_params, projections, misid, output, vmin, resid_range):

    import dadi.DFE
    from Distribs import get_dadi_pdf
