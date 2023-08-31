import dadi
import dadi.Godambe
import dadi.DFE as DFE
import glob, pickle
import numpy as np
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import get_opts_and_theta, convert_to_None


def godambe_stat_demograpy(
    fs, func, grids, output, bootstrap_dir, demo_popt, fixed_params, nomisid, logscale, eps_l
):
    """
    Description:
        Godambe statistics for demographic inference.

    Arguments:
        fs str: Name of the file containing frequency spectrum from dadi.
        func function: Function for modeling demography.
        grids tuple: Grid sizes for modeling.
        output str: Name of the output file.
        bootstrap_dir str: Name of the directory containing bootstrapped frequency spectra.
        demo_popt str: Name of the file containg the best-fit demographic parameters.
        fixed_params list: List of the fixed parameters.
        nomisid bool: If False, add a parameter for modeling ancestral state misidentification when data are polarized.
        logscale bool: If True, calculate statistics using log scale.
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

    f = open(output, "w")
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
    f.close()


def godambe_stat_dfe(
    fs,
    cache1d,
    cache2d,
    sele_dist,
    sele_dist2,
    output,
    bootstrap_syn_dir,
    bootstrap_non_dir,
    dfe_popt,
    fixed_params,
    nomisid,
    logscale,
    eps_l,
):
    """
    Description:
        Godambe statistics for DFE inference.

    Argument:
        fs str: Name of the file containing frequency spectrum from dadi.
        cache1d str: Name of the file containing 1d frequency spectra cache from dadi.
        cache2d str: Name of the file containing 2d frequency spectra cache from dadi.
        sele_dist str: Name of the 1d PDF for modeling DFE.
        sele_dist2 str: Name of the 2d PDF for modeling DFE.
        output str: Name of the output file.
        bootstrap_syn_dir str: Name of the directory containing bootstrapped frequency spectra for synonymous mutations.
        bootstrap_non_dir str: Name of the directory containing bootstrapped frequency spectra for non-synonymous mutations.
        dfe_popt str: Name of the file containing the best-fit DFE parameters.
        fixed_params list: List of the fixed parameters.
        nomisid bool: If False, add a parameter for modeling ancestral state misidentification when data are polarized.
        logscale bool: If True, calculate statistics using log scale.
    """
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

    if cache1d != None:
        s1 = pickle.load(open(cache1d, "rb"))
        sfunc = s1.integrate
    if cache2d != None:
        s2 = pickle.load(open(cache2d, "rb"))
        sfunc = s2.integrate

    if sele_dist2 != None:
        sele_dist2 = get_dadi_pdf(sele_dist2)
    if sele_dist != None:
        sele_dist = get_dadi_pdf(sele_dist)
    else:
        sele_dist = sele_dist2

    if (cache1d != None) and (cache2d != None):
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

    elif (cache1d != None) or (cache2d != None):
        if not nomisid:
            sfunc = dadi.Numerics.make_anc_state_misid_func(sfunc)

        def func(free_params, ns, pts):
            params = _convert_free_params(free_params, fixed_params)
            return sfunc(params, None, sele_dist, theta, None, exterior_int=True)

    f = open(output, "w")
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
    f.close()


# Because we don't want confidence intervals estimated
# on fixed parameters, we find the free parameters
# that we will pass into Godambe.
def _free_params(dfe_popt, fixed_params):
    """
    Description:
        Helper function for finding the free parameters for Godambe.

    Arguments:
        dfe_popt list: List of the best-fit parameters for DFE inference.
        fixed_params list: List of the fixed parameters.

    Returns:
        free_params list: List of the free parameters.
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
def _convert_free_params(free_params, fixed_params):
    """
    Description:
        Helper function for recreating the optimal parameters.

    Arguments:
        free_params list: List of the free parameters.
        fixed_params list: List of the fixed parameters.

    Returns:
        params list: List of the optimal parameters.
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
