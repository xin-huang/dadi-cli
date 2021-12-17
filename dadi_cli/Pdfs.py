import dadi.DFE as DFE


def get_dadi_pdf(pdf):
    """
    Description:
        Obtains a built-in probability density function for
        modeling distribution of fitness effects in dadi.

    Arguments:
        pdf string: Name of the probability density function.

    Returns:
        func DFE.PDFs: PDF for modeling. 
    """
    if pdf == "beta":
        func = DFE.PDFs.beta
    elif pdf == "biv_ind_gamma":
        func = DFE.PDFs.biv_ind_gamma
    elif pdf == "biv_lognormal":
        func = DFE.PDFs.biv_lognormal
    elif pdf == "exponential":
        func = DFE.PDFs.exponential
    elif pdf == "gamma":
        func = DFE.PDFs.gamma
    elif pdf == "lognormal":
        func = DFE.PDFs.lognormal
    elif pdf == "normal":
        func = DFE.PDFs.normal
    elif "mixture" in pdf:
        func = DFE.mixture
    else:
        raise Exception("Probability density function " + pdf + " is not available!")

    return func


def get_dadi_pdf_params(pdf):
    """
    Description:
        Obtains a list of parameters for a given built-in probability density function
        in dadi.

    Arguments:
        pdf string: Name of the probability density function.

    Returns:
        params list: List of parameters.
    """
    if pdf == "beta":
        params = ["alpha", "beta"]
    elif pdf == "biv_sym_ind_gamma":
        params = ["shape", "scale"]
    elif pdf == "biv_asym_ind_gamma":
        params = ["shape1", "scale1", "shape2", "scale2"]
    elif pdf == "biv_sym_lognormal":
        params = ["log_mu", "log_sigma", "rho"]
    elif pdf == "biv_asym_lognormal":
        params = ["log_mu1", "log_sigma1", "log_mu2", "log_sigma2", "rho"]
    elif pdf == "exponential":
        params = ["scale"]
    elif pdf == "gamma":
        params = ["shape", "scale"]
    elif pdf == "lognormal":
        params = ["log_mu", "log_sigma"]
    elif pdf == "mixture_gamma":
        params = ["shape", "scale", "w"]
    elif pdf == "mixture_lognormal":
        params = ["log_mu", "log_sigma", "rho", "w"]
    elif pdf == "normal":
        params = ["mu", "sigma"]
    else:
        raise Exception("Probability density function " + pdf + " is not available!")

    return params


def print_available_pdfs():
    """
    Description:
        Prints out available built-in probability density functions in dadi.
    """
    print("Available probability density functions:")
    print("- beta")
    print("- biv_ind_gamma")
    print("- biv_lognormal")
    print("- exponential")
    print("- gamma")
    print("- lognormal")
    print("- normal")
    print("- mixture")


def print_pdf_details(pdf_name):
    """
    Description:
        Prints out the details of a given built-in probability density function
        in dadi.

    Arguments:
        pdf_name string: Name of the probability density function.
    """

    beta = """
        Beta probability density function.

        params = [alpha, beta]
    """
    biv_ind_gamma = """
        Bivariate independent gamma probability density function.

        If len(params) == 2, then params = [alpha, beta] by assuming alpha and beta are equal in the two populations
        If len(params) == 4, then params = [alpha1, alpha2, beta1, beta2]
        If len(params) == 3 or 5, then the last parameter is ignored
    """
    biv_lognormal = """
        Bivariate lognormal probability density function.

        If len(params) == 3, then params = [mu, sigma, rho] by assuming mu and sigma are equal in the two populations
        If len(params) == 5, then params = [mu1, mu2, sigma1, sigma2, rho]
    """
    exponential = """
        Exponential probability density function.

        params = [scale]
    """
    gamma = """
        Gamma probability density function.

        params = [alpha, beta] = [shape, scale]
    """
    lognormal = """
        Lognormal probability density function.

        params = [log_mu, log_sigma]
    """
    normal = """
        Normal probability density function.

        params = [mu, sigma]
    """
    mixture = """
        Weighted summation of 1d and 2d distributions that share parameters.
        The 1d distribution is equivalent to assuming selection coefficients are
        perfectly correlated.

        params: Parameters for potential optimization.
                It is assumed that last parameter is the weight for the 2d dist.
                The second-to-last parameter is assumed to be the correlation
                    coefficient for the 2d distribution.
                The remaining parameters as assumed to be shared between the
                    1d and 2d distributions.
    """

    if pdf_name == "beta":
        print("- beta:\n" + beta)
    elif pdf_name == "biv_ind_gamma":
        print("- biv_ind_gamma:\n" + biv_ind_gamma)
    elif pdf_name == "biv_lognormal":
        print("- biv_lognormal:\n" + biv_lognormal)
    elif pdf_name == "exponential":
        print("- exponential:\n" + exponential)
    elif pdf_name == "gamma":
        print("- gamma:\n" + gamma)
    elif pdf_name == "lognormal":
        print("- lognormal:\n" + lognormal)
    elif pdf_name == "normal":
        print("- normal:\n" + normal)
    elif pdf_name == "mixture":
        print("- mixture:\n" + mixture)
    else:
        raise Exception(
            "Probability density function " + pdf_name + " is not available!"
        )
