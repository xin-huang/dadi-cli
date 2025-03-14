import dadi
import dadi.DFE as DFE
import pytest
import textwrap
from dadi_cli.Models import *
from inspect import isfunction, getmembers
from importlib.metadata import version


# Define varibles to hold list of all dadi model names and functions
@pytest.fixture
def model_list():
    pytest.demo_model_list = getmembers(dadi.Demographics1D, isfunction) + \
    getmembers(dadi.Demographics2D, isfunction) + \
    getmembers(dadi.Demographics3D, isfunction)
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


@pytest.mark.skipif(version('dadi') <= '2.3.6', reason="Older version of dadi has extra redundant model names that have been removed.")
def test_print_built_in_models(capfd, model_list):
    print_built_in_models()
    out, err = capfd.readouterr()
    expected = """\
    Built-in 1D dadi demographic models:
    - bottlegrowth_1d
    - growth
    - snm_1d
    - three_epoch
    - three_epoch_inbreeding
    - two_epoch

    Built-in 2D dadi and Portik et al. (2017) demographic models:
    - IM
    - IM_mscore
    - IM_pre
    - IM_pre_mscore
    - anc_asym_mig
    - anc_asym_mig_size
    - anc_sym_mig
    - anc_sym_mig_size
    - asym_mig
    - asym_mig_size
    - asym_mig_twoepoch
    - bottlegrowth_2d
    - bottlegrowth_split
    - bottlegrowth_split_mig
    - founder_asym
    - founder_nomig
    - founder_nomig_admix_early
    - founder_nomig_admix_late
    - founder_nomig_admix_two_epoch
    - founder_sym
    - no_mig
    - no_mig_size
    - sec_contact_asym_mig
    - sec_contact_asym_mig_size
    - sec_contact_asym_mig_size_three_epoch
    - sec_contact_asym_mig_three_epoch
    - sec_contact_sym_mig
    - sec_contact_sym_mig_size
    - sec_contact_sym_mig_size_three_epoch
    - sec_contact_sym_mig_three_epoch
    - snm_2d
    - split_asym_mig
    - split_delay_mig
    - split_mig
    - split_mig_mscore
    - sym_mig
    - sym_mig_size
    - sym_mig_twoepoch
    - vic_anc_asym_mig
    - vic_anc_sym_mig
    - vic_no_mig
    - vic_no_mig_admix_early
    - vic_no_mig_admix_late
    - vic_sec_contact_asym_mig
    - vic_sec_contact_sym_mig
    - vic_two_epoch_admix

    Built-in 3D dadi and Portik et al. (2017) demographic models:
    - admix_origin_no_mig
    - admix_origin_sym_mig_adj
    - admix_origin_uni_mig_adj
    - ancmig_2_size
    - ancmig_adj_1
    - ancmig_adj_2
    - ancmig_adj_3
    - out_of_africa
    - refugia_adj_1
    - refugia_adj_2
    - refugia_adj_2_var_sym
    - refugia_adj_2_var_uni
    - refugia_adj_3
    - refugia_adj_3_var_sym
    - refugia_adj_3_var_uni
    - sim_split_no_mig
    - sim_split_no_mig_size
    - sim_split_refugia_sym_mig_adjacent
    - sim_split_refugia_sym_mig_adjacent_size
    - sim_split_refugia_sym_mig_adjacent_var
    - sim_split_refugia_sym_mig_all
    - sim_split_refugia_uni_mig_adjacent_var
    - sim_split_sym_mig_adjacent
    - sim_split_sym_mig_adjacent_var
    - sim_split_sym_mig_all
    - sim_split_uni_mig_adjacent_var
    - split_nomig
    - split_nomig_size
    - split_sym_mig_adjacent_var1
    - split_sym_mig_adjacent_var2
    - split_symmig_adjacent
    - split_symmig_all
    - split_uni_mig_adjacent_var1
    - split_uni_mig_adjacent_var2

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


def test_custom_model_import(capfd):
    # Test importing a non-existing file
    model_file = 'tests/non_existing_model'
    with pytest.raises(ImportError) as excinfo:
        get_model('hallo', model_file)

    assert f"Failed to import module: {model_file}" in str(excinfo.value)

    model_file = 'tests/example_data/example_models'
    custome_model_list = ['three_epoch_bottleneck', 'split_mig_fix_T', 'split_mig_fix_T_sel']

    # Test importing good custom models
    for custome_model in custome_model_list:
        get_model(custome_model, model_file)
        out, err = capfd.readouterr()
        assert out == "" and err == ""
        
    # Test importing a custom model without .__param_names__ attribute
    with pytest.raises(ValueError) as e_info:
        get_model('split_no_mig_missing_param_names', model_file)
    assert str(e_info.value) == "Demographic model needs a .__param_names__ attribute!\nAdd one by adding the line split_no_mig_missing_param_names.__param_name__ = [LIST_OF_PARAMS]\nReplacing LIST_OF_PARAMS with the names of the parameters as strings."

    # Test importing a custom model not in example_models
    with pytest.raises(AttributeError) as e_info:
        get_model('haha', model_file)
    assert str(e_info.value) == "module 'example_models' has no attribute 'haha'"
