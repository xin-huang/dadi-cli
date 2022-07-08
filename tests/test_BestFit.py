import dadi
import pytest
import subprocess
from dadi_cli import BestFit
import os

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

@pytest.fixture
def files():
    pytest.example_input = "./tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    pytest.example_output = "./tests/test_results/example.bestfit.two_epoch.demo.params.InferDM.bestfits"

@pytest.mark.skip()
def test_BestFit(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./tests/example_data/example.two_epoch.demo.params.InferDM " +
        "--lbounds 10e-3 10e-3 --ubounds 10 10", shell=True
    )
    assert os.path.exists("./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits")

def test_get_bestfit_params(files):
    ll_delta = 0.999
    num_top = 10
    BestFit.get_bestfit_params(path=pytest.example_input, 
        lbounds=[1e-3, 1e-3, 1e-5], 
        ubounds=[10, 10, 1], output=pytest.example_output, 
        delta=ll_delta, Nclose=3, Nbest=num_top)
    fid = open(pytest.example_output).readlines()
    converged_res = False
    ll_converged_list = []
    top_res = False
    top_list = []
    for line in fid:
        if line.startswith('# Converged'):
            converged_res = True
        if line.startswith('# Top'):
            converged_res = False
            top_res = True
        if line.startswith('#') != True:
            if converged_res:
                ll_converged_list.append(float(line.split('\t')[0]))
            if top_res:
                top_list.append(line)
    assert ll_delta >= max(ll_converged_list) - min(ll_converged_list)
    assert len(top_list) == num_top

def test_get_bestfit_params_no_convergence(capfd):
    BestFit.get_bestfit_params(path=pytest.example_input, lbounds=[1e-3, 1e-3, 1e-5], 
        ubounds=[10, 10, 1], output=pytest.example_output, 
        delta=0, Nclose=3, Nbest=10)
    out, err = capfd.readouterr()
    assert out.strip() == "No convergence"

def test_opt_params_converged():
    pass

def test_close2boundaries():
    pass
