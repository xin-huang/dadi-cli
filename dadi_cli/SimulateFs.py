import os, time, inspect
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.Pdfs import get_dadi_pdf_params
from dadi_cli.utilities import pts_l_func
import dadi


def simulate_demography(
    model: str, 
    model_file: str, 
    p0: list[float], 
    ns: int, 
    pts_l: tuple[int],
    misid: bool, 
    output: str, 
    inference_file: bool
) -> None:
    """
    Simulates frequency spectrum from a demographic model and optionally output inference files.

    Parameters
    ----------
    model : str
        Name of the demographic model.
    model_file : str
        Path and name of the file containing customized models.
    p0 : list[float]
        Initial parameter values for inference.
    ns : int
        Sample size.
    pts_l : tuple[int]
        Grid sizes for modeling. If None, a default is calculated based on ns.
    misid : bool
        If True, adds a parameter for modeling ancestral state misidentification.
    output : str
        Name of the output file.
    inference_file : bool
        If True, outputs the inference results to generate caches.

    """
    if pts_l is None:
        pts_l = pts_l_func(ns)
    # fs = dadi.Numerics.make_extrap_func(get_dadi_model_func(model, model_file))(popt, fs.sample_sizes, pts_l)*theta
    func, params = get_model(model, model_file)

    if misid:
        param_names = func.__param_names__
        func = dadi.Numerics.make_anc_state_misid_func(func)
        func.__param_names__ = param_names + ["misid"]
    func_ex = dadi.Numerics.make_extrap_func(func)
    fs = func_ex(p0, ns, pts_l)
    fs.to_file(output)

    if inference_file:
        with open(f"{output}.SimulateDM.pseudofit", "w") as fi:
            fi.write(
                "# Ran SimulateDM\n# This is a fake inference output results to generate caches\n# Log(likelihood)   "
                + "\t".join(func.__param_names__)
                + "\ttheta0\n"
                + "-0\t" + "\t".join([str(ele) for ele in p0]) + "\t1"
            )


def simulate_demes(
    demes_file: str, 
    ns: int, 
    pts_l: tuple[int], 
    pop_ids: list[str], 
    output: str,
) -> None:
    """
    Simulates frequency spectrum from a DEMES format file using `dadi`.

    Parameters
    ----------
    demes_file : str
        Path to the DEMES format file.
    ns : int
        Sample size for each population.
    pts_l : tuple[int]
        Grid sizes for numerical integration modeling. If None, which triggers automatic grid size determination based on `ns`.
    pop_ids : list[str]
        Names of the populations to be sampled within the DEMES model.
    output : str
        Path and name of the output file where the frequency spectrum is saved.

    """
    if pts_l is None:
        pts_l = pts_l_func(ns)

    fs = dadi.Spectrum.from_demes(
        demes_file, sampled_demes=pop_ids, sample_sizes=ns, pts=pts_l
    )

    fs.to_file(output)


def simulate_dfe(
    p0: list[str], 
    cache1d: dadi.DFE.Cache1D_mod, 
    cache2d: dadi.DFE.Cache2D_mod, 
    sele_dist: str, 
    sele_dist2: str, 
    ratio: float, 
    misid: bool, 
    output: str
) -> None:
    """
    Simulates frequency spectrum from a Distribution of Fitness Effects (DFE) model.

    Parameters
    ----------
    p0 : list[str]
        Initial parameter values for inference.
    cache1d : dadi.DFE.Cache1D_mod
        Caches of 1D frequency spectra for DFE inference.
    cache2d : dadi.DFE.Cache2D_mod
        Caches of 2D frequency spectra for DFE inference.
    sele_dist : str
        Name of the 1D Probability Density Function (PDF) for modeling DFEs.
    sele_dist2 : str
        Name of the 2D PDF for modeling DFEs.
    ratio : float
        Ratio of synonymous to non-synonymous mutations.
    misid : bool
        If True, adds a parameter for modeling ancestral state misidentification when data are polarized.
    output : str
        Name of the output file where the simulated frequency spectrum is saved.

    Raises
    ------
    ValueError
        If neither `cache1d` nor `cache2d` is provided, an error is raised.

    """
    if not cache1d and not cache2d:
        raise ValueError("At least one of cache1d or cache2d must be provided.")

    if cache1d is not None:
        func = cache1d.integrate
    if cache2d is not None:
        func = cache2d.integrate

    if sele_dist is not None:
        sele_dist = get_dadi_pdf(sele_dist)
    if sele_dist2 is not None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if (sele_dist is None) and (sele_dist2 is not None):
        sele_dist = sele_dist2

    if (cache1d is not None) and (cache2d is not None):
        func = dadi.DFE.Cache2D_mod.mixture
        func_args = [cache1d, cache2d, sele_dist, sele_dist2, ratio]
    else:
        func_args = [sele_dist, ratio]

    if misid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    print(p0, None, sele_dist, ratio, None)
    # Get expected SFS for MLE
    if (cache1d is not None) and (cache2d is not None):
        fs = func(p0, None, cache1d, cache2d, sele_dist, sele_dist2, ratio, None)
    else:
        fs = func(p0, None, sele_dist, ratio, None)
    fs.to_file(output)
