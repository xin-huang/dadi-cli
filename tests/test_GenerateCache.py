import dadi
import pytest
import subprocess
from os.path import exists
import numpy as np
import pickle

def test_GenerateCache(capsys):
    min_gamma_bound = -2000
    gamma_pts = 50
    subprocess.run(
        "dadi-cli GenerateCache --demo-popt ./example_data/example.two_epoch.demo.params.InferDM.bestfits " +
        "--gamma-bounds 1e-4 " + str(min_gamma_bound) + " --gamma-pts " + str(gamma_pts) + 
        " --grids 120 140 160 --model two_epoch " + 
        "--output ./test_results/cache_large_two_epoch.bpkl --sample-sizes 20", shell=True
    )
    assert exists("./test_results/cache_large_two_epoch.bpkl")
    s = pickle.load(open('./test_results/cache_large_two_epoch.bpkl','rb'))
    assert int(np.min(s.gammas)) == min_gamma_bound
    assert len(s.gammas) == gamma_pts


