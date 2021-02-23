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

    fs = dadi.Spectrum.from_file(fs)
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)
    ns = fs.sample_sizes
    pts_l = [int(ns[0]+10), int(ns[0]+20), int(ns[0]+30)]

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


def plot_fitted_dfe(fs, cache1d, cache2d, demo_popt, sele_popt, ns_s, projections, pdf, pdf2, misid, output, vmin, resid_range):

    import dadi.DFE
    from src.Pdfs import get_dadi_pdf
    
    fs = dadi.Spectrum.from_file(fs)
    theta = ns_s * float(open(demo_popt, 'r').readline().rstrip().split()[-1])
    sele_popt = np.array(open(sele_popt, 'r').readline().rstrip().split()[1:], dtype=float)
    pdf = get_dadi_pdf(pdf)
    if pdf2 != None:
        pdf2 = get_dadi_pdf(pdf2)

    ns = fs.sample_sizes
    # Integrate over a range of gammas
    pts_l = [ns[0]+10, ns[0]+20, ns[0]+30]
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
        dadi.Plotting.plot_1d_comp_multinom(model, fs)
    if len(ns) == 2:
        if projections == None: projections = [20, 20]
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_multinom(model, fs, vmin=vmin, resid_range=resid_range)
    fig.savefig(output)
