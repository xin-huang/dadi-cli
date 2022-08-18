import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from dadi_cli.Models import get_model

def generate_cache(func, grids, popt,
                   gamma_bounds, gamma_pts, additional_gammas,
                   output, sample_sizes, mp, cuda, dimensionality):

    popt = _get_opt(popt)

    if cuda:
        dadi.cuda_enabled(True)

    if grids == None:
        grids = [sample_sizes[0]+10, sample_sizes[0]+20, sample_sizes[0]+30]

    if dimensionality == 1:
       spectra = DFE.Cache1D(popt, sample_sizes, func, pts=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    elif dimensionality == 2:
       spectra = DFE.Cache2D(popt, sample_sizes, func, pts=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp)
    else:
        raise ValueError("Incorrect value for --dimensionality")

    if (spectra.spectra<0).sum() > 0:
        print(
            f'!!!WARNING!!!\nPotentially large negative values!\nMost negative value is: {spectra.spectra.min()}'+
            f'\nSum of negative entries is: {np.sum(spectra.spectra[spectra.spectra<0])}\nIf negative values are very negative (<-1), rerun with larger values for --grids'
            )

    fid = open(output, 'wb')
    pickle.dump(spectra, fid, protocol=2)
    fid.close()

# This function is very similar to dadi_cli.utilities._get_opts_and_theta.
# However, because we want to always remove misid for cache generation
# We need a custom function.
def _get_opt(popt):

    opts = []
    params = []
    fid = open(popt, 'r')
    for line in fid.readlines():
        if line.startswith('#'):
            if line.startswith('# L'): params.extend(line.rstrip().split("\t"))
            continue
        else:
            try:
                opts.extend([float(_) for _ in line.rstrip().split()])
                break
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
    if 'misid' in params: 
        popt = opts[1:-2]
        params = params[1:-2]
    else: 
        popt = opts[1:-1]
        params = params[1:-1]

    print('The optimal parameters are:')
    print("\t".join([str(_) for _ in params]))
    print("\t".join([str(_) for _ in popt]))
    
    return popt
