import dadi
import dadi.DFE
import dadi.NLopt_mod
import pickle, glob, nlopt
import os, time
import numpy as np
from src.Pdfs import get_dadi_pdf


def infer_dfe(fs, cache1d, cache2d, sele_dist, sele_dist2, ns_s,
              popt, p0, upper_bounds, lower_bounds, fixed_params, misid, cuda):

    ts = time.time()
    seed = int(ts) + int(os.getpid())
    np.random.seed(seed)

    fs = dadi.Spectrum.from_file(fs)

    popt = np.array(open(popt, 'r').readline().rstrip().split(), dtype=float)
    theta = ns_s * popt[-1]

    if cache1d != None:
        spectra1d = pickle.load(open(cache1d, 'rb'))
        func = spectra1d.integrate
    if cache2d != None:
        spectra2d = pickle.load(open(cache2d, 'rb'))
        func = spectra2d.integrate
   
    if sele_dist != None: 
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 != None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if (sele_dist == None) and (sele_dist2 != None):
        sele_dist = sele_dist2
    
    if (cache1d != None) and (cache2d != None):
        func = dadi.DFE.Cache2D_mod.mixture
        func_args = [spectra1d, spectra2d, sele_dist, sele_dist2, theta]
    else:
        func_args = [sele_dist, theta]
        
    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    # Fit a DFE to the data
    # Initial guess and bounds
    p0 = dadi.Misc.perturb_params(p0, lower_bound=lower_bounds, upper_bound=upper_bounds)
    popt = dadi.Inference.optimize_log(p0, fs, func, pts=None,
                                       func_args=func_args, fixed_params=fixed_params,
                                       lower_bound=lower_bounds, upper_bound=upper_bounds,
                                       verbose=0, maxiter=200, multinom=False)

    #print('Optimized parameters: {0}'.format(popt))

    # Get expected SFS for MLE
    if (cache1d != None) and (cache2d != None):
        model = func(popt, None, spectra1d, spectra2d, sele_dist, sele_dist2, theta, None)
    else:
        model = func(popt, None, sele_dist, theta, None)
    # Likelihood of the data given the model AFS.
    ll_model = dadi.Inference.ll_multinom(model, fs)
    #print('Maximum log composite likelihood: {0}'.format(ll_model))

    with open(output, 'w') as f:
        f.write(str(ll_model))
        for p in popt:
            f.write("\t")
            f.write(str(p))
        f.write("\n")
