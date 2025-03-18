import dadi, importlib, os, sys
import dadi.DFE as DFE
from inspect import getmembers, isfunction


def get_dadi_pdf(
    pdf: str,
    pdf_file: str = None
    ) -> tuple[callable, list[str]]:
    """
    Obtains a built-in probability density function for modeling the distribution
    of fitness effects in dadi.

    Parameters
    ----------
    pdf : str
        Name of the probability density function.

    Returns
    -------
    callable
        The probability density function from DFE.PDFs module.

    Raises
    ------
    ValueError
        If the specified probability density function name is not recognized.

    """
    if pdf_file is not None:
        # If the user has the model folder in their PATH
        #try:
        #    func = getattr(importlib.import_module(model_file), model_name)
        # If the user does not have the model folder in their PATH we add it
        # This currently can mess with the User's PATH while running dadi-cli
        #except:
        #    model_file = os.path.abspath(model_file)
        #    model_path = os.path.dirname(model_file)
        #    model_file = os.path.basename(model_file)
        #    model_file = os.path.splitext(model_file)[0]
        #    sys.path.append(model_path)
        #    func = getattr(importlib.import_module(model_file), model_name)
        try:
            module_name = os.path.splitext(os.path.basename(pdf_file))[0]
            model_path = os.path.dirname(os.path.abspath(pdf_file))
            sys.path.append(model_path)
            func = getattr(importlib.import_module(module_name), pdf)
        except ImportError as e:
            raise ImportError(f"Failed to import module: {pdf_file}") from e
    elif pdf == "beta":
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
        raise ValueError("Probability density function " + pdf + " is not available!")

    if pdf_file is not None:
        return func, func.__param_names__
    else:
        return func, None


def get_dadi_pdf_params(pdf: str) -> list[str]:
    """
    Obtains a list of parameters for a given built-in probability density function in dadi.

    Parameters
    ----------
    pdf : str
        Name of the probability density function.

    Returns
    -------
    list[str]
        List of parameter names associated with the specified PDF.

    Raises
    ------
    ValueError
        If the specified probability density function name is not recognized.

    """
    params_dict = {
        "beta": ["alpha", "beta"],
        "biv_sym_ind_gamma": ["shape", "scale"],
        "biv_asym_ind_gamma": ["shape1", "scale1", "shape2", "scale2"],
        "biv_sym_lognormal": ["log_mu", "log_sigma", "rho"],
        "biv_asym_lognormal": ["log_mu1", "log_sigma1", "log_mu2", "log_sigma2", "rho"],
        "exponential": ["scale"],
        "gamma": ["shape", "scale"],
        "lognormal": ["log_mu", "log_sigma"],
        "mixture_gamma": ["shape", "scale", "w"],
        "mixture_lognormal": ["log_mu", "log_sigma", "rho", "w"],
        "normal": ["mu", "sigma"]
    }
    
    if pdf in params_dict:
        return params_dict[pdf]
    else:
        raise ValueError(f"Probability density function '{pdf}' is not available!")

    return params


def print_available_pdfs() -> None:
    """
    Prints out available built-in probability density functions in dadi.
    
    This function lists all the PDFs that can be used with the dadi library for demographic modeling,
    providing a quick reference for users to know what options are available.

    """
    pdfs = [
        "beta", "biv_ind_gamma", "biv_lognormal", 
        "exponential", "gamma", "lognormal", 
        "normal", "mixture"
    ]

    print("Available probability density functions:")
    for pdf in pdfs:
        print(f"- {pdf}")


def print_pdf_details(pdf_name: str) -> None:
    """
    Prints out the details of a given built-in probability density function in dadi.

    Parameters
    ----------
    pdf_name : str
        Name of the probability density function.

    Raises
    ------
    ValueError
        If the specified probability density function name is not recognized.

    """
    pdf_details = {
        "beta" : """
            Beta probability density function.

            params = [alpha, beta]
        """,

        "biv_ind_gamma" : """
            Bivariate independent gamma probability density function.

            If len(params) == 2, then params = [alpha, beta] by assuming alpha and beta are equal in the two populations
            If len(params) == 4, then params = [alpha1, alpha2, beta1, beta2]
            If len(params) == 3 or 5, then the last parameter is ignored
        """,

        "biv_lognormal" : """
            Bivariate lognormal probability density function.

            If len(params) == 3, then params = [mu, sigma, rho] by assuming mu and sigma are equal in the two populations
            If len(params) == 5, then params = [mu1, mu2, sigma1, sigma2, rho]
        """,

        "exponential" : """
            Exponential probability density function.

            params = [scale]
        """,

        "gamma" : """
            Gamma probability density function.

            params = [alpha, beta] = [shape, scale]
        """,

        "lognormal" : """
            Lognormal probability density function.

            params = [log_mu, log_sigma]
        """,

        "normal" : """
            Normal probability density function.

            params = [mu, sigma]
        """,

        "mixture" : """
            Weighted summation of 1d and 2d distributions that share parameters.
            The 1d distribution is equivalent to assuming selection coefficients are
            perfectly correlated.

            params: Parameters for potential optimization.
                    It is assumed that last parameter is the weight for the 2d dist.
                    The second-to-last parameter is assumed to be the correlation
                        coefficient for the 2d distribution.
                    The remaining parameters as assumed to be shared between the
                        1d and 2d distributions.
        """,
    }

    if pdf_name in pdf_details:
        print(f"- {pdf_name}:\n{pdf_details[pdf_name]}")
    else:
        raise ValueError(f"Probability density function '{pdf_name}' is not available!")
