import dadi
import pytest
import numpy as np
from src.Pdfs import get_dadi_pdf, get_dadi_pdf_params, print_available_pdfs, print_pdf_details

def test_get_dadi_pdf():
    pass

def test_get_dadi_pdf_params():
    assert np.array_equal(get_dadi_pdf_params('beta'), ['alpha', 'beta'])
    assert np.array_equal(get_dadi_pdf_params('biv_sym_ind_gamma'), ['shape', 'scale'])
    assert np.array_equal(get_dadi_pdf_params('biv_asym_ind_gamma'), ['shape1', 'scale1', 'shape2', 'scale2'])
    assert np.array_equal(get_dadi_pdf_params('biv_sym_lognormal'), ['log(mu)', 'log(sigma)', 'rho'])
    assert np.array_equal(get_dadi_pdf_params('biv_asym_lognormal'), ['log(mu1)', 'log(sigma1)', 'log(mu2)', 'log(sigma2)', 'rho'])
    assert np.array_equal(get_dadi_pdf_params('exponential'), ['scale'])
    assert np.array_equal(get_dadi_pdf_params('gamma'), ['shape', 'scale'])
    assert np.array_equal(get_dadi_pdf_params('lognormal'), ['log(mu)', 'log(sigma)'])
    assert np.array_equal(get_dadi_pdf_params('normal'), ['mu', 'sigma'])

    with pytest.raises(Exception) as e_info:
        get_dadi_pdf_params('haha')

def test_print_available_pdfs(capfd):
    print_available_pdfs()

    out, err = capfd.readouterr()

    assert out == 'Available probability density functions:\n' + '- beta\n' + '- biv_ind_gamma\n' + '- biv_lognormal\n' + '- exponential\n' + '- gamma\n' + '- lognormal\n' + '- normal\n'

def test_print_pdf_details(capfd):
    pass
