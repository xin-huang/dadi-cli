import dadi
import pytest
import subprocess
from os.path import exists
from src import BestFit

def test_BestFit(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./tests/example_data/example.two_epoch.demo.params.InferDM " +
        "--model two_epoch_1d --lbounds 10e-3 10e-3 --ubounds 10 10", shell=True
    )
    assert exists("./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits")

def test_get_bestfit_params():
    pass

def test_opt_params_converged():
    pass

def test_close2boundaries():
    pass
