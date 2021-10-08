import dadi
import pytest
from src.Models import get_dadi_model_func, get_dadi_model_params, print_available_models, print_model_details

def test_get_dadi_model_func():
    pass

def test_get_dadi_model_params():
    pass

def test_print_available_models(capfd):
    print_available_models()
    out, err = capfd.readouterr()
    assert out == 'Available 1D demographic models:\n' + '- bottlegrowth_1d\n' + '- growth\n' + '- snm_1d\n' + '- three_epoch\n' + '- two_epoch\n\n' + 'Available 2D demographic models:\n' + '- bottlegrowth_2d\n' + '- bottlegrowth_split\n' + '- bottlegrowth_split_mig\n' + '- IM\n' + '- IM_pre\n' + '- split_mig\n' + '- split_asym_mig\n' + '- snm_2d\n\n' + 'Available demographic models with selection:\n' + '- equil\n' + '- equil_X\n' + '- IM_sel\n' + '- IM_sel_single_gamma\n' + '- IM_pre_sel\n' + '- IM_pre_sel_single_gamma\n' + '- split_mig_sel\n' + '- split_mig_sel_single_gamma\n' + '- split_asym_mig_sel\n' + '- split_asym_mig_sel_single_gamma\n' + '- two_epoch_sel\n' + '- three_epoch_sel\n' + '- mixture\n'

def test_print_model_details():
    pass
