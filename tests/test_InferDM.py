import dadi
import pytest
import numpy as np
import subprocess
import glob

def test_InferDM(capsys):
    threads = 3
    subprocess.run([
        "dadi-cli", "InferDM",
        "--fs", "./example_data/two_epoch_syn.fs", "--model", "two_epoch_1d", "--grids", "120", "140", "160", 
        "--p0", "1", ".5", "--ubounds", "10", "10", "--lbounds", "10e-3", "10e-3",
        "--output", "./test_results/simulation.two_epoch.demo.params", "--thread", str(threads)
    ])
    fits = glob.glob("./test_results/simulation.two_epoch.demo.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits








