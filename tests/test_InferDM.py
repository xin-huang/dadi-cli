import dadi
import pytest
import subprocess
import glob
import nlopt
import os
import signal
import time
from dadi_cli.InferDM import infer_demography
from dadi_cli.InferDM import infer_global_opt
from dadi_cli.BestFit import get_bestfit_params
from dadi_cli.Models import get_model

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


@pytest.fixture
def files():
    pytest.bash_command = str(
        "dadi-cli InferDM "
        + "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch --nomisid "
        + "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 "
        + "--output-prefix ./tests/test_results/example.two_epoch.demo.params --optimizations "
    )


def test_infer_demography_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_syn.fs")
    func = dadi.Demographics1D.two_epoch
    p0 = [1, 0.5]
    pts_l = [120, 140, 160]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = -1
    misid = False
    cuda = False
    maxeval = 100
    maxtime = 300
    infer_demography(
        fs,
        func,
        p0,
        pts_l,
        upper_bounds,
        lower_bounds,
        fixed_params,
        misid,
        cuda,
        maxeval,
        maxtime,
    )

def test_infer_custom_demography_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_syn.fs")
    func, params = get_model('three_epoch_bottleneck', 'tests/example_data/example_models')
    p0 = [1, 0.5]
    pts_l = [120, 140, 160]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = -1
    misid = False
    cuda = False
    maxeval = 100
    maxtime = 300
    infer_demography(
        fs,
        func,
        p0,
        pts_l,
        upper_bounds,
        lower_bounds,
        fixed_params,
        misid,
        cuda,
        maxeval,
        maxtime,
    )

def test_infer_global_opt_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_syn.fs")
    func = dadi.Demographics1D.two_epoch
    p0 = [1, 0.5]
    pts_l = [120, 140, 160]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = -1
    misid = False
    cuda = False
    maxeval = 100
    maxtime = 300
    global_algorithm = nlopt.GN_MLSL
    ll_global, popt, theta = infer_global_opt(
        fs,
        func,
        p0,
        pts_l,
        upper_bounds,
        lower_bounds,
        fixed_params,
        misid,
        cuda,
        maxeval,
        maxtime,
        global_algorithm,
        seed=12345,
    )


@pytest.mark.skip()
def test_infer_demography_bash(files):
    optimizations = 3
    subprocess.run(pytest.bash_command + str(optimizations), shell=True)
    fits = glob.glob(
        "./tests/test_results/example.two_epoch.demo.params.InferDM.opts.*"
    )
    number_of_fits = sum(
        [ele.startswith("#") != True for ele in open(fits[-1]).readlines()]
    )
    assert optimizations == number_of_fits

@pytest.mark.skip()
def test_infer_custom_demography_bash(files):
    optimizations = 3
    cmd = pytest.bash_command.replace("--model two_epoch", "--model three_epoch_bottleneck").replace(".two_epoch.", ".three_epoch_bottleneck.") + str(optimizations) + " --model-file tests/example_data/example_models"
    subprocess.run(cmd, shell=True)
    fits = glob.glob(
        "./tests/test_results/example.three_epoch_bottleneck.demo.params.InferDM.opts.*"
    )
    number_of_fits = sum(
        [ele.startswith("#") != True for ele in open(fits[-1]).readlines()]
    )
    assert optimizations == number_of_fits

@pytest.mark.skip()
def test_InferDM_wq(files):
    optimizations = 3
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w "
        + str(optimizations),
        shell=True,
    )
    print(
        pytest.bash_command.replace(".demo.", ".demo.workqueue.")
        + str(optimizations)
        + " --debug-wq "
        + "--work-queue test-dm-two-epoch ./tests/mypwfile"  # , shell=True
    )
    # WorkQueue can take awhile to shutdown, which can delay tests
    # So we force kill it and delay for 20 seconds so that results can
    # properly be written to file (result files are written after WorkQueue ends),
    # and because we test multiple instances of WorkQueue, we want to make sure they
    # do not run into an error when they try accessing the same WorkQueue resources.
    factory.kill()
    # WorkQueue
    time.sleep(20)
    fits = glob.glob(
        "./tests/test_results/example.two_epoch.demo.workqueue.params.InferDM.opts.*"
    )
    number_of_fits = sum(
        [ele.startswith("#") != True for ele in open(fits[-1]).readlines()]
    )
    assert optimizations == number_of_fits


@pytest.mark.skip()
def test_InferDM_seed(files):
    optimizations = 3
    subprocess.run(
        pytest.bash_command.replace(".demo.", ".demo.seeded.")
        + str(optimizations)
        + " --seed 12345",
        shell=True,
    )
    subprocess.run(
        pytest.bash_command.replace(".demo.", ".demo.seeded.")
        + str(optimizations)
        + " --seed 12345",
        shell=True,
    )
    fits_list = glob.glob(
        "./tests/test_results/example.two_epoch.demo.seeded.params.InferDM.opts.*"
    )
    fits_list.sort()
    fits1 = [line.strip() for line in open(fits_list[-2], "r").readlines()]
    fits1.sort()
    fits2 = [line.strip() for line in open(fits_list[-1], "r").readlines()]
    fits2.sort()
    for i in range(2, len(fits1)):
        assert fits1[i] == fits2[i]


@pytest.mark.skip()
def test_InferDM_wq_seed(files):
    optimizations = 3
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dm-seed-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w "
        + str(optimizations),
        shell=True,
    )
    subprocess.run(
        pytest.bash_command.replace(".demo.", ".demo.workqueue.seed.")
        + str(optimizations)
        + " --seed 12345 "
        + "--work-queue test-dm-seed-two-epoch ./tests/mypwfile",
        shell=True,
    )
    subprocess.run(
        pytest.bash_command.replace(".demo.", ".demo.workqueue.seed.")
        + str(optimizations)
        + " --seed 12345 "
        + "--work-queue test-dm-seed-two-epoch ./tests/mypwfile",
        shell=True,
    )
    # WorkQueue can take awhile to shutdown, which can delay tests
    # So we force kill it and delay for 20 seconds so that results can
    # properly be written to file (result files are written after WorkQueue ends),
    # and because we test multiple instances of WorkQueue, we want to make sure they
    # do not run into an error when they try accessing the same WorkQueue resources.
    factory.kill()
    time.sleep(20)
    fits_list = glob.glob(
        "./tests/test_results/simulation.two_epoch.demo.workqueue.seed.params.InferDM.opts.*"
    )
    fits_list.sort()
    fits1 = [line.strip() for line in open(fits_list[-2], "r").readlines()]
    fits1.sort()
    fits2 = [line.strip() for line in open(fits_list[-1], "r").readlines()]
    fits2.sort()
    for i in range(2, len(fits1)):
        print(fits1[i], fits2[i])
        assert fits1[i] == fits2[i]
