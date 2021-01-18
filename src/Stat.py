import dadi
import dadi.Godambe
import dadi.DFE as DFE
import glob, pickle
import numpy as np
from src.Models import get_dadi_model_func
from src.Pdfs import get_dadi_pdf

def godambe_stat(fs, model, cache1d, cache2d, sele_dist, sele_dist2, ns_s, 
                 output, bootstrap_dir, demo_popt, popt, misid, logscale):

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
        if misid:
            func = dadi.Numerics.make_anc_state_misid_func(func)
    if sele_dist != None:
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 != None:
        sele_dist2 = get_dadi_pdf(sele_dist2)

    if (cache1d != None) and (cache2d != None):
        mfunc = dadi.DFE.mixture
        if misid:
            mfunc = dadi.Numerics.make_anc_state_misid_func(mfunc)
        def func(pin, ns, pts):
            # for mixture model, pin = [mu, sigma, p0, misid]
            # Add in gammapos parameter
            # fix rho=0
            params = np.concatenate([pin[0:2], [0], pin[2:]])
            return mfunc(params, None, s1, s2, sele_dist, 
                         sele_dist2, theta, None, exterior_int=True)

    boot_theta_adjusts = [b.sum()/fs.sum() for b in all_boot]
    p = np.array([popt[1], popt[2], popt[4], popt[5]])
    uncerts_adj = dadi.Godambe.GIM_uncert(func, [], all_boot, p,
                                          fs, multinom=False, log=logscale,
                                          boot_theta_adjusts=boot_theta_adjusts)

    with open(output, 'w') as f:
        f.write('Estimated 95% uncerts (theta adj): {0}'.format(1.96*uncerts_adj) + '\n')
        if logscale:
            f.write('Lower bounds of 95% confidence interval : {0}'.format(np.exp(np.log(p)-1.96*uncerts_adj)) + '\n')
            f.write('Upper bounds of 95% confidence interval : {0}'.format(np.exp(np.log(p)+1.96*uncerts_adj)) + '\n')
        else:
            f.write('Lower bounds of 95% confidence interval : {0}'.format(p-1.96*uncerts_adj) + '\n')
            f.write('Upper bounds of 95% confidence interval : {0}'.format(p+1.96*uncerts_adj) + '\n')
