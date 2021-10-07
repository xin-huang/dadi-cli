import dadi
import pytest
import subprocess
import glob
import os

try:
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
except:
    pass

def test_InferDM(capsys):
    threads = 3
    subprocess.run(
        "dadi-cli InferDM " + 
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch_1d " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.params --thread " + str(threads), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits


# dadi-cli InferDM --fs ./example_data/two_epoch_syn.fs --model two_epoch_1d --grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 \
# --output ./test_results/simulation.two_epoch.demo.params.wq --thread 3 --work-queue test-two-epoch mypwfile &
# work_queue_worker -M test-two-epoch -P mypwfile --cores=1 --workers-per-cycle=0 -t 180 -w 3 --factory-timeout=600
@pytest.mark.skip(reason="no way of currently testing this")
def test_InferDM_wq(capsys):
    threads = 3
    subprocess.run(
        "dadi-cli InferDM " +
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch_1d " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " +
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.params.wq --thread " + str(threads) + ' ' +
        "--work-queue test-dm-two-epoch ./tests/mypwfile " +
        "& work_queue_factory -T local -M test-dm-two-epoch -P mypwfile --factory-timeout=180 --workers-per-cycle=0 --cores=1  -w " + str(threads), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.wq.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits




