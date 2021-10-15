import dadi
import pytest
import numpy as np
import pickle
from src.GenerateCache import generate_cache

#def test_GenerateCache(capsys):
#    min_gamma_bound = 2000
#    gamma_pts = 50
#    subprocess.run(
#        "dadi-cli GenerateCache --demo-popt ./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits " +
#        "--gamma-bounds 1e-4 " + str(min_gamma_bound) + " --gamma-pts " + str(gamma_pts) + 
#        " --grids 120 140 160 --model two_epoch " + 
#        "--output ./tests/test_results/cache_large_two_epoch.bpkl --sample-sizes 20", shell=True
#    )

def test_generate_cache(capsys):
    generate_cache(model="two_epoch", grids=[120, 140, 160], popt="./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits", misid=False, gamma_bounds=[1e-4, 2000], gamma_pts=50, output="./tests/test_results/cache_large_two_epoch.bpkl", sample_sizes=[20], additional_gammas=[], mp=False, cuda=False, single_gamma=False)

    assert exists("./tests/test_results/cache_large_two_epoch.bpkl")
    s = pickle.load(open('./tests/test_results/cache_large_two_epoch.bpkl','rb'))
    assert int(np.min(s.gammas)) == -2000
    assert len(s.gammas) == 50
