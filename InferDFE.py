import dadi
import dadi.DFE
import pickle


def infer_dfe(fs, cache1d, cache2d, sele_dist, sele_dist2, theta, output_dir, 
              output_prefix, p0, upper_bounds, lower_bounds, fixed_params, mixture, misid, cuda):

    if cache1d != None:
        spectra1d = pickle.load(open(cache1d, 'rb'))
        func = spectra1d.integrate
        func_args = [sele_dist, theta]
    if cache2d != None:
        spectra2d = pickle.load(open(cache1d, 'rb'))
        func = spectra2d.integrate
        func_args = [sele_dist, theta]
    if mixture:
        func = dadi.DFE.Cache2D_mod.mixture
        func_args = [spectra1d, spectra2d, sele_dist, sele_dist2, theta]
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    # Fit a DFE to the data
    # Initial guess and bounds
    p0 = dadi.Misc.perturb_params(p0, fold=1, lower_bound=lower_bound, upper_bound=upper_bound)
    popt = dadi.Inference.optimize_log(p0, data, func, pts=None,
                                       func_args=func_args,
                                       lower_bound=lower_bound, upper_bound=upper_bound,
                                       verbose=0, maxiter=200, multinom=False)

    print('Optimized parameters: {0}'.format(popt))

    # Get expected SFS for MLE
    if mixture:
        model = func(popt, None, spectra1d, spectra2d, sele_dist, sele_dist2, theta, None)
    else:
        model = func(popt, None, sele_dist, theta, None)
    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll_multinom(model, data)
    print('Maximum log composite likelihood: {0}'.format(ll_model))

    # Plot figures
    output_prefix += '_ll_%.4f_params' %tuple([ll_model])
    output_prefix += '_%.4f'*len(popt) %tuple(popt)

    fig = plt.figure(219033)
    fig.clear()
    dadi.Plotting.plot_1d_comp_multinom(model, data)
    fig.savefig(output_dir + "/" + output_prefix + '.pdf')
