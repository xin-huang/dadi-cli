import dadi
import dadi.Godambe
import dadi.DFE as DFE
import glob, pickle
import numpy as np
from src.Models import get_dadi_model_func
from src.Pdfs import get_dadi_pdf
from src.GenerateCache import _get_opt

def godambe_stat(fs, model, cache1d, cache2d, sele_dist, sele_dist2, ns_s, grids,
                 output, bootstrap_dir, demo_popt, dfe_popt, misid, logscale):
    print('\n'.join([str(ele) for ele in [fs, model, cache1d, cache2d, sele_dist, sele_dist2, ns_s, grids,
              output, bootstrap_dir, demo_popt, dfe_popt, misid, logscale]]))
    if demo_popt != None:
        demo_popt = _get_opt(demo_popt, False)
        print('\n'.join([str(ele) for ele in demo_popt]))
    if dfe_popt != None:
        dfe_popt = _get_opt(dfe_popt, False)
        #Make sure the BestFit from InferDFE inference always 
        theta = _get_theta(dfe_popt)

    fs = dadi.Spectrum.from_file(fs)
    fs_files = glob.glob(bootstrap_dir + '/*.fs')
    all_boot = []
    for f in fs_files:
        boot_fs = dadi.Spectrum.from_file(f)
        all_boot.append(boot_fs)

    if cache1d != None:
        s1 = pickle.load(open(cache1d, 'rb'))
        sfunc = s1.integrate
    if cache2d != None:
        s2 = pickle.load(open(cache2d, 'rb'))
        sfunc = s2.integrate
        
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
    elif (cache1d != None) or (cache2d != None):
        if misid:
            sfunc = dadi.Numerics.make_anc_state_misid_func(sfunc)
        def func(params, ns, pts):
            return sfunc(params, None, sele_dist, theta, None, exterior_int=True)

    if model != None:
        popt = np.array(demo_popt)#[1:-1]
        func_ex = dadi.Numerics.make_extrap_func(func)
        uncerts_adj = dadi.Godambe.GIM_uncert(func_ex, grids, all_boot, popt,
                                              fs, multinom=True, log=logscale)
        uncerts_adj = uncerts_adj[:-1]
    else:
        if (cache1d != None) and (cache2d != None):
            popt = np.array([dfe_popt[1], dfe_popt[2], dfe_popt[4], dfe_popt[5]])
        else:
            popt = dfe_popt[1:]
        boot_theta_adjusts = [b.sum()/fs.sum() for b in all_boot]
        uncerts_adj = dadi.Godambe.GIM_uncert(func, [], all_boot, popt,
                                              fs, multinom=False, log=logscale,
                                              boot_theta_adjusts=boot_theta_adjusts)

    print(uncerts_adj)
    with open(output, 'w') as f:
        f.write('Estimated 95% uncerts (theta adj): {0}'.format(1.96*uncerts_adj) + '\n')
        if logscale:
            f.write('Lower bounds of 95% confidence interval : {0}'.format(np.exp(np.log(popt)-1.96*uncerts_adj)) + '\n')
            f.write('Upper bounds of 95% confidence interval : {0}'.format(np.exp(np.log(popt)+1.96*uncerts_adj)) + '\n')
        else:
            f.write('Lower bounds of 95% confidence interval : {0}'.format(popt-1.96*uncerts_adj) + '\n')
            f.write('Upper bounds of 95% confidence interval : {0}'.format(popt+1.96*uncerts_adj) + '\n')


def _get_theta(popt):

    opts = []
    fid = open(popt, 'r')
    for line in fid.readlines():
        if line.startswith('#'):
            continue
        else:
            try:
                opts.append([float(_) for _ in line.rstrip().split()])
            except ValueError:
                pass
    fid.close()

    if len(opts) == 0:
        print('No optimization results found')
        return

    theta = opts[0][-1]

    return theta