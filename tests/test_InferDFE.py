import dadi
import pickle
import pytest
import subprocess
import glob
import os
import signal
import time
from src.InferDFE import infer_dfe

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

def test_infer_dfe_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_non.fs")
    cache1d = pickle.load(open("./tests/example_data/cache_two_epoch_1d.bpkl","rb"))
    cache2d = None
    sele_dist = "lognormal"
    sele_dist2 = None
    theta = 1000*2.31
    p0 = [1, 1]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = None
    misid = False
    cuda = False
    maxeval = 100
    seed = None
    infer_dfe(fs, cache1d, cache2d, sele_dist, sele_dist2, theta,
              p0, upper_bounds, lower_bounds, fixed_params, misid, cuda, maxeval, seed)

def test_InferDFE_bash(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.params --optimizations " + str(optimizations), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.dfe.params.InferDFE.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits

def test_InferDFE_seed(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.seeded.params " +
        "--seed 12345 --optimizations " + str(optimizations), shell=True
    )
    fits = open(glob.glob("./tests/test_results/simulation.two_epoch.dfe.seeded.params.InferDFE.opts.*")[-1],'r').readlines()
    assert fits[1] == fits[2] == fits[3]

def test_InferDFE_wq(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dfe-two-epoch -P ./tests/mypwfile -t 10 --workers-per-cycle=0 --cores=1  -w " + str(optimizations), 
        shell=True#, preexec_fn=os.setsid
        )
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.workqueue.params --optimizations " + str(optimizations) + ' ' +
        "--work-queue test-dfe-two-epoch ./tests/mypwfile", shell=True#, preexec_fn=os.setsid
    )
    factory.kill()
    time.sleep(10)
    fits = glob.glob("./tests/test_results/simulation.two_epoch.dfe.workqueue.params.InferDFE.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits




