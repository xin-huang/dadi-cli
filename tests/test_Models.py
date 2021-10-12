import dadi
import dadi.DFE as DFE
import pytest
from src.Models import get_dadi_model_func, get_dadi_model_params, print_available_models, print_model_details

def test_get_dadi_model_func():
    #Selection with a gamma shared between populations
    assert get_dadi_model_func('IM', withSelection=True, single_gamma=True) == DFE.DemogSelModels.IM_single_gamma
    assert get_dadi_model_func('IM_pre', withSelection=True, single_gamma=True) == DFE.DemogSelModels.IM_pre_single_gamma
    assert get_dadi_model_func('split_mig', withSelection=True, single_gamma=True) == DFE.DemogSelModels.split_mig_single_gamma
    assert get_dadi_model_func('split_asym_mig', withSelection=True, single_gamma=True) == DFE.DemogSelModels.split_asym_mig_single_gamma
    #Selection with independant gammas
    assert get_dadi_model_func('IM', withSelection=True, single_gamma=False) == DFE.DemogSelModels.IM
    assert get_dadi_model_func('IM_pre', withSelection=True, single_gamma=False) == DFE.DemogSelModels.IM_pre
    assert get_dadi_model_func('split_mig', withSelection=True, single_gamma=False) == DFE.DemogSelModels.split_mig
    assert get_dadi_model_func('split_asym_mig', withSelection=True, single_gamma=False) == DFE.DemogSelModels.split_asym_mig
    assert get_dadi_model_func('equil', withSelection=True, single_gamma=False) == DFE.DemogSelModels.equil
    assert get_dadi_model_func('two_epoch', withSelection=True, single_gamma=False) == DFE.DemogSelModels.two_epoch
    assert get_dadi_model_func('three_epoch', withSelection=True, single_gamma=False) == DFE.DemogSelModels.three_epoch
    assert get_dadi_model_func('mixture', withSelection=True, single_gamma=False) == DFE.mixture
    #1D demographic models
    assert get_dadi_model_func('bottlegrowth_1d', withSelection=False, single_gamma=False) == dadi.Demographics1D.bottlegrowth
    assert get_dadi_model_func('growth', withSelection=False, single_gamma=False) == dadi.Demographics1D.growth
    assert get_dadi_model_func('snm_1d', withSelection=False, single_gamma=False) == dadi.Demographics1D.snm
    assert get_dadi_model_func('three_epoch', withSelection=False, single_gamma=False) == dadi.Demographics1D.three_epoch
    assert get_dadi_model_func('two_epoch', withSelection=False, single_gamma=False) == dadi.Demographics1D.two_epoch
    #2D demographic models
    assert get_dadi_model_func('bottlegrowth_2d', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth
    assert get_dadi_model_func('bottlegrowth_split', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth_split
    assert get_dadi_model_func('bottlegrowth_split_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth_split_mig
    assert get_dadi_model_func('IM', withSelection=False, single_gamma=False) == dadi.Demographics2D.IM
    assert get_dadi_model_func('IM_pre', withSelection=False, single_gamma=False) == dadi.Demographics2D.IM_pre
    assert get_dadi_model_func('split_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.split_mig
    assert get_dadi_model_func('split_asym_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.split_asym_mig
    assert get_dadi_model_func('snm_2d', withSelection=False, single_gamma=False) == dadi.Demographics2D.snm
    #Cover error message
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=False, single_gamma=False)
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=True, single_gamma=False)
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=True, single_gamma=True)

def test_get_dadi_model_params():
    #1D demographic models
    assert get_dadi_model_params('bottlegrowth_1d') == ['nuB', 'nuF', 'T']
    assert get_dadi_model_params('growth') == ['nu', 'T']
    assert get_dadi_model_params('snm_1d') == []
    assert get_dadi_model_params('three_epoch') == ['nuB', 'nuF', 'TB', 'TF']
    assert get_dadi_model_params('two_epoch') == ['nu', 'T']
    #2D demographic models
    assert get_dadi_model_params('bottlegrowth_2d') == ['nuB', 'nuF', 'T']
    assert get_dadi_model_params('bottlegrowth_split') == ['nuB', 'nuF', 'T', 'Ts']
    assert get_dadi_model_params('bottlegrowth_split_mig') == ['nuB', 'nuF', 'm', 'T', 'Ts']
    assert get_dadi_model_params('IM') == ['s', 'nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('IM_pre') == ['nuPre', 'TPre', 's', 'nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('split_mig') == ['nu1', 'nu2', 'T', 'm']
    assert get_dadi_model_params('split_asym_mig') == ['nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('snm_2d') == []
    #Cover error message
    with pytest.raises(Exception) as e_info:
        get_dadi_model_params('haha')

def test_print_available_models(capfd):
    print_available_models()
    out, err = capfd.readouterr()
    assert out == 'Available 1D demographic models:\n' + '- bottlegrowth_1d\n' + '- growth\n' + '- snm_1d\n' + '- three_epoch\n' + '- two_epoch\n\n' + 'Available 2D demographic models:\n' + '- bottlegrowth_2d\n' + '- bottlegrowth_split\n' + '- bottlegrowth_split_mig\n' + '- IM\n' + '- IM_pre\n' + '- split_mig\n' + '- split_asym_mig\n' + '- snm_2d\n\n' + 'Available demographic models with selection:\n' + '- equil\n' + '- equil_X\n' + '- IM_sel\n' + '- IM_sel_single_gamma\n' + '- IM_pre_sel\n' + '- IM_pre_sel_single_gamma\n' + '- split_mig_sel\n' + '- split_mig_sel_single_gamma\n' + '- split_asym_mig_sel\n' + '- split_asym_mig_sel_single_gamma\n' + '- two_epoch_sel\n' + '- three_epoch_sel\n' + '- mixture\n'

def test_print_model_details():
    pass
