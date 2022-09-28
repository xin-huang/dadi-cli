import pytest
import dadi_cli.__main__ as dadi_cli
import os

from dadi_cli.GenerateFs import *
from dadi_cli.GenerateCache import *
from dadi_cli.InferDM import *
from dadi_cli.InferDFE import *
from dadi_cli.Pdfs import *
from dadi_cli.Models import *
from dadi_cli.utilities import *

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass

@pytest.fixture
def infer_dm_args():
    pytest.fs = "tests/example_data/two_epoch_syn.fs"
    pytest.model = "three_epoch_bottleneck"
    pytest.model_file = "tests/example_data/example_models"
    pytest.p0 = [1, 0.5]
    pytest.grids = [120, 140, 160]
    pytest.ubounds = [10, 10]
    pytest.lbounds = [1e-3, 1e-3]
    pytest.constants = -1
    pytest.nomisid = True
    pytest.cuda = False
    pytest.maxeval = 100
    pytest.maxtime = 300
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo.params"
    pytest.check_convergence = True
    pytest.force_convergence = False
    pytest.work_queue = []
    pytest.debug_wq = False
    pytest.cpus = 1
    pytest.gpus = 0
    pytest.optimizations = 1
    pytest.bestfit_p0 = None
    pytest.delta_ll = 0.001
    pytest.global_optimization = False
    pytest.seed = None

def test_run_infer_dm(infer_dm_args):
    dadi_cli.run_infer_dm(args)

def test_run_infer_dm_misid(infer_dm_args):
    pytest.nomisid = False
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_misid.params"
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    dadi_cli.run_infer_dm(args)

def test_run_infer_dm_bestfit(infer_dm_args):
    pytest.bestfit_p0 = "tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_bestfit_p0.params"
    dadi_cli.run_infer_dm(args)

try:
    import work_queue as wq
    skip = False
except:
    skip = True

@pytest.mark.skipif(skip, reason="Could not load Work Queue")
def test_run_infer_dm_workqueue(infer_dm_args):
    import subprocess
    factory = subprocess.Popen(
        "work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w 1 -W 1 -E '--connection-mode by_apparent_ip'",
        shell=True,
    )
    pytest.model = "two_epoch"
    pytest.model_file = None
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_wq.params"
    pytest.work_queue = ['test-dm-two-epoch', 'tests/mypwfile']
    dadi_cli.run_infer_dm(args)
    factory.kill()


    # Clean up args
    pytest.nomisid = True
    pytest.p0 = [1, 0.5]
    pytest.ubounds = [10, 10]
    pytest.lbounds = [1e-3, 1e-3]
    pytest.output_prefix = None
    pytest.work_queue = []


def test_run_simulate_dm():
    def simulate_args():
        return
    simulate_args.model = "two_epoch"
    simulate_args.model_file = None
    simulate_args.p0 = [1, 0.5]
    simulate_args.ns = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.misid = False
    simulate_args.output = "tests/test_results/main_simulate_two_epoch.fs"
    simulate_args.inference_file = False

    dadi_cli.run_simulate_dm(simulate_args)


