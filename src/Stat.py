import dadi
import dadi.Godambe
import dadi.DFE as DFE
import glob, pickle
import numpy as np
from Models import get_dadi_model_func
from Distribs import get_dadi_pdf

def godambe_stat(fs, model, cache1d, cache2d, sele_dist, sele_dist2, ns_s, output,
                 bootstrap_dir, pi, demo_popt, popt, popt_simple, misid, lrt, logscale):

    popt = np.array(open(popt, 'r').readline().rstrip().split(), dtype=float)
    theta = ns_s * float(open(demo_popt, 'r').readline().rstrip().split()[-1])

    if lrt:
        popt_simple = np.array(open(popt_simple, 'r').readline().rstrip().split(), dtype=float)

    fs = dadi.Spectrum.from_file(fs)
    fs_files = glob.glob(bootstrap_dir + '/*.fs')
    all_boot = []
    for f in fs_files:
        boot_fs = dadi.Spectrum.from_file(f)
        all_boot.append(boot_fs)

    if cache1d != None:
        s1 = pickle.load(open(cache1d, 'rb'))
    if cache2d != None:
        s2 = pickle.load(open(cache2d, 'rb'))

    if model != None:
        func = get_dadi_model_func(model)
    if sele_dist != None:
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 != None:
        sele_dist2 = get_dadi_pdf(sele_dist2)

    if (cache1d != None) and (cache2d != None):
        func = dadi.DFE.mixture
        if misid:
            func = dadi.Numerics.make_anc_state_misid_func(func)
        def model_func(params, ns, pts):
            # for mixture model, pin = [mu, sigma, p0, misid]
            # Add in gammapos parameter
            # params = np.concatenate([pin[0:2], [0], pin[2:]])
            return func(params, None, s1, s2, sele_dist, 
                        sele_dist2, theta, None, exterior_int=True)

    boot_theta_adjusts = [b.sum()/fs.sum() for b in all_boot]
    if lrt:
        ll_complex = popt[0]
        ll_simple = popt_simple[0]
        adj = dadi.Godambe.LRT_adjust(model_func, [], all_boot, popt_simple[1:], fs,
                                      nested_indices=[pi-1], multinom=False, boot_theta_adjusts=boot_theta_adjusts)
        D_adj = adj*2*(ll_complex - ll_simple)
        pval = dadi.Godambe.sum_chi2_ppf(D_adj, weights=(0.5,0.5))
        
        with open(output, 'w') as f:
            f.write('Adjusted D statistic: {0}'.format(D_adj) + '\n') 
            f.write('p-value for rejecting the simple model: {0}'.format(pval) + '\n')
    else:
        uncerts_adj = dadi.Godambe.GIM_uncert(model_func, [], all_boot, popt[1:],
                                              fs, multinom=False, eps=1e-4, log=logscale,
                                              boot_theta_adjusts=boot_theta_adjusts)

        with open(output, 'w') as f:
            f.write('Estimated 95% uncerts (theta adj): {0}'.format(1.96*uncerts_adj) + '\n')
            if logscale:
                f.write('Lower bounds of 95% confidence interval : {0}'.format(np.exp(np.log(popt[1:])-1.96*uncerts_adj)) + '\n')
                f.write('Upper bounds of 95% confidence interval : {0}'.format(np.exp(np.log(popt[1:])+1.96*uncerts_adj)) + '\n')
            else:
                f.write('Lower bounds of 95% confidence interval : {0}'.format(popt[1:]-1.96*uncerts_adj) + '\n')
                f.write('Upper bounds of 95% confidence interval : {0}'.format(popt[1:]+1.96*uncerts_adj) + '\n')
