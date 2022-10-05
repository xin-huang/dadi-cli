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
    pytest.optimizations = 3
    pytest.bestfit_p0 = None
    pytest.delta_ll = 0.001
    pytest.global_optimization = False
    pytest.seed = None


@pytest.fixture
def infer_dfe_args():
    pytest.fs_mix = "tests/example_data/split_mig_non_mix.fs"
    pytest.fs_1d_lognorm = "tests/example_data/split_mig_non_1d.fs"
    pytest.fs_2d_lognorm = "tests/example_data/split_mig_non_2d.fs"
    pytest.model = "split_mig_fix_T"
    pytest.model_file = "tests/example_data/example_models"
    pytest.demo_popt = "tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    pytest.cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    pytest.cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pytest.pdf1d = "lognormal"
    pytest.pdf2d = "biv_lognormal"
    pytest.mix_pdf = False
    pytest.ratio = 2.31
    pytest.pdf_file = False
    pytest.p0 = [1, 1, 1]
    pytest.grids = [120, 140, 160]
    pytest.ubounds = [10, 10, 10]
    pytest.lbounds = [1e-3, 1e-3, 1e-3]
    pytest.constants = -1
    pytest.nomisid = True
    pytest.cuda = False
    pytest.maxeval = 100
    pytest.maxtime = 300
    pytest.output_prefix = "tests/test_results/example.split_mig_fix_T.dfe.params"
    pytest.check_convergence = True
    pytest.force_convergence = False
    pytest.work_queue = []
    pytest.debug_wq = False
    pytest.cpus = 1
    pytest.gpus = 0
    pytest.optimizations = 3
    pytest.bestfit_p0 = None
    pytest.delta_ll = 0.001
    pytest.global_optimization = False
    pytest.seed = None


def test_run_infer_dm(infer_dm_args):
    dadi_cli.run_infer_dm(pytest)

def test_run_infer_dm_misid(infer_dm_args):
    pytest.nomisid = False
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_misid.params"
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    dadi_cli.run_infer_dm(pytest)

def test_run_infer_dm_bestfit(infer_dm_args):
    print(pytest.nomisid)
    pytest.bestfit_p0 = "tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_bestfit_p0.params"
    pytest.nomisid = False
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    dadi_cli.run_infer_dm(pytest)

try:
    import work_queue as wq
    skip = False
except:
    skip = True

if os.path.exists("/home/runner/work/dadi-cli/dadi-cli"):
    skip = True

@pytest.mark.skipif(skip, reason="Could not load Work Queue or in GitAction environments")
# @pytest.mark.skip(reason="Issues running Work Queue right now")
def test_run_infer_dm_workqueue(infer_dm_args):
    import subprocess
    factory = subprocess.Popen(
        "work_queue_factory -T local -M pytest-dadi-cli -P ./tests/mypwfile --workers-per-cycle=0 --cores=1  -w 3 -W 3",
        shell=True,
    )
    pytest.output_prefix = "tests/test_results/example.two_epoch.demo_wq.params"
    pytest.work_queue = ['pytest-dadi-cli', 'tests/mypwfile']
    dadi_cli.run_infer_dm(pytest)
    factory.kill()

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







