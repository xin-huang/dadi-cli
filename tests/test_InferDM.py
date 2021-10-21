import dadi
import pytest
import subprocess
import glob
import os
import signal
import time

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

def test_InferDM(capsys):
    optimizations = 3
    subprocess.run(
        "dadi-cli InferDM " + 
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.params --optimizations " + str(optimizations), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits

def test_InferDM_seed(capsys):
    optimizations = 3
    subprocess.run(
        "dadi-cli InferDM " + 
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.seeded.params " +
        "--seed 12345 --optimizations " + str(optimizations), shell=True
    )
    fits = open(glob.glob("./tests/test_results/simulation.two_epoch.demo.seeded.params.InferDM.opts.*")[-1],'r').readlines()
    assert fits[1] == fits[2] == fits[3]

def test_InferDM_wq(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w " + str(optimizations), 
        shell=True, preexec_fn=os.setsid
        )
    subprocess.run(
        "dadi-cli InferDM " +
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " +
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.workqueue.params --optimizations " + str(optimizations) + ' ' +
        "--work-queue test-dm-two-epoch ./tests/mypwfile", shell=True, preexec_fn=os.setsid
        )
    factory.kill()
    time.sleep(10)
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.workqueue.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits

def cleanup(capsys):
    import shutil
    import os
    shutil.rmtree("./tests/test_results/")
    assert os.path.exists("./tests/test_results") == False


