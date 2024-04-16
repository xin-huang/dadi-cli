import dadi
import dadi.Godambe
import dadi.DFE as DFE
import glob, pickle
import numpy as np
from typing import Optional
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import get_opts_and_theta, convert_to_None


def godambe_stat_demograpy(
    fs: str, 
    func: callable, 
    grids: tuple[int], 
    output: str, 
    bootstrap_dir: str, 
    demo_popt: str, 
    fixed_params: list[Optional[float]], 
    nomisid: bool, 
    logscale: bool, 
    eps_l: list[float],
) -> None:
    """
    Calculates Godambe statistics for demographic inference, estimating parameter uncertainties 
    using bootstrapped frequency spectra.

    Parameters
    ----------
    fs : str
        Path to the file containing the frequency spectrum.
    func : callable
        Demographic model function to be used for simulations.
    grids : tuple[int]
        Grid sizes for numerical integration.
    output : str
        File path for writing the output results.
    bootstrap_dir : str
        Directory containing bootstrapped frequency spectra files.
    demo_popt : str
        Path to the file containing the best-fit demographic parameters.
    fixed_params : list[Optional[float]]
        List of fixed parameters where `None` indicates parameters to be inferred.
    nomisid : bool
        If False, includes modeling of ancestral state misidentification.
    logscale : bool
        If True, statistics are calculated on a logarithmic scale.
    eps_l : list[float]
        List of epsilon values for numerical differentiation when calculating the Godambe matrix.

    """
    # We want the best fits from the demograpic fit.
    # We set the second argument to true, since we want
    # all the parameters from the file.
    demo_popt, _ = get_opts_and_theta(demo_popt)
    fixed_params = convert_to_None(fixed_params, len(demo_popt))
    free_params = _free_params(demo_popt, fixed_params)
    fs = dadi.Spectrum.from_file(fs)
    fs_boot_files = glob.glob(bootstrap_dir + "/*.fs")
    all_boot = []
    for f in fs_boot_files:
        boot_fs = dadi.Spectrum.from_file(f)
        all_boot.append(boot_fs)

    if not nomisid:
        func = dadi.Numerics.make_anc_state_misid_func(func)

    func_ex = dadi.Numerics.make_extrap_func(func)

    def gfunc(free_params, ns, pts):
        params = _convert_free_params(free_params, fixed_params)
        return func_ex(params, ns, pts)

    with open(output, "w") as f:
        for eps in eps_l:
            popt = np.array(free_params)
            uncerts_adj = dadi.Godambe.GIM_uncert(
                gfunc, grids, all_boot, popt, fs, multinom=True, log=logscale, eps=eps
            )
            # The uncertainty for theta is predicted, so we slice the
            # the uncertainties for just the parameters.
            uncerts_adj = uncerts_adj[:-1]

            f.write(
                "Estimated 95% uncerts (theta adj), with step size "
                + str(eps)
                + "): {0}".format(1.96 * uncerts_adj)
                + "\n"
            )
            if logscale:
                f.write(
                    "Lower bounds of 95% confidence interval : {0}".format(
                        np.exp(np.log(popt) - 1.96 * uncerts_adj)
                    )
                    + "\n"
                )
                f.write(
                    "Upper bounds of 95% confidence interval : {0}".format(
                        np.exp(np.log(popt) + 1.96 * uncerts_adj)
                    )
                    + "\n\n"
                )
            else:
                f.write(
                    "Lower bounds of 95% confidence interval : {0}".format(
                         popt - 1.96 * uncerts_adj
                    )
                    + "\n"
                )
                f.write(
                    "Upper bounds of 95% confidence interval : {0}".format(
                        popt + 1.96 * uncerts_adj
                    )
                    + "\n\n"
                )


def godambe_stat_dfe(
    fs: str,
    cache1d: str,
    cache2d: str,
    sele_dist: str,
    sele_dist2: str,
    output: str,
    bootstrap_syn_dir: str,
    bootstrap_non_dir: str,
    dfe_popt: str,
    fixed_params: list[Optional[float]],
    nomisid: bool,
    logscale: bool,
    eps_l: list[float],
) -> None:
    """
    Calculates Godambe statistics for DFE inference using cached frequency spectra and bootstrapping.

    Parameters
    ----------
    fs : str
        Path to the file containing the frequency spectrum.
    cache1d : str
        Path to the file containing 1D frequency spectra cache.
    cache2d : str
        Path to the file containing 2D frequency spectra cache.
    sele_dist : str
        Name of the 1D PDF for modeling DFE.
    sele_dist2 : str
        Name of the 2D PDF for modeling DFE.
    output : str
        File path for the output results.
    bootstrap_syn_dir : str
        Directory containing bootstrapped frequency spectra for synonymous mutations.
    bootstrap_non_dir : str
        Directory containing bootstrapped frequency spectra for non-synonymous mutations.
    dfe_popt : str
        Path to the file containing the best-fit DFE parameters.
    fixed_params : list[Optional[float]]
        List of fixed parameters where `None` indicates parameters to be inferred.
    nomisid : bool
        If False, includes a parameter for modeling ancestral state misidentification.
    logscale : bool
        If True, calculations are done on a logarithmic scale.
    eps_l : list[float]
        List of epsilon values for numerical differentiation when calculating the Godambe matrix.

    Raises
    ------
    ValueError
        If neither `cache1d` nor `cache2d` is provided, an error is raised.

    """
    if not cache1d and not cache2d:
        raise ValueError("At least one of cache1d or cache2d must be provided.")

    dfe_popt, theta = get_opts_and_theta(dfe_popt)
    fixed_params = convert_to_None(fixed_params, len(dfe_popt))
    free_params = _free_params(dfe_popt, fixed_params)

    fs = dadi.Spectrum.from_file(fs)
    non_fs_files = glob.glob(bootstrap_non_dir + "/*.fs")
    all_non_boot = []
    for f in non_fs_files:
        boot_fs = dadi.Spectrum.from_file(f)
        all_non_boot.append(boot_fs)
    syn_fs_files = glob.glob(bootstrap_syn_dir + "/*.fs")
    all_syn_boot = []
    for f in syn_fs_files:
        boot_fs = dadi.Spectrum.from_file(f)
        all_syn_boot.append(boot_fs)

    if cache1d is not None:
        s1 = pickle.load(open(cache1d, "rb"))
        sfunc = s1.integrate
    if cache2d is not None:
        s2 = pickle.load(open(cache2d, "rb"))
        sfunc = s2.integrate

    if sele_dist2 is not None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if sele_dist is not None:
        sele_dist = get_dadi_pdf(sele_dist)
    else:
        sele_dist = sele_dist2

    if (cache1d is not None) and (cache2d is not None):
        mfunc = dadi.DFE.mixture
        if not nomisid:
            mfunc = dadi.Numerics.make_anc_state_misid_func(mfunc)

        def func(free_params, ns, pts):
            # for mixture model, pin = [mu, sigma, p0, misid]
            # Add in gammapos parameter
            # fix rho=0
            params = _convert_free_params(free_params, fixed_params)
            return mfunc(
                params,
                None,
                s1,
                s2,
                sele_dist,
                sele_dist2,
                theta,
                None,
                exterior_int=True,
            )

    elif (cache1d is not None) or (cache2d is not None):
        if not nomisid:
            sfunc = dadi.Numerics.make_anc_state_misid_func(sfunc)

        def func(free_params, ns, pts):
            params = _convert_free_params(free_params, fixed_params)
            return sfunc(params, None, sele_dist, theta, None, exterior_int=True)

    with open(output, "w") as f:
        for eps in eps_l:
            free_params = np.array(free_params)
            boot_theta_adjusts = [b.sum() / fs.sum() for b in all_syn_boot]
            uncerts_adj = dadi.Godambe.GIM_uncert(
                func,
                [],
                all_non_boot,
                free_params,
                fs,
                multinom=False,
                log=logscale,
                eps=eps,
                boot_theta_adjusts=boot_theta_adjusts,
            )

            f.write(
                "Estimated 95% uncerts (theta adj), with step size "
                + str(eps)
                + "): {0}".format(1.96 * uncerts_adj)
                + "\n"
            )
            if logscale:
                f.write(
                    "Lower bounds of 95% confidence interval : {0}".format(
                        np.exp(np.log(free_params) - 1.96 * uncerts_adj)
                    )
                    + "\n"
                )
                f.write(
                    "Upper bounds of 95% confidence interval : {0}".format(
                        np.exp(np.log(free_params) + 1.96 * uncerts_adj)
                    )
                    + "\n\n"
                )
            else:
                f.write(
                    "Lower bounds of 95% confidence interval : {0}".format(
                        free_params - 1.96 * uncerts_adj
                    )
                    + "\n"
                )
                f.write(
                    "Upper bounds of 95% confidence interval : {0}".format(
                        free_params + 1.96 * uncerts_adj
                    )
                    + "\n\n"
                )


# Because we don't want confidence intervals estimated
# on fixed parameters, we find the free parameters
# that we will pass into Godambe.
def _free_params(
    dfe_popt: list[float], 
    fixed_params: list[Optional[float]]
) -> list[float]:
    """
    Identifies and returns the free parameters for Godambe statistics calculation
    based on a list of best-fit parameters and a corresponding list of fixed indicators.

    Parameters
    ----------
    dfe_popt : list[float]
        List of the best-fit parameters for DFE inference.
    fixed_params : list[None]
        List indicating which parameters are fixed. `None` signifies that a parameter is free.

    Returns
    -------
    list[float]
        List of the free parameters, extracted from `dfe_popt` based on `fixed_params`.

    """
    free_params = []
    free_index = {}
    fixed_index = {}
    index_free_fixed = {}
    for i in range(len(fixed_params)):
        if fixed_params[i] == None:
            free_params.append(dfe_popt[i])
            free_index[i] = dfe_popt[i]
            index_free_fixed[i] = ("free", i)
        else:
            fixed_index[i] = fixed_params[i]
    return free_params


# Because the free params need to be passed into Godambe and func but also
# need to contain any fixed parameters used to generate the model or DFE
# we use the free parameters to recreate the optimal parameters.
def _convert_free_params(
    free_params: list[float], 
    fixed_params: list[Optional[float]]
) -> list[float]:
    """
    Recreates the complete list of optimal parameters by merging free parameters with their fixed counterparts.

    Parameters
    ----------
    free_params : list[float]
        List of the free parameters, these are the parameters that have been optimized.
    fixed_params : list[Optional[float]]
        List indicating which parameters are fixed (specified as actual values) or free (specified as None).

    Returns
    -------
    list[float]
        List of the optimal parameters, combining free and fixed parameters into a single parameter vector.

    """
    params = []
    ii = 0
    for i in range(len(fixed_params)):
        if fixed_params[i] == None:
            params.append(free_params[ii])
            ii += 1
        else:
            params.append(fixed_params[i])

    params = np.array(params)
    return params
