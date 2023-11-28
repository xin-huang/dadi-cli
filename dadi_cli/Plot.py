import dadi, pickle
import dadi.DFE
import numpy as np
import matplotlib.pyplot as plt
from dadi_cli.utilities import get_opts_and_theta
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import pts_l_func

fig = plt.figure(figsize=(8, 6))


def plot_single_sfs(fs, projections, output, vmin):
    """
    Description:
        Plots 1d or 2d frequency spectrum.

    Arguments:
        fs str: Name of the file containing frequency spectrum from dadi.
        projections list: Sample sizes after projection.
        output str: Name of the output file.
        vmin float: Minimum value in the colorbar.
    """
    fs = dadi.Spectrum.from_file(fs)
    if projections == None:
        projections = fs.sample_sizes
    fig = plt.figure(219033)
    if len(fs.sample_sizes) == 1:
        dadi.Plotting.plot_1d_fs(fs)
    if len(fs.sample_sizes) == 2:
        dadi.Plotting.plot_single_2d_sfs(fs, vmin=vmin)
    if len(fs.sample_sizes) > 2:
        raise Exception("dadi-cli does not support plotting a single fs with more than two populations")
    fig.savefig(output)


def plot_comparison(fs, fs2, projections, output, vmin, resid_range):
    """
    Description:
        Plots comparison between two frequence spectra.

    Arguments:
        fs str: Name of the file containing the first frequency spectrum from dadi.
        fs2 str: Name of the file containing the second frequency spectrum from dadi.
        projections list: Sample sizes after projection.
        output str: Name of the output file.
        vmin float: Minimum value in the colorbar.
        resid_range list: Range of the residuals.
    """
    fs = dadi.Spectrum.from_file(fs)
    fs2 = dadi.Spectrum.from_file(fs2)

    if projections == None:
        if fs.sample_sizes is not fs2.sample_sizes:
            projections = [min([fs.sample_sizes[i], fs2.sample_sizes[i]]) for i in range(len(fs.sample_sizes))]
        else:
            projections = fs.sample_sizes

    fig = plt.figure(219033)
    if len(fs.sample_sizes) == 1:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_1d_comp_Poisson(model=fs, data=fs2)
    if len(fs.sample_sizes) == 2:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_2d_comp_Poisson(
            model=fs, data=fs2, vmin=vmin, resid_range=resid_range
        )
    if len(fs.sample_sizes) == 3:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_3d_comp_Poisson(
            model=fs, data=fs2, vmin=vmin, resid_range=resid_range
        )
    if len(fs.sample_sizes) > 3:
        raise Exception("dadi-cli does not support comparing fs with more than three populations")
    fig.savefig(output)


def plot_fitted_demography(
    fs, func, popt, projections, nomisid, output, vmin, resid_range
):
    """
    Description:
        Plots frequency spectrum fitted to a demographic model.

    Arguments:
        fs str: Name of the file containing frequecy spectrum from dadi.
        model str: Name of the demographic model.
        popt str: Name of the file containing the best-fit demographic parameters.
        projections list: Sample sizes after projection.
        nomisid bool: If False, add a parameter for modeling ancestral state misidentification when data are polarized.
        output str: Name of the output file.
        vmin float: Minimum value in the colorbar.
        resid_range list: Range of the residuals.
    """

    popt, _ = get_opts_and_theta(popt)

    fs = dadi.Spectrum.from_file(fs)
    if not nomisid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    func_ex = dadi.Numerics.make_extrap_func(func)
    ns = fs.sample_sizes
    pts_l = pts_l_func(ns)

    model = func_ex(popt, ns, pts_l)

    fig = plt.figure(219033)
    if len(ns) == 1:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_1d_comp_multinom(model, fs)
    if len(ns) == 2:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_multinom(
            model, fs, vmin=vmin, resid_range=resid_range
        )
    if len(ns) == 3:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_3d_comp_multinom(
            model, fs, vmin=vmin, resid_range=resid_range
        )
    if len(ns) > 3:
        raise Exception("dadi-cli does not support comparing fs and model with more than three populations")
    fig.savefig(output)


def plot_fitted_dfe(
    fs,
    cache1d,
    cache2d,
    sele_popt,
    projections,
    pdf,
    pdf2,
    nomisid,
    output,
    vmin,
    resid_range,
):
    """
    Description:
        Plots frequency specturm fitted to a demographic model with a DFE.

    Arguments:
        fs str: Name of the file containing frequency spectrum from dadi.
        cache1d str: Name of the file containing 1d frequency spectra cache from dadi.
        cache2d str: Name of the file containing 2d frequency spectra cache from dadi.
        sele_popt str: Name of the file containing the best-fit DFE parameters.
        projections list: Sample sizes after projection.
        pdf str: Name of the 1d PDF for modeling DFE.
        pdf2 str: Name of the 2d PDF for modeling DFE.
        nomisid bool: If False, add a parameter for modeling ancestral state misidentification when data are polarized.
        output str: Name of the output file.
        vmin float: Minimum value in the colorbar.
        resid_range list: Range of the residuals.
    """
    sele_popt, theta = get_opts_and_theta(sele_popt)

    fs = dadi.Spectrum.from_file(fs)

    if pdf != None:
        pdf = get_dadi_pdf(pdf)
    if pdf2 != None:
        pdf2 = get_dadi_pdf(pdf2)
        if pdf == None:
            pdf = pdf2

    ns = fs.sample_sizes
    # Integrate over a range of gammas
    pts_l = pts_l_func(ns)
    if cache1d != None:
        spectra1d = pickle.load(open(cache1d, "rb"))
        func = spectra1d.integrate
    if cache2d != None:
        spectra2d = pickle.load(open(cache2d, "rb"))
        func = spectra2d.integrate
    if (cache1d != None) and (cache2d != None):
        func = dadi.DFE.mixture

    if not nomisid:
        func = dadi.Numerics.make_anc_state_misid_func(func)
    # Get expected SFS for MLE
    if (cache1d != None) and (cache2d != None):
        model = func(sele_popt, None, spectra1d, spectra2d, pdf, pdf2, theta, None)
    else:
        model = func(sele_popt, None, pdf, theta, None)

    fig = plt.figure(219033)
    if len(ns) == 1:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_1d_comp_Poisson(model, fs)
    if len(ns) == 2:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_Poisson(
            model, fs, vmin=vmin, resid_range=resid_range
        )
    if len(ns) == 3:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_3d_comp_Poisson(
            model, fs, vmin=vmin, resid_range=resid_range
        )
    if len(ns) > 3:
        raise Exception("dadi-cli does not support comparing fs and model with more than three populations")
    fig.savefig(output)


def plot_mut_prop(pdf, dfe_popt, output):
    """
    Description:
        Plots proportions of mutations with different selection coefficients given a DFE in 2Ns unit.

    Arguments:
        pdf: Type of the probability distribution for the best-fit DFE.
        dfe_popt str: Name of the file containing the best-fit DFE parameters.
        output str: Name of the output file.
    """
    from scipy import stats

    dfe_params, theta = get_opts_and_theta(dfe_popt)

    if pdf == 'beta':
        ps = stats.beta.cdf([1, 10, 100], dfe_params[0], dfe_params[1])
    elif pdf == 'exponential':
        ps = stats.expon.cdf([1, 10, 100], scale=dfe_params[0])
    elif pdf == 'gamma':
        ps = stats.gamma.cdf([1, 10, 100], dfe_params[0], scale=dfe_params[1])
    elif pdf == 'lognormal':
        ps = stats.lognorm.cdf([1, 10, 100], dfe_params[1], scale=np.exp(dfe_params[0]))
    elif pdf == 'normal':
        ps = stats.norm.cdf([1, 10, 100], loc=dfe_params[0], scale=dfe_params[1])
    else:
        raise Exception(f'The {pdf} distribution is NOT supported!')
    
    props = [ps[0], ps[1]-ps[0], ps[2]-ps[1], 1-ps[2]]
    
    fig = plt.figure(219033)
    plt.bar([0, 1, 2, 3], props, alpha=0.7)
    plt.ylabel("Proportion")
    plt.xlabel("2N|s|")
    plt.xticks(
        [0, 1, 2, 3],
        [
            "<1",
            "1–10",
            "10–100",
            ">100",
        ],
    )
    plt.grid(alpha=0.3)

    fig.savefig(output, bbox_inches="tight")
