import pytest
import subprocess
from dadi_cli import BestFit
import os
import numpy as np

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


@pytest.fixture
def files():
    pytest.example_input = (
        "./tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    )
    pytest.example_output = (
        "./tests/test_results/example.bestfit.two_epoch.demo.params.InferDM.bestfits"
    )
    pytest.res = np.array([
        [-np.inf, 10, 10, 10, np.inf],
        [-np.inf, 5, 5, 5, np.inf],
        [-np.inf, 1, 1, 1, np.inf]
        ])
#     pytest.res = BestFit.get_bestfit_params("./tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0", 
#         None, None, "./tests/test_results/not_used", 0.00001)
# os.remove("./tests/test_results/not_used")

@pytest.mark.skip()
def test_BestFit(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./tests/example_data/example.two_epoch.demo.params.InferDM "
        + "--lbounds 10e-3 10e-3 --ubounds 10 10",
        shell=True,
    )
    assert os.path.exists(
        "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    )


def test_get_bestfit_params(files):
    ll_delta = 0.999
    num_top = 10
    BestFit.get_bestfit_params(
        path=pytest.example_input,
        lbounds=[1e-3, 1e-3, 1e-5],
        ubounds=[10, 10, 1],
        output=pytest.example_output,
        delta=ll_delta,
        Nclose=3,
        Nbest=num_top,
    )
    fid = open(pytest.example_output).readlines()
    converged_res = False
    ll_converged_list = []
    top_res = False
    top_list = []
    for line in fid:
        if line.startswith("# Converged"):
            converged_res = True
        if line.startswith("# Top"):
            converged_res = False
            top_res = True
        if line.startswith("#") is not True:
            if converged_res:
                ll_converged_list.append(float(line.split("\t")[0]))
            if top_res:
                top_list.append(line)
    assert ll_delta >= max(ll_converged_list) - min(ll_converged_list)
    assert len(top_list) == num_top


def test_get_bestfit_params_no_convergence(capfd):
    BestFit.get_bestfit_params(
        path=pytest.example_input,
        lbounds=[1e-3, 1e-3, 1e-5],
        ubounds=[10, 10, 1],
        output=pytest.example_output,
        delta=0,
        Nclose=3,
        Nbest=10,
    )
    out, err = capfd.readouterr()
    assert out.strip() == "No convergence"


def test_opt_params_converged():
    pass


def test_close2boundaries():
    pass

@pytest.mark.parametrize("test_type, ubounds, lbounds",
                        [
                        ("normal_all", [15, 15, 15], [1e-3, 1e-3, 1e-3]),
                        ("normal_upper", [7, 7, 7], [1e-3, 1e-3, 1e-3]),
                        ("normal_lower", [15, 15, 15], [3, 3, 3]),
                        ("bound_error", [15, 15], [1e-3, 1e-3, 1e-3]),
                        ("res_error", [15, 15], [1e-3, 1e-3]),
                         ]
                         )
def test_boundary_filter(files, test_type, ubounds, lbounds):
    if "normal" not in test_type:
        with pytest.raises(ValueError) as exc_info:
            BestFit.boundary_filter(pytest.res, ubounds, lbounds)
        assert exc_info.type is ValueError
        if test_type == "bound_error":
            assert exc_info.value.args[0]== "Number of upper boundaries do not match number of lower boundaries."
        if test_type == "res_error":
            assert exc_info.value.args[0] == "Number of boundaries do not match number of model parameters."
    else:
        filtered_res = BestFit.boundary_filter(pytest.res, ubounds, lbounds)
        if "_all" in test_type:
            assert np.all(filtered_res == pytest.res)
        if "_upper" in test_type:
            assert np.all(filtered_res == pytest.res[1:,:])
        if "_lower" in test_type:
            assert np.all(filtered_res == pytest.res[:2,:])

