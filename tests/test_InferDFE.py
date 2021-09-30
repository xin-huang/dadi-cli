import dadi
import pytest
import numpy as np
import subprocess
import glob
import os

try:
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
except:
    pass

def test_InferDFE(capsys):
    threads = 3
    try:
        fits_fid = glob.glob("./test_results/simulation.two_epoch.demo.params.InferDM.bestfits")[0]
    except:
        fid = open("./test_results/simulation.two_epoch.demo.params.InferDM.bestfits", "w")
        fid.write("#title\n0\t0\t0\t1000\n")
        fits_fid = "./test_results/simulation.two_epoch.demo.params.InferDM.bestfits_fake"
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./example_data/two_epoch_non.fs --cache1d example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./test_results/simulation.two_epoch.dfe.params --thread " + str(threads), shell=True
    )
    fits = glob.glob("./test_results/simulation.two_epoch.dfe.params.InferDFE.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits

def test_InferDM_wq(capsys):
    threads = 3
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./example_data/two_epoch_non.fs --cache1d cache_two_epoch_1d.bpkl " +
        "--demo-popt two_epoch_1d --pdf1d lognormal --ratio 2.31 " +
        "--grids 120 140 160 --p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./test_results/simulation.two_epoch.dfe.params --thread " + str(threads) + ' ' +
        "--work-queue test-dfe-two-epoch mypwfile " +
        "& work_queue_factory -T local -M test-dfe-two-epoch -P mypwfile --factory-timeout=180 --workers-per-cycle 0 --cores=1  -w " + str(threads), shell=True
    )
    fits = glob.glob("./test_results/simulation.two_epoch.dfe.params.wq.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits




