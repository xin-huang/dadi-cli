import dadi, pickle
import dadi.DFE
import numpy as np
import matplotlib.pyplot as plt
from dadi_cli.utilities import get_opts_and_theta
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf
from dadi_cli.utilities import pts_l_func


fig = plt.figure(figsize=(8, 6))


def plot_single_sfs(
    fs: str, 
    output: str, 
    vmin: float,
    show: bool = False,
    projections: list[int] = None,
) -> None:
    """
    Plots 1D, 2D, or 3D frequency spectrum based on the number of sample sizes in the given dadi Spectrum file.

    Parameters
    ----------
    fs : str
        Path to the file containing the frequency spectrum data from dadi.
    output : str
        File path where the plot will be saved. The format of the saved plot is determined by the extension of the file path.
    vmin : float
        Minimum value in the colorbar. This sets the lower limit for color scaling in 2D and 3D plots.
    show : bool, optional
        If True, the plot is displayed using matplotlib's plt.show(). If False (default), the plot is not displayed.
    projections : list[int], optional
        Sample sizes after projection which may be used to adjust plots. If not provided, the original sample sizes from the spectrum file are used.

    Raises
    ------
    AttributeError
        If an outdated version of dadi is used that does not support required plotting functions, specifically 3D plotting.
    ValueError
        If the number of sample sizes (populations) in the spectrum exceeds three, as plotting of more than three populations is not supported by dadi-cli.

    """
    fs = dadi.Spectrum.from_file(fs)
    if projections is None:
        projections = fs.sample_sizes
    if len(fs.sample_sizes) == 1:
        fig = plt.figure(219033)
        dadi.Plotting.plot_1d_fs(fs, show=show)
    if len(fs.sample_sizes) == 2:
        fig = plt.figure(219033)
        dadi.Plotting.plot_single_2d_sfs(fs, vmin=vmin)#, show=show)
    if len(fs.sample_sizes) == 3:
        try:
            fig = plt.figure(219033, figsize=(10,4))
            dadi.Plotting.plot_3d_pairwise(fs, vmin=vmin, show=show)
        except AttributeError:
            raise AttributeError("Update to dadi 2.3.3 to use plot_3d_pairwise function")
    if len(fs.sample_sizes) > 3:
        raise ValueError("dadi-cli does not support plotting a single fs with more than three populations")

    fig.savefig(output)


def plot_comparison(
    fs: str, 
    fs2: str, 
    projections: list[int], 
    output: str, 
    vmin: float, 
    resid_range: list[float], 
    show: bool = False
) -> None:
    """
    Plots a comparison between two frequency spectra from dadi, including their residuals.

    Parameters
    ----------
    fs : str
        Path to the file containing the first dadi frequency spectrum.
    fs2 : str
        Path to the file containing the second dadi frequency spectrum.
    projections : list[int]
        List of integers representing the sample sizes after projection. This is used to adjust the plots accordingly.
    output : str
        Path where the comparison plot will be saved. The file format is inferred from the file extension.
    vmin : float
        Minimum value for the colorbar. This parameter sets the lower limit of color scaling in the plots.
    resid_range : list[float]
        A list of two floats specifying the minimum and maximum values for the residuals colorbar.
    show : bool
        If True, the plot is displayed using matplotlib's plt.show(). If False (default), the plot is not displayed.

    Raises
    ------
    ValueError
        If comparison with more than three populations.

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
        dadi.Plotting.plot_1d_comp_Poisson(model=fs, data=fs2, show=show)
    if len(fs.sample_sizes) == 2:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_2d_comp_Poisson(
            model=fs, data=fs2, vmin=vmin, resid_range=resid_range, show=show
        )
    if len(fs.sample_sizes) == 3:
        fs = fs.project(projections)
        fs2 = fs2.project(projections)
        dadi.Plotting.plot_3d_comp_Poisson(
            model=fs, data=fs2, vmin=vmin, resid_range=resid_range, show=show
        )
    if len(fs.sample_sizes) > 3:
        raise ValueError("dadi-cli does not support comparing fs with more than three populations")
    fig.savefig(output)


def plot_fitted_demography(
    fs: str, 
    func: callable, 
    popt: str, 
    projections: list[int], 
    nomisid: bool, 
    output: str, 
    vmin: float, 
    resid_range: list[float],
    show: bool = False
) -> None: 
    """
    Plots a frequency spectrum from dadi fitted to a demographic model along with residuals.

    Parameters
    ----------
    fs : str
        Path to the file containing the dadi frequency spectrum.
    func : callable
        The demographic model function, which should accept demographic parameters and return a modeled frequency spectrum.
    popt : str
        Path to the file containing the best-fit parameters for the demographic model.
    projections : list[int]
        List of integers representing the sample sizes after projection, used to adjust the plots.
    nomisid : bool
        If True, ancestral state misidentification is considered in the modeling; if False, it is not.
    output : str
        Path where the comparison plot will be saved. The file format is inferred from the file extension.
    vmin : float
        Minimum value for the colorbar, setting the lower limit of color scaling in the plots.
    resid_range : list[float]
        A list of two floats specifying the minimum and maximum values for the residuals colorbar.
    show : bool, optional
        If True, the plot is displayed using matplotlib's plt.show(). Default: False.

    Raises
    ------
    ValueError
        If comparison with more than three populations.

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
        dadi.Plotting.plot_1d_comp_multinom(model, fs, show=show)
    if len(ns) == 2:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_2d_comp_multinom(
            model, fs, vmin=vmin, resid_range=resid_range, show=show
        )
    if len(ns) == 3:
        if projections == None:
            projections = ns
        fs = fs.project(projections)
        model = model.project(projections)
        dadi.Plotting.plot_3d_comp_multinom(
            model, fs, vmin=vmin, resid_range=resid_range, show=show
        )
    if len(ns) > 3:
        raise ValueError("dadi-cli does not support comparing fs and model with more than three populations")
    fig.savefig(output)


def plot_fitted_dfe(
    fs: str,
    cache1d: str,
    cache2d: str,
    sele_popt: str,
    projections: list[int],
    pdf: str,
    pdf2: str,
    nomisid: bool,
    output: str,
    vmin: float,
    resid_range: list[float],
    show: bool = False
):
    """
    Plots a frequency spectrum from dadi fitted to a demographic model with a Distribution of Fitness Effects (DFE).

    Parameters
    ----------
    fs : str
        Path to the file containing the dadi frequency spectrum.
    cache1d : str
        Path to the file containing 1D frequency spectra cache used for the DFE modeling.
    cache2d : str
        Path to the file containing 2D frequency spectra cache used for the DFE modeling.
    sele_popt : str
        Path to the file containing the best-fit DFE parameters.
    projections : list[int]
        List of integers representing the sample sizes after projection, used to adjust the plots.
    pdf : str
        Name of the 1D probability density function file for modeling the DFE.
    pdf2 : str
        Name of the 2D probability density function file for modeling the DFE.
    nomisid : bool
        If True, includes ancestral state misidentification in the modeling; if False, it does not.
    output : str
        Path where the comparison plot will be saved. The file format is inferred from the file extension.
    vmin : float
        Minimum value for the colorbar, setting the lower limit of color scaling in the plots.
    resid_range : list[float]
        A list of two floats specifying the minimum and maximum values for the residuals colorbar.
    show : bool, optional
        If True, the plot is displayed using matplotlib's plt.show(). Default: False.

    Raises
    ------
    ValueError
        If comparison with more than three populations.

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
        raise ValueError("dadi-cli does not support comparing fs and model with more than three populations")
    fig.savefig(output)


def plot_mut_prop(
    pdf: str, 
    dfe_popt: str, 
    output: str,
    show: bool = False
) -> None:
    """
    Plots proportions of mutations with different selection coefficients given a Distribution of Fitness Effects (DFE).

    Parameters
    ----------
    pdf : str
        Type of the probability distribution used to model the best-fit DFE. Examples include 'gamma', 'normal', etc.
    dfe_popt : str
        Path to the file containing the best-fit DFE parameters.
    output : str
        Path where the plot will be saved. The file format is inferred from the file extension.
    show : bool, optional
        If True, the plot is displayed using matplotlib's plt.show(). Default: False.

    Raises
    ------
    ValueError
        If `pdf` is not supported.

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
        raise ValueError(f'The {pdf} distribution is NOT supported!')
    
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

    if show: plt.show()

    fig.savefig(output, bbox_inches="tight")
