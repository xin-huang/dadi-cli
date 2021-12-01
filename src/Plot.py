import dadi, pickle
import numpy as np
import matplotlib.pyplot as plt
 
fig = plt.figure(figsize=(8,6))

def plot_single_sfs(fs, projections, output, vmin):

    fs = dadi.Spectrum.from_file(fs)    
    
    fig = plt.figure(219033)
    if len(fs.sample_sizes) == 1:
        if projections == None: projections = [20]
        fs = fs.project(projections)
        dadi.Plotting.plot_1d_fs(fs)
    if len(fs.sample_sizes) == 2:
        if projections == None: projections = [20, 20]
        fs = fs.project(projections)
        dadi.Plotting.plot_single_2d_sfs(fs, vmin=vmin)
    fig.savefig(output)

def plot_comparison(fs, fs2, projections, output, vmin, resid_range):

    fs = dadi.Spectrum.from_file(fs)
    fs2 = dadi.Spectrum.from_file(fs2)

    fig = plt.figure(219033)
    if len(fs.sample_sizes) == 1:
        if projections == None: projections = [20]
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_1d_comp_Poisson(model=fs, data=fs2)
    if len(fs.sample_sizes) == 2:
        if projections == None: projections = [20, 20]
        fs = fs.project(projections)
        fs2 = fs2.project(projections) 
        dadi.Plotting.plot_2d_comp_Poisson(model=fs, data=fs2, vmin=vmin, resid_range=resid_range)
    fig.savefig(output)

def plot_fitted_demography(fs, model, popt, projections, misid, output, vmin, resid_range):
    
    from src.Models import get_dadi_model_func
    func = get_dadi_model_func(model)

    from src.GenerateCache import _get_opt
    popt = _get_opt(popt, False)

    fs = dadi.Spectrum.from_file(fs)
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)
    ns = fs.sample_sizes
    pts_l = [int(max(ns)+10), int(max(ns)+20), int(max(ns)+30)]

    model = func_ex(popt, ns, pts_l)    
   
    fig = plt.figure(219033)
    if len(ns) == 1: 
        if projections == None: projections = [20]
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_1d_comp_multinom(model, fs)   
    if len(ns) == 2:
        if projections == None: projections = [20, 20]
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_multinom(model, fs, vmin=vmin, resid_range=resid_range)
    fig.savefig(output) 


def plot_fitted_dfe(fs, cache1d, cache2d, demo_popt, sele_popt, projections, pdf, pdf2, misid, output, vmin, resid_range):

    import dadi.DFE
    from src.Pdfs import get_dadi_pdf
    
    from src.Stat import _get_theta
    theta = _get_theta(sele_popt)

    from src.GenerateCache import _get_opt
    sele_popt = _get_opt(sele_popt, False)

    fs = dadi.Spectrum.from_file(fs)

    if pdf != None:
        pdf = get_dadi_pdf(pdf)
    if pdf2 != None:
        pdf2 = get_dadi_pdf(pdf2)
        if pdf == None:
            pdf=pdf2

    ns = fs.sample_sizes
    # Integrate over a range of gammas
    pts_l = [max(ns)+10, max(ns)+20, max(ns)+30]
    if cache1d != None:
        spectra1d = pickle.load(open(cache1d, 'rb'))
        func = spectra1d.integrate
    if cache2d != None:
        spectra2d = pickle.load(open(cache2d, 'rb'))
        func = spectra2d.integrate
    if (cache1d != None) and (cache2d != None): 
        func = dadi.DFE.mixture
    
    if misid: func = dadi.Numerics.make_anc_state_misid_func(func)
    # Get expected SFS for MLE
    if (cache1d != None) and (cache2d != None):
        model = func(sele_popt, None, spectra1d, spectra2d, pdf, pdf2, theta, None)
    else:
        model = func(sele_popt, None, pdf, theta, None)

    fig = plt.figure(219033)
    if len(ns) == 1:
        if projections == None: projections = [20]
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_Poisson(model, fs)
    if len(ns) == 2:
        if projections == None: projections = [20, 20]
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_Poisson(model, fs, vmin=vmin, resid_range=resid_range)
    fig.savefig(output)

def plot_mut_prop(dfe_popt, pdf1d, misid, mut_rate, seq_len, ratio, output):

    from src.Pdfs import get_dadi_pdf

    dfe_params, theta = _get_bestfit_params(dfe_popt, misid)

    Na = theta/(4*mut_rate*seq_len*(ratio/(1+ratio)))

    def mut_prop(shape, scale, Na):
        from scipy import stats
        scale = scale / (2*Na)
        p1 = stats.gamma.cdf(1e-5, a=shape, scale=scale)
        p2 = stats.gamma.cdf(1e-4, a=shape, scale=scale)
        p3 = stats.gamma.cdf(1e-3, a=shape, scale=scale)
        p4 = stats.gamma.cdf(1e-2, a=shape, scale=scale)

        return p1, p2-p1, p3-p2, p4-p3, 1-p4

    props = mut_prop(dfe_params[0], dfe_params[1], Na)

    fig = plt.figure(219033)
    plt.bar([0,1,2,3,4],props,alpha=0.7)
    plt.ylabel('Proportion')
    plt.xlabel('Selection coefficient')
    plt.xticks([0,1,2,3,4],
               ['0<=|s|<1e-5', '1e-5<=|s|<1e-4', '1e-4<=|s|<1e-3', '1e-3<=|s|<1e-2', '1e-2<=|s|'], rotation=45)
    plt.grid(alpha=0.3)
    fig.savefig(output, bbox_inches='tight')

def _get_bestfit_params(filename, misid):

    opts = []
    fid = open(filename, 'r')
    for line in fid.readlines():
        if line.startswith('#'):
            continue
        elif line.startswith('# T'):
            break
        else:
            try:
                opts.append([float(_) for _ in line.rstrip().split()])
            except ValueError:
                pass
    fid.close()

    if len(opts) == 0:
        print('No optimization results found')
        return

    if misid:
        return opts[0][1:-2], opts[0][-1]
    else:
        return opts[0][1:-1], opts[0][-1]
