import dadi
import pytest
import subprocess
import glob
import os
import signal

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

def test_InferDFE(capsys):
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
        "work_queue_factory -T local -M test-dfe-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 --cores=1  -w " + str(optimizations), 
        shell=True, preexec_fn=os.setsid
        )
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.workqueue.params --optimizations " + str(optimizations) + ' ' +
        "--work-queue test-dfe-two-epoch ./tests/mypwfile", shell=True
    )
    os.killpg(os.getpgid(factory.pid), signal.SIGTERM)
    # factory.kill()
    fits = glob.glob("./tests/test_results/simulation.two_epoch.dfe.workqueue.params.InferDFE.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits




