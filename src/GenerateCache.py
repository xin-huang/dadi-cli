import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from src.Models import get_dadi_model_func

def generate_cache(model, grids, popt, misid,
                   gamma_bounds, gamma_pts, additional_gammas,
                   output, sample_sizes, mp, cuda, single_gamma):

    popt = _get_opt(popt, misid)

    if cuda:
        dadi.cuda_enabled(True)

    func = get_dadi_model_func(model, True, single_gamma)
    if grids == None:
        grids = [sample_sizes[0]+10, sample_sizes[0]+20, sample_sizes[0]+30]

    #print(grids)

    if single_gamma:
       spectra = DFE.Cache1D(popt, sample_sizes, func, pts_l=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    elif (model == 'equil') or (model == 'two_epoch') or (model == 'three_epoch'):
       spectra = DFE.Cache1D(popt, sample_sizes, func, pts_l=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    else:
       spectra = DFE.Cache2D(popt, sample_sizes, func, pts=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp)

    if (s.spectra<0).sum() > 0:
        print(
            '!!!WARNING!!!\nPotentially large negative values!\nMost negative value is: '+str(s.spectra.min())+
            '\nIf negative values are very negative (<-1), rerun with larger values for --grids'
            )

    fid = open(output, 'wb')
    pickle.dump(spectra, fid, protocol=2)
    fid.close()

def _get_opt(popt, misid):

    opts = []
    params = []
    fid = open(popt, 'r')
    for line in fid.readlines():
        if line.startswith('#'):
            if line.startswith('# L'): params.append(line.rstrip().split("\t"))
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

    # Get the optimization results with the maximum likelihood
    # The first parameter in the optimization results is the likelihood
    # The last parameter in the optimization results is theta
    # The misidentification is the second last parameter if exists
    if misid: 
        popt = opts[0][1:-2]
        params = params[0][1:-2]
    else: 
        popt = opts[0][1:-1]
        params = params[0][1:-1]

    print('The demographic parameters for generating the cache:')
    print("\t".join([str(_) for _ in params]))
    print("\t".join([str(_) for _ in popt]))
    
    return popt
