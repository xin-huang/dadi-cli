import dadi
import pickle
import pytest
import subprocess
import glob
import os
import signal
import time
from dadi_cli.InferDFE import infer_dfe


try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


def test_infer_dfe_code():
    fs = dadi.Spectrum.from_file("./tests/example_data/two_epoch_non.fs")
    cache1d = pickle.load(open("./tests/example_data/cache_two_epoch_1d.bpkl", "rb"))
    cache2d = None
    sele_dist = "lognormal"
    sele_dist2 = None
    theta = 1000 * 2.31
    p0 = [1, 1]
    upper_bounds = [10, 10]
    lower_bounds = [1e-3, 1e-3]
    fixed_params = -1
    misid = False
    cuda = False
    maxeval = 100
    maxtime = 300
    infer_dfe(
        fs,
        cache1d,
        cache2d,
        sele_dist,
        sele_dist2,
        theta,
        p0,
        upper_bounds,
        lower_bounds,
        fixed_params,
        misid,
        cuda,
        maxeval,
        maxtime,
    )


@pytest.mark.skip()
def test_InferDFE_bash(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/example.two_epoch.dfe.params --optimizations "
        + str(optimizations),
        shell=True,
    )
    fits = glob.glob(
        "./tests/test_results/example.two_epoch.dfe.params.InferDFE.opts.*"
    )
    number_of_fits = sum(
        [ele.startswith("#") != True for ele in open(fits[-1]).readlines()]
    )
    assert optimizations == number_of_fits


@pytest.mark.skip()
def test_InferDFE_wq(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dfe-two-epoch -P ./tests/mypwfile -t 10 --workers-per-cycle=0 --cores=1  -w "
        + str(optimizations),
        shell=True,  # , preexec_fn=os.setsid
    )
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/example.two_epoch.dfe.workqueue.params --optimizations "
        + str(optimizations)
        + " "
        + "--work-queue test-dfe-two-epoch ./tests/mypwfile",
        shell=True,  # , preexec_fn=os.setsid
    )
    # WorkQueue can take awhile to shutdown, which can delay tests
    # So we force kill it and delay for 20 seconds so that results can
    # properly be written to file (result files are written after WorkQueue ends),
    # and because we test multiple instances of WorkQueue, we want to make sure they
    # do not run into an error when they try accessing the same WorkQueue resources.
    factory.kill()
    time.sleep(20)
    fits = glob.glob(
        "./tests/test_results/example.two_epoch.dfe.workqueue.params.InferDFE.opts.*"
    )
    number_of_fits = sum(
        [ele.startswith("#") != True for ele in open(fits[-1]).readlines()]
    )
    assert optimizations == number_of_fits


def test_InferDFE_seed(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/example.two_epoch.dfe.seeded.params "
        + "--seed 12345 --optimizations "
        + str(optimizations),
        shell=True,
    )
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/example.two_epoch.dfe.seeded.params "
        + "--seed 12345 --optimizations "
        + str(optimizations),
        shell=True,
    )
    fits_list = glob.glob(
        "./tests/test_results/example.two_epoch.dfe.seeded.params.InferDFE.opts.*"
    )
    fits_list.sort()
    fits1 = [line.strip() for line in open(fits_list[-2], "r").readlines()]
    fits1.sort()
    fits2 = [line.strip() for line in open(fits_list[-1], "r").readlines()]
    fits2.sort()
    for i in range(2, len(fits1)):
        assert fits1[i] == fits2[i]


@pytest.mark.skip()
def test_InferDFE_wq(capsys):
    optimizations = 3
    fits_fid = "./tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dfe-seed-two-epoch -P ./tests/mypwfile -t 10 --workers-per-cycle=0 --cores=1  -w "
        + str(optimizations),
        shell=True,  # , preexec_fn=os.setsid
    )
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.workqueue.seed.params --optimizations "
        + str(optimizations)
        + " --seed 12345 "
        + "--work-queue test-dfe-seed-two-epoch ./tests/mypwfile",
        shell=True,
    )
    subprocess.run(
        "dadi-cli InferDFE "
        + "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl "
        + "--demo-popt "
        + fits_fid
        + " --pdf1d lognormal --ratio 2.31 "
        + "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --nomisid "
        + "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.workqueue.seed.params --optimizations "
        + str(optimizations)
        + " --seed 12345 "
        + "--work-queue test-dfe-seed-two-epoch ./tests/mypwfile",
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
        "./tests/test_results/simulation.two_epoch.dfe.workqueue.seed.params.InferDFE.opts.*"
    )
    fits_list.sort()
    fits1 = [line.strip() for line in open(fits_list[-2], "r").readlines()]
    fits1.sort()
    fits2 = [line.strip() for line in open(fits_list[-1], "r").readlines()]
    fits2.sort()
    for i in range(2, len(fits1)):
        assert fits1[i] == fits2[i]
