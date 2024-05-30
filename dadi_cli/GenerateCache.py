import dadi
import dadi.DFE as DFE
import pickle, glob
import numpy as np
from dadi_cli.Models import get_model
from dadi_cli.utilities import get_opts_and_theta, cache_pts_l_func


def generate_cache(
    func: callable,
    grids: list[int],
    popt: str,
    gamma_bounds: list[str],
    gamma_pts: int,
    additional_gammas: list[float],
    output: str,
    sample_sizes: list[int],
    cpus: int,
    gpus: int,
    cache_type: str
) -> None:
    """
    Generates caches of frequency spectra for DFE inference using demographic models.

    Parameters
    ----------
    func : callable
        A callable demographic model function from DFE.DemogSelModels.
    grids : list[int]
        Grid sizes for the frequency spectrum calculation.
    popt : str
        File name containing demographic parameters for inference.
    gamma_bounds : list[str]
        Range of population-scaled selection coefficients, specified as strings.
    gamma_pts : int
        Number of grid points for gamma integration.
    additional_gammas : list[float]
        List of additional gamma values to cache.
    output : str
        Output file name where the cache will be saved.
    sample_sizes : list[int]
        List of population sample sizes.
    cpus : int
        Number of CPUs to utilize.
    gpus : int
        Number of GPUs to utilize.
    cache_type : str
        Type of the cache.

    Raises
    ------
    ValueError
        If the number of populations is not 1 or 2.
        If the number of populations is 1 and `cache_type` is `cache2d`.

    """
    num_pop = len(sample_sizes)

    if (num_pop == 1) and (cache_type == 'cache2d'):
        raise ValueError("`cache2d` is only supported for JSFS from two populations.")

    if num_pop not in [1, 2]:
        raise ValueError(f"Invalid number of populations: {num_pop}. Only 1 or 2 are accepted.")

    if func is not getattr(DFE.DemogSelModels, 'equil'):
        popt, theta = get_opts_and_theta(popt, gen_cache=True)
    else:
        popt = []

    if grids == None:
        grids = cache_pts_l_func(sample_sizes)

    if cache_type == 'cache1d':
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
    elif cache_type == 'cache2d':
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

    if (spectra.spectra < 0).sum() > 0:
        print(
            f"!!!WARNING!!!\nPotentially large negative values!\nMost negative value is: {spectra.spectra.min()}"
            + f"\nSum of negative entries is: {np.sum(spectra.spectra[spectra.spectra<0])}\nIf negative values are very negative (<-1), rerun with larger values for --grids"
        )

    fid = open(output, "wb")
    pickle.dump(spectra, fid, protocol=2)
    fid.close()
