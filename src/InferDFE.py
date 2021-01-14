import dadi
import dadi.DFE
import dadi.NLopt_mod
import pickle, glob, nlopt
import os, time
import numpy as np
from Pdfs import get_dadi_pdf


def infer_dfe(opt, fs, cache1d, cache2d, sele_dist, sele_dist2, ns_s, #output,
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

    res = str(ll_model)
    for p in popt:
        res += "\t" + str(p)

    opt.append(res)

    #with open(output, 'w') as f:
    #    f.write(str(ll_model))
    #    for p in popt:
    #        f.write("\t")
    #        f.write(str(p))
    #    f.write("\n")

def infer_dfe_nuisance_1d(syn_fs, non_fs, pdf1d, cache1d, p0, lbounds, ubounds, 
                          fixed_params, misid, is_nlopt, output):

    def nuisance(params, ns, data, pdf, spectra, pts=None):

        shape = params[0]
        scale = params[1]
        ratio = params[2]

        bneu = 1.0 / np.arange(len(data[0]))
        bsel = spectra.integrate([shape, scale], ns, pdf, theta=ratio)

        r = (data[0,:]+data[1,:]) / (bneu+bsel)
        mneu = r * bneu
        msel = r * bsel.data

        rneu_1 = data[0,1]/bneu[1]
        rsel_1 = data[1,1]/bsel[1]

        mneu[1] = rneu_1 * bneu[1]
        msel[1] = rsel_1 * bsel[1]
        
        model = dadi.Spectrum([mneu, msel])
        model.mask[:,0] = model.mask[:,-1] = True

        return model

    spectra = pickle.load(open(cache1d, 'rb'))
    syn_fs = dadi.Spectrum.from_file(syn_fs)
    non_fs = dadi.Spectrum.from_file(non_fs)
    data = dadi.Spectrum([syn_fs.data, non_fs.data])
    data.mask[:,0] = data.mask[:,-1] = True
    pdf = get_dadi_pdf(pdf1d)

    if misid:
        nuisance = dadi.Numerics.make_anc_state_misid_func(nuisance)

    p0 = dadi.Misc.perturb_params(p0, lower_bound=lbounds, upper_bound=ubounds)

    if is_nlopt:
        popt, LLopt_global, result_global = dadi.NLopt_mod.opt(p0, data, nuisance, pts=None,
                                                               lower_bound=lbounds, upper_bound=ubounds,
                                                               fixed_params=fixed_params, func_args=[data, pdf, spectra],
                                                               #verbose=0, algorithm=nlopt.LN_BOBYQA, maxeval=1000)
                                                               verbose=0, algorithm=nlopt.GN_MLSL_LDS, #maxeval=1000)
                                                               local_optimizer=nlopt.LN_BOBYQA, maxeval=1000)
    else:
        popt = dadi.Inference.optimize(p0, data, nuisance, pts=None, func_args=[data, pdf, spectra],  
                                       fixed_params=fixed_params, lower_bound=lbounds, upper_bound=ubounds, verbose=0, 
                                       maxiter=1000, multinom=False)

    shape = popt[0]
    scale = popt[1]
    ratio = popt[2]

    bneu = 1.0 / np.arange(len(data[0]))
    bsel = spectra.integrate([shape, scale], None, pdf, theta=ratio)
    r = (data[0,:]+data[1,:]) / (bneu+bsel)
    mneu = r * bneu
    msel = r * bsel.data

    theta = np.mean(r[1:-1])
    norm = np.linalg.norm(r[1:-1])

    rneu_1 = data[0,1]/bneu[1]
    rsel_1 = data[1,1]/bsel[1]

    mneu[1] = rneu_1 * bneu[1]
    msel[1] = rsel_1 * bsel[1]

    #print(str(r[1]) + "\t" + str(rneu_1) + "\t" + str(rsel_1))

    model = dadi.Spectrum([mneu, msel])
    model.mask[:,0] = model.mask[:,-1] = True

    ll_model = dadi.Inference.ll_multinom(model, data)

    results = str(ll_model) + "\t" + str(shape) + "\t" + str(scale) + "\t" + str(ratio) + "\t" + str(theta) + "\t" + str(norm)
    if output != None:
        with open(output, 'w') as f:
            f.write(results + "\n")
    else:
        print(results)
