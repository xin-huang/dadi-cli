import pytest
import dadi_cli.__main__ as dadi_cli
import os
import glob

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

def test_run_generate_fs():
    def gen_fs_args():
        return
    gen_fs_args.vcf = "tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf"
    gen_fs_args.output = "tests/test_results/main_gen_data.fs"
    gen_fs_args.bootstrap = None
    gen_fs_args.chunk_size = None
    gen_fs_args.seed = 1234
    gen_fs_args.pop_ids = ["YRI", "CEU"]
    gen_fs_args.pop_info = "examples/data/1KG.YRI.CEU.popfile.txt"
    gen_fs_args.projections = [216, 198]
    gen_fs_args.polarized = True
    gen_fs_args.marginalize_pops = None
    gen_fs_args.subsample = False
    gen_fs_args.mask_shared = False
    gen_fs_args.mask = False
    dadi_cli.run_generate_fs(gen_fs_args)
    gen_fs_args.mask = True
    dadi_cli.run_generate_fs(gen_fs_args)
    gen_fs_args.mask_shared = True
    dadi_cli.run_generate_fs(gen_fs_args)
    os.remove(gen_fs_args.output)


def test_run_simulate_dm():
    def simulate_args():
        return
    simulate_args.model = "two_epoch"
    simulate_args.model_file = None
    simulate_args.p0 = [1, 0.5]
    simulate_args.sample_sizes = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.nomisid = True
    simulate_args.output = "tests/test_results/main_simulate_two_epoch.fs"
    simulate_args.inference_file = False

    dadi_cli.run_simulate_dm(simulate_args)
    os.remove(simulate_args.output)

def test_run_simulate_demes():
    def simulate_args():
        return
    simulate_args.demes_file = "examples/data/gutenkunst_ooa.yml"
    simulate_args.pop_ids = ["YRI"]
    simulate_args.sample_sizes = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.output = "tests/test_results/main_simulate_demes_ooa.fs"

    dadi_cli.run_simulate_demes(simulate_args)
    os.remove(simulate_args.output)

def test_run_simulate_dfe():
    def simulate_args():
        return
    simulate_args.p0 = [1, 1.5, 0, 0.01, 0.05]
    simulate_args.cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    simulate_args.cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    simulate_args.pdf1d = "lognormal"
    simulate_args.pdf2d = "biv_lognormal"
    simulate_args.ratio = 2.31
    simulate_args.nomisid = False
    simulate_args.output = "tests/test_results/main_simulate_mix_dfe.fs"

    dadi_cli.run_simulate_dfe(simulate_args)
    os.remove(simulate_args.output)

def test_run_generate_cache():
    def generate_cache_args():
        return
    generate_cache_args.model = "split_mig_fix_T_one_s"
    generate_cache_args.model_file = "tests/example_data/example_models"
    generate_cache_args.grids = [20, 40, 60]
    generate_cache_args.demo_popt = "tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    generate_cache_args.gamma_bounds = (1e-4, 10)
    generate_cache_args.gamma_pts = 5
    generate_cache_args.additional_gammas = []
    generate_cache_args.output = "tests/test_results/test.cache.bpkl"
    generate_cache_args.sample_sizes = [10, 10]
    generate_cache_args.cpus = 1
    generate_cache_args.gpus = 0
    generate_cache_args.dimensionality = 1
    dadi_cli.run_generate_cache(generate_cache_args)
    os.remove(generate_cache_args.output)

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
    pytest.maxeval = 10
    pytest.maxtime = 10
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo.params"
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
    pytest.email = None

def test_run_infer_dm(infer_dm_args):
    dadi_cli.run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_no_custom_model_dm(infer_dm_args):
    pytest.model = "three_epoch_inbreeding"
    pytest.model_file = None
    pytest.constants = [None, 1, None, None, None]
    pytest.ubounds = [10, 10, 10, 10, 1]
    pytest.lbounds = [1e-3, 1e-3, 1e-3, 1e-3, 1e-5]
    pytest.p0 = -1
    pytest.maxeval = False
    pytest.inbreeding = True
    pytest.global_optimization = True
    dadi_cli.run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_dm_misid(infer_dm_args):
    pytest.nomisid = False
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo_misid.params"
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    dadi_cli.run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_dm_global_bestfit(infer_dm_args):
    pytest.global_optimization = True
    print(pytest.nomisid)
    pytest.bestfit_p0 = "tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo_bestfit_p0.params"
    pytest.nomisid = False
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    pytest.maxeval = 10
    dadi_cli.run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def boundary_test_run_infer_dm_simple_snm(infer_dm_args):
    pytest.model = "snm_1d"
    pytest.nomisid = True
    pytest.output_prefix = "tests/test_results/main.test.snm.no.boundaries.demo_misid.params"
    pytest.p0 = -1
    pytest.ubounds = None
    pytest.lbounds = None
    dadi_cli.run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

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
    pytest.p0 = [1, 1]
    pytest.grids = [120, 140, 160]
    pytest.ubounds = [10, 10]
    pytest.lbounds = [1e-3, 1e-3]
    pytest.constants = -1
    pytest.nomisid = True
    pytest.cuda = False
    pytest.maxeval = 100
    pytest.maxtime = 300
    pytest.output_prefix = "tests/test_results/main.test.split_mig_fix_T."
    pytest.check_convergence = True
    pytest.force_convergence = False
    pytest.cpus = 1
    pytest.gpus = 0
    pytest.optimizations = 3
    pytest.bestfit_p0 = None
    pytest.delta_ll = 0.001
    pytest.global_optimization = False
    pytest.seed = None
    pytest.work_queue = []
    pytest.debug_wq = False
    pytest.port = 9123
    pytest.email = None

def test_run_infer_dfe_1d(infer_dfe_args):
    pytest.fs = pytest.fs_1d_lognorm
    pytest.pdf2d = None
    pytest.cache2d = None
    pytest.mix_pdf = None
    pytest.output_prefix += "1d_lognormal_dfe"
    dadi_cli.run_infer_dfe(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_dfe_1d_gamma(infer_dfe_args):
    pytest.fs = pytest.fs_1d_lognorm
    pytest.pdf1d = "gamma"
    pytest.pdf2d = None
    pytest.cache2d = None
    pytest.mix_pdf = None
    pytest.output_prefix += "1d_gamma_dfe"
    dadi_cli.run_infer_dfe(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_dfe_2d_lognormal(infer_dfe_args):
    pytest.fs = pytest.fs_2d_lognorm
    pytest.pdf1d = None
    pytest.cache1d = None
    pytest.mix_pdf = None
    pytest.output_prefix += "2d_lognormal_dfe"
    pytest.p0 = [1, 1, 0.5]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-3]
    dadi_cli.run_infer_dfe(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

def test_run_infer_dfe_mix(infer_dfe_args):
    pytest.fs = pytest.fs_2d_lognorm
    pytest.mix_pdf = 'mixture_lognormal'
    pytest.output_prefix += "mix_lognormal_dfe"
    pytest.p0 = [1, 1, 0, 0.5]
    pytest.ubounds = [10, 10, None, 0.999]
    pytest.lbounds = [1e-3, 1e-3, None, 1e-3]
    pytest.constants = [None, None, 0, None]
    dadi_cli.run_infer_dfe(pytest)
    fids = glob.glob(pytest.output_prefix+"*.opts.0")
    print(fids)
    opt = open(fids[-1],'r').readlines()
    print(opt)
    fix_check = [float(ele.split('\t')[3]) == 0.0 for ele in opt[2:]]
    for ele in fix_check:
        assert(ele)
    for fi in fids:
        os.remove(fi)

# May want third top_tops test to make sure log-likelihood sorted, but that would require changing the function
def test_top_opts_error():
    filename = "tests/example_data/_top_opts_test_files/top_opts.empty.txt"
    with pytest.raises(ValueError) as exc_info:
        dadi_cli._top_opts(filename)

    print(f"Fits not found in file {filename}.")
    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == f"Fits not found in file {filename}."

def test_top_opts_func():
    filename = "tests/example_data/_top_opts_test_files/top_opts.bestfits.txt"
    opts = dadi_cli._top_opts(filename)
    opt = list(opts[0])
    for ele in opts[1:]:
        assert opt != list(ele)

try:
    import work_queue as wq
    skip = False
except:
    skip = True

if os.path.exists("/home/runner/work/dadi-cli/dadi-cli"):
    skip = True

@pytest.mark.skipif(skip, reason="Could not load Work Queue or in GitAction environments")
def test_run_infer_dm_workqueue(infer_dm_args):
    import subprocess
    factory = subprocess.Popen(
        "work_queue_factory -T local -M pytest-dadi-cli -P ./tests/mypwfile --workers-per-cycle=0 --cores=1  -w 3 -W 3",
        shell=True,
    )
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo_wq.params"
    pytest.work_queue = ['pytest-dadi-cli', 'tests/mypwfile']
    dadi_cli.run_infer_dm(pytest)
    factory.kill()
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)








