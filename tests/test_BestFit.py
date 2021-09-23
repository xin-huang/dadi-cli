import dadi
import pytest
import subprocess
from os.path import exists

def test_BestFit(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./test_results/simulation.two_epoch.demo.params.InferDM " +
        "--model two_epoch_1d --lbounds 10e-3 10e-3 --ubounds 10 10", shell=True
    )
    assert exists("./test_results/simulation.two_epoch.demo.params.InferDM.bestfits")