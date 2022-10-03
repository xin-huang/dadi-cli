import dadi.DFE as DFE
import pytest
import numpy as np
import pickle
import os
from dadi_cli.GenerateCache import generate_cache
from dadi_cli.Models import get_model


try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


def test_generate_cache_code(capsys):
    generate_cache(
        func=DFE.DemogSelModels.two_epoch_sel,
        grids=[120, 140, 160],
        popt="./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits",
        gamma_bounds=[1e-4, 2000],
        gamma_pts=50,
        output="./tests/test_results/cache_large_two_epoch_code.bpkl",
        sample_sizes=[20],
        additional_gammas=[],
        cpus=None,
        gpus=0,
        dimensionality=1,
    )

    assert os.path.exists("./tests/test_results/cache_large_two_epoch_code.bpkl")
    s = pickle.load(open("./tests/test_results/cache_large_two_epoch_code.bpkl", "rb"))
    assert int(np.min(s.gammas)) == -2000
    assert len(s.gammas) == 50


@pytest.mark.skip()
def test_generate_cache_bash(capsys):
    import subprocess

    subprocess.run(
        "dadi-cli GenerateCache --demo-popt tests/example_data/example.two_epoch.demo.params.InferDM.bestfits "
        + "--model two_epoch_sel --gamma-pts 50 --gamma-bounds 1e-4 2000 "
        + "--grids 120 140 160 --sample-sizes 20 --dimensionality 1 --output tests/test_results/cache_large_two_epoch_bash.bpkl",
        shell=True,
    )

    assert os.path.exists("./tests/test_results/cache_large_two_epoch_bash.bpkl")
    s = pickle.load(open("./tests/test_results/cache_large_two_epoch_bash.bpkl", "rb"))
    assert int(np.min(s.gammas)) == -2000
    assert len(s.gammas) == 50


def test_generate_cache_custom_model_code(capsys):
    sel_func, params = get_model(
        "split_mig_fix_T_sel", "tests/example_data/example_models.py"
    )
    generate_cache(
        func=sel_func,
        grids=[120, 140, 160],
        popt="./tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits",
        gamma_bounds=[1e-4, 20],
        gamma_pts=5,
        output="./tests/test_results/cache_small_2s_split_mig_fix_T_sel_code.bpkl",
        sample_sizes=[20, 20],
        additional_gammas=[],
        cpus=None,
        gpus=0,
        dimensionality=2,
    )

    assert os.path.exists(
        "./tests/test_results/cache_small_2s_split_mig_fix_T_sel_code.bpkl"
    )
    s = pickle.load(
        open("./tests/test_results/cache_small_2s_split_mig_fix_T_sel_code.bpkl", "rb")
    )
    assert int(np.min(s.gammas)) == -20
    assert len(s.gammas) == 5


@pytest.mark.skip()
def test_generate_cache_custom_model_bash(capsys):
    import subprocess

    subprocess.run(
        "dadi-cli GenerateCache --demo-popt tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits "
        + "--model split_mig_fix_T_sel --model-file tests/example_data/example_models --gamma-pts 5 --gamma-bounds 1e-4 20 "
        + "--grids 120 140 160 --sample-sizes 20 20 --dimensionality 2 --output tests/test_results/cache_small_2s_split_mig_fix_T_sel_bash.bpkl",
        shell=True,
    )

    assert os.path.exists(
        "./tests/test_results/cache_small_2s_split_mig_fix_T_sel_code.bpkl"
    )
    s = pickle.load(
        open("./tests/test_results/cache_small_2s_split_mig_fix_T_sel_code.bpkl", "rb")
    )
    assert int(np.min(s.gammas)) == -2000
    assert len(s.gammas) == 50
