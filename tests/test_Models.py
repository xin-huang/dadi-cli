import dadi
import dadi.DFE as DFE
import pytest
import textwrap
from dadi_cli.Models import *
from inspect import isfunction, getmembers


# Define varibles to hold list of all dadi model names and functions
@pytest.fixture
def model_list():
    pytest.demo_model_list = getmembers(dadi.Demographics1D, isfunction) + getmembers(
        dadi.Demographics2D, isfunction
    )
    pytest.sel_model_list = getmembers(DFE.DemogSelModels, isfunction)


def test_get_built_in_model(model_list):
    for model in pytest.demo_model_list:  # + pytest.sel_model_list:
        if model[0] == "bottlegrowth":
            continue
        if model[0] == "snm":
            continue
        func, params = get_model(model[0])
        assert func == model[1]
        assert params == model[1].__param_names__

    # Cover error message
    with pytest.raises(ValueError) as e_info:
        get_model("haha")

    assert str(e_info.value) == "Cannot find model: haha."


def test_print_built_in_models(capfd, model_list):
    print_built_in_models()
    out, err = capfd.readouterr()
    expected = """\
    Built-in 1D demographic models:
    - bottlegrowth_1d
    - growth
    - snm_1d
    - three_epoch
    - three_epoch_inbreeding
    - two_epoch

    Built-in 2D demographic models:
    - IM
    - IM_mscore
    - IM_pre
    - IM_pre_mscore
    - bottlegrowth_2d
    - bottlegrowth_split
    - bottlegrowth_split_mig
    - snm_2d
    - split_asym_mig
    - split_delay_mig
    - split_mig
    - split_mig_mscore

    Built-in demographic models with selection:
    - IM_pre_sel
    - IM_pre_sel_single_gamma
    - IM_sel
    - IM_sel_single_gamma
    - bottlegrowth_1d_sel
    - bottlegrowth_2d_sel
    - bottlegrowth_2d_sel_single_gamma
    - bottlegrowth_split_mig_sel
    - bottlegrowth_split_mig_sel_single_gamma
    - bottlegrowth_split_sel
    - bottlegrowth_split_sel_single_gamma
    - equil
    - growth_sel
    - split_asym_mig_sel
    - split_asym_mig_sel_single_gamma
    - split_delay_mig_sel
    - split_delay_mig_sel_single_gamma
    - split_mig_sel
    - split_mig_sel_single_gamma
    - three_epoch_sel
    - two_epoch_sel
    """
    assert textwrap.dedent(expected) == out


def test_print_built_in_model_details(capfd, model_list):
    for model in pytest.demo_model_list:  # + pytest.sel_model_list:
        if model[0] == "bottlegrowth":
            continue
        if model[0] == "snm":
            continue
        print_built_in_model_details(model[0])
        out = ""
        out, err = capfd.readouterr()
        model_doc = model[1].__doc__
        model_doc_new = ""
        for ele in model_doc.split("\n"):
            if "ns:" not in ele and "pts:" not in ele and "n1" not in ele:
                model_doc_new += "\t" + ele.strip() + "\n"
        model_doc_new = "- " + model[0] + ":\n\n\t" + model_doc_new.strip() + "\n\n"
        assert out == model_doc_new

    with pytest.raises(ValueError) as e_info:
        print_built_in_model_details("mixture")

    assert str(e_info.value) == "Cannot find model: mixture."

def test_custome_model_import(capfd):
    import tests.example_data.example_models as custom
    custome_model_list = ['three_epoch_bottleneck', 'split_mig_fix_T', 'split_mig_fix_T_sel']
    # Test importing good custom models
    for custome_model in custome_model_list:
        get_model(custome_model, 'tests/example_data/example_models')
        out, err = capfd.readouterr()
        assert out == "" and err == ""
    # Test importing a custom model without .__param_names__ attribute
    with pytest.raises(ValueError) as e_info:
        get_model('split_no_mig_missing_param_names', 'tests/example_data/example_models')
    assert str(e_info.value) == "Demographic model needs a .__param_names__ attribute!\nAdd one by adding the line split_no_mig_missing_param_names.__param_name__ = [LIST_OF_PARAMS]\nReplacing LIST_OF_PARAMS with the names of the parameters as strings."
    # Test importing a custom model not in example_models
    with pytest.raises(AttributeError) as e_info:
        get_model('haha', 'tests/example_data/example_models')
    assert str(e_info.value) == "module 'example_models' has no attribute 'haha'"


