import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from src.Models import get_dadi_model_func

def generate_cache(model, grids, popt,
                   gamma_bounds, gamma_pts, additional_gammas,
                   output, sample_sizes, mp, cuda, single_gamma):

    if cuda:
        dadi.cuda_enabled(True)

    func = get_dadi_model_func(model, True, single_gamma)
    if grids == None:
        grids = [sample_sizes[0]+10, sample_sizes[0]+20, sample_sizes[0]+30]

    if single_gamma:
       spectra = DFE.Cache1D(popt, sample_sizes, func, pts_l=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    elif (model == 'equil') or (model == 'two_epoch') or (model == 'three_epoch'):
       spectra = DFE.Cache1D(popt, sample_sizes, func, pts_l=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp) 
    else:
       spectra = DFE.Cache2D(popt, sample_sizes, func, pts=grids, additional_gammas=additional_gammas, gamma_bounds=gamma_bounds, gamma_pts=gamma_pts, mp=mp)

    fid = open(output, 'wb')
    pickle.dump(spectra, fid, protocol=2)
    fid.close()
