import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from dadi_cli.Models import get_model
from dadi_cli.utilities import get_opts_and_theta, cache_pts_l_func


def generate_cache(
    func,
    grids,
    popt,
    gamma_bounds,
    gamma_pts,
    additional_gammas,
    output,
    sample_sizes,
    cpus,
    gpus,
    dimensionality,
):
    """
    Description:
        Generates caches of frequency spectra for DFE inference.

    Arguments:
        func function: dadi demographic models.
        grids list: Grid sizes.
        popt str: Name of the file containing demographic parameters for the inference.
        gamma_bounds list: Range of population-scaled selection coefficients to cache.
        gamma_pts int: Number of gamma grid points over which to integrate.
        additional_gammas list: Additional positive population-scaled selection coefficients to cache for.
        output str: Name of the output file.
        sample_sizes list: Sample sizes of populations.
        cpus int: Number of CPUs to use in cache generation.
        gpus int: Number of GPUs to use in cache generation.
        dimensionality int: Dimensionality of the frequency spectrum.
    """

    if func is not getattr(DFE.DemogSelModels, 'equil'):
        popt, theta = get_opts_and_theta(popt, gen_cache=True)
    else:
        popt = []

    if grids == None:
        grids = cache_pts_l_func(sample_sizes)

    if dimensionality == 1:
        spectra = DFE.Cache1D(
            popt,
            sample_sizes,
            func,
            pts=grids,
            additional_gammas=additional_gammas,
            gamma_bounds=gamma_bounds,
            gamma_pts=gamma_pts,
            cpus=cpus,
            gpus=gpus
        )
    elif dimensionality == 2:
        spectra = DFE.Cache2D(
            popt,
            sample_sizes,
            func,
            pts=grids,
            additional_gammas=additional_gammas,
            gamma_bounds=gamma_bounds,
            gamma_pts=gamma_pts,
            cpus=cpus,
            gpus=gpus
        )
    else:
        raise ValueError("--dimensionality only accepts 1 or 2.")

    if (spectra.spectra < 0).sum() > 0:
        print(
            f"!!!WARNING!!!\nPotentially large negative values!\nMost negative value is: {spectra.spectra.min()}"
            + f"\nSum of negative entries is: {np.sum(spectra.spectra[spectra.spectra<0])}\nIf negative values are very negative (<-1), rerun with larger values for --grids"
        )

    fid = open(output, "wb")
    pickle.dump(spectra, fid, protocol=2)
    fid.close()
