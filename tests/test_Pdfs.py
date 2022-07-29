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


def test_print_pdf_details(capfd):
    print_pdf_details("beta")
    out, err = capfd.readouterr()
    assert (
        out
        == "- beta:\n\n"
        + "        Beta probability density function.\n\n        params = [alpha, beta]\n"
        + "    \n"
    )

    print_pdf_details("biv_ind_gamma")
    out, err = capfd.readouterr()
    assert (
        out
        == "- biv_ind_gamma:\n\n"
        + "        Bivariate independent gamma probability density function.\n\n        If len(params) == 2, then params = [alpha, beta] by assuming alpha and beta are equal in the two populations\n        If len(params) == 4, then params = [alpha1, alpha2, beta1, beta2]\n        If len(params) == 3 or 5, then the last parameter is ignored\n"
        + "    \n"
    )

    print_pdf_details("biv_lognormal")
    out, err = capfd.readouterr()
    assert (
        out
        == "- biv_lognormal:\n\n"
        + "        Bivariate lognormal probability density function.\n\n        If len(params) == 3, then params = [mu, sigma, rho] by assuming mu and sigma are equal in the two populations\n        If len(params) == 5, then params = [mu1, mu2, sigma1, sigma2, rho]\n"
        + "    \n"
    )

    print_pdf_details("exponential")
    out, err = capfd.readouterr()
    assert (
        out
        == "- exponential:\n\n"
        + "        Exponential probability density function.\n\n        params = [scale]\n"
        + "    \n"
    )

    print_pdf_details("gamma")
    out, err = capfd.readouterr()
    assert (
        out
        == "- gamma:\n\n"
        + "        Gamma probability density function.\n\n        params = [alpha, beta] = [shape, scale]\n"
        + "    \n"
    )

    print_pdf_details("lognormal")
    out, err = capfd.readouterr()
    assert (
        out
        == "- lognormal:\n\n"
        + "        Lognormal probability density function.\n\n        params = [log_mu, log_sigma]\n"
        + "    \n"
    )

    print_pdf_details("normal")
    out, err = capfd.readouterr()
    assert (
        out
        == "- normal:\n\n"
        + "        Normal probability density function.\n\n        params = [mu, sigma]\n"
        + "    \n"
    )

    with pytest.raises(Exception) as e_info:
        print_pdf_details("haha")
