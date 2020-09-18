import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from Models import get_dadi_model_func

def generate_cache(model, grids, popt,
                   gamma_bounds, gamma_pts, additional_gammas,
                   output, sample_sizes, misid, mp):

    popt = np.array(open(popt, 'r').readline().rstrip().split()[1:-1], dtype=float)
    if misid:
        popt = popt[:-1]

    func, is_cache1d = get_dadi_model_func(model, True)
    if grids == None:
        grids = [sample_sizes[0]+10, sample_sizes[0]+20, sample_sizes[0]+30]

    if is_cache1d:
       spectra = DFE.Cache1D(list(popt), sample_sizes, func, pts_l=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    else:
       spectra = DFE.Cache2D(popt, sample_sizes, func, pts=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp)

    fid = open(output, 'wb')
    pickle.dump(spectra, fid, protocol=2)
    fid.close()
