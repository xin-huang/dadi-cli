import dadi
import dadi.DFE as DFE
import pytest
import numpy as np
from dadi_cli.Pdfs import (
    get_dadi_pdf,
    get_dadi_pdf_params,
    print_available_pdfs,
    print_pdf_details,
)


def test_get_dadi_pdf():
    assert get_dadi_pdf("beta") == DFE.PDFs.beta
    assert get_dadi_pdf("biv_ind_gamma") == DFE.PDFs.biv_ind_gamma
    assert get_dadi_pdf("biv_lognormal") == DFE.PDFs.biv_lognormal
    assert get_dadi_pdf("exponential") == DFE.PDFs.exponential
    assert get_dadi_pdf("gamma") == DFE.PDFs.gamma
    assert get_dadi_pdf("lognormal") == DFE.PDFs.lognormal
    assert get_dadi_pdf("normal") == DFE.PDFs.normal
    assert get_dadi_pdf("mixture") == DFE.mixture

    with pytest.raises(Exception) as e_info:
        get_dadi_pdf("haha")


def test_get_dadi_pdf_params():
    assert np.array_equal(get_dadi_pdf_params("beta"), ["alpha", "beta"])
    assert np.array_equal(get_dadi_pdf_params("biv_sym_ind_gamma"), ["shape", "scale"])
    assert np.array_equal(
        get_dadi_pdf_params("biv_asym_ind_gamma"),
        ["shape1", "scale1", "shape2", "scale2"],
    )
    assert np.array_equal(
        get_dadi_pdf_params("biv_sym_lognormal"), ["log_mu", "log_sigma", "rho"]
    )
    assert np.array_equal(
        get_dadi_pdf_params("biv_asym_lognormal"),
        ["log_mu1", "log_sigma1", "log_mu2", "log_sigma2", "rho"],
    )
    assert np.array_equal(get_dadi_pdf_params("exponential"), ["scale"])
    assert np.array_equal(get_dadi_pdf_params("gamma"), ["shape", "scale"])
    assert np.array_equal(get_dadi_pdf_params("lognormal"), ["log_mu", "log_sigma"])
    assert np.array_equal(get_dadi_pdf_params("normal"), ["mu", "sigma"])
    assert np.array_equal(
        get_dadi_pdf_params("mixture_lognormal"), ["log_mu", "log_sigma", "rho", "w"]
    )
    assert np.array_equal(get_dadi_pdf_params("mixture_gamma"), ["shape", "scale", "w"])

    with pytest.raises(Exception) as e_info:
        get_dadi_pdf_params("haha")


def test_print_available_pdfs(capfd):
    print_available_pdfs()
    out, err = capfd.readouterr()
    assert (
        out
        == "Available probability density functions:\n"
        + "- beta\n"
        + "- biv_ind_gamma\n"
        + "- biv_lognormal\n"
        + "- exponential\n"
        + "- gamma\n"
        + "- lognormal\n"
        + "- normal\n"
        + "- mixture\n"
    )

@pytest.fixture
def pdf_details():
    return {
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


def test_print_pdf_details(capfd, pdf_details):
    print_pdf_details("beta")
    out, err = capfd.readouterr()
    assert pdf_details["beta"] in out

    print_pdf_details("biv_ind_gamma")
    out, err = capfd.readouterr()
    assert pdf_details["biv_ind_gamma"] in out

    print_pdf_details("biv_lognormal")
    out, err = capfd.readouterr()
    assert pdf_details["biv_lognormal"] in out

    print_pdf_details("exponential")
    out, err = capfd.readouterr()
    assert pdf_details["exponential"] in out

    print_pdf_details("gamma")
    out, err = capfd.readouterr()
    assert pdf_details["gamma"] in out

    print_pdf_details("lognormal")
    out, err = capfd.readouterr()
    assert pdf_details["lognormal"] in out

    print_pdf_details("normal")
    out, err = capfd.readouterr()
    assert pdf_details["normal"] in out

    with pytest.raises(Exception) as e_info:
        print_pdf_details("haha")
