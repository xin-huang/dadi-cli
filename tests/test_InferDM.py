import dadi
import pytest
import subprocess
import glob
import os
import signal
import time
from src.InferDM import infer_demography

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

@pytest.fixture
def files():
    pytest.bash_command = str(
        "dadi-cli InferDM " + 
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.params --optimizations "
        )

def test_InferDM_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_syn.fs")
    func = dadi.Demographics1D.two_epoch
    p0 = [1, 0.5]
    pts_l = [120, 140, 160]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = -1
    misid = False
    cuda = False
    global_optimization = True
    maxeval = 100
    maxtime = 300
    seed = None
    infer_demography(fs, func, p0, pts_l, upper_bounds, lower_bounds, 
                     fixed_params, misid, cuda, global_optimization, maxeval, maxtime, seed)

def test_InferDM_bash(files):
    optimizations = 3
    subprocess.run(
        pytest.bash_command + str(optimizations), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits

def test_InferDM_seed(files):
    optimizations = 3
    subprocess.run(
        pytest.bash_command.replace('.demo.','.demo.seeded.') + str(optimizations) + " --seed 12345" , shell=True
    )
    fits = open(glob.glob("./tests/test_results/simulation.two_epoch.demo.seeded.params.InferDM.opts.*")[-1],'r').readlines()
    assert fits[1] == fits[2] == fits[3]

def test_InferDM_wq(files):
    optimizations = 3
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w " + str(optimizations), 
        shell=True
        )
    subprocess.run(
        pytest.bash_command.replace('.demo.','.demo.workqueue.') + str(optimizations) + ' ' +
        "--work-queue test-dm-two-epoch ./tests/mypwfile", shell=True
        )
    factory.kill()
    time.sleep(10)
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.workqueue.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert optimizations == number_of_fits



