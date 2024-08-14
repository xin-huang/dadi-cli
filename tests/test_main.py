import glob, os, pytest

from dadi_cli.parsers.generate_fs_parsers import _run_generate_fs
from dadi_cli.parsers.generate_cache_parsers import _run_generate_cache
from dadi_cli.parsers.simulate_dm_parsers import _run_simulate_dm
from dadi_cli.parsers.simulate_dfe_parsers import _run_simulate_dfe
from dadi_cli.parsers.simulate_demes_parsers import _run_simulate_demes
from dadi_cli.parsers.infer_dm_parsers import _run_infer_dm
from dadi_cli.parsers.infer_dfe_parsers import _run_infer_dfe
from dadi_cli.parsers.stat_dm_parsers import _run_stat_demography
from dadi_cli.parsers.stat_dfe_parsers import _run_stat_dfe
from dadi_cli.parsers.model_parsers import _run_model
from dadi_cli.parsers.pdf_parsers import _run_pdf
from dadi_cli.parsers.plot_parsers import _run_plot
from dadi_cli.parsers.common_arguments import make_dir

from dadi_cli.GenerateFs import *
from dadi_cli.GenerateCache import *
from dadi_cli.InferDM import *
from dadi_cli.InferDFE import *
from dadi_cli.Pdfs import *
from dadi_cli.Models import *
from dadi_cli.utilities import *

from importlib.metadata import version


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
    gen_fs_args.subsample = []
    gen_fs_args.mask_shared = False
    gen_fs_args.calc_coverage = False
    gen_fs_args.mask = False

    _run_generate_fs(gen_fs_args)
    gen_fs_args.mask = True
    _run_generate_fs(gen_fs_args)
    gen_fs_args.mask_shared = True
    _run_generate_fs(gen_fs_args)
    # Test LowPass
    gen_fs_args.vcf = "tests/example_data/LowPass-files/cov_gatk_Replicate_8_filtered_2D-GT-update.vcf"
    gen_fs_args.pop_info = "tests/example_data/LowPass-files/cov_popfile_2D.txt"
    gen_fs_args.pop_ids = ["pop1", "pop2"]
    gen_fs_args.polarized = False
    gen_fs_args.calc_coverage = True
    _run_generate_fs(gen_fs_args)
    os.remove(gen_fs_args.output)
    os.remove(gen_fs_args.output+".coverage.pickle")


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

    _run_simulate_dm(simulate_args)
    os.remove(simulate_args.output)


def test_run_simulate_dm_html():
    def simulate_args():
        return
    simulate_args.model = "three_epoch_bottleneck"
    simulate_args.model_file = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example_models.py"
    simulate_args.p0 = [1, 0.5, 0.05]
    simulate_args.sample_sizes = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.nomisid = False
    simulate_args.output = "tests/test_results/main_simulate_three_epoch_bottleneck_html.fs"
    simulate_args.inference_file = False

    _run_simulate_dm(simulate_args)
    os.remove(simulate_args.output)


try:
    import demes
    demesskip = False
except:
    demesskip = True


@pytest.mark.skipif(demesskip, reason="Could not load demes")
def test_run_simulate_demes():
    def simulate_args():
        return
    simulate_args.demes_file = "examples/data/gutenkunst_ooa.yml"
    simulate_args.pop_ids = ["YRI"]
    simulate_args.sample_sizes = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.output = "tests/test_results/main_simulate_demes_ooa.fs"

    _run_simulate_demes(simulate_args)
    os.remove(simulate_args.output)


@pytest.mark.skipif(demesskip, reason="Could not load demes")
def test_run_simulate_demes_html():
    def simulate_args():
        return
    simulate_args.demes_file = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/examples/data/gutenkunst_ooa.yml"
    simulate_args.pop_ids = ["YRI"]
    simulate_args.sample_sizes = [10]
    simulate_args.grids = [20, 30, 40]
    simulate_args.output = "tests/test_results/main_simulate_demes_ooa_html.fs"

    _run_simulate_demes(simulate_args)
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

    _run_simulate_dfe(simulate_args)
    os.remove(simulate_args.output)


def test_run_simulate_dfe_html():
    def simulate_args():
        return
    simulate_args.p0 = [1, 1.5, 0, 0.01, 0.05]
    simulate_args.cache1d = "https://github.com/xin-huang/dadi-cli/blob/master/tests/example_data/cache_split_mig_1d.bpkl?raw=true"
    simulate_args.cache2d = "https://github.com/xin-huang/dadi-cli/blob/master/tests/example_data/cache_split_mig_2d.bpkl?raw=true"
    simulate_args.pdf1d = "lognormal"
    simulate_args.pdf2d = "biv_lognormal"
    simulate_args.ratio = 2.31
    simulate_args.nomisid = False
    simulate_args.output = "tests/test_results/main_simulate_mix_dfe_html.fs"

    _run_simulate_dfe(simulate_args)
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

    _run_generate_cache(generate_cache_args)
    os.remove(generate_cache_args.output)


def test_run_generate_cache_html():
    def generate_cache_args():
        return
    generate_cache_args.model = "split_mig_fix_T_one_s"
    generate_cache_args.model_file = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example_models.py"
    generate_cache_args.grids = [20, 40, 60]
    generate_cache_args.demo_popt = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    generate_cache_args.gamma_bounds = (1e-4, 10)
    generate_cache_args.gamma_pts = 5
    generate_cache_args.additional_gammas = []
    generate_cache_args.output = "tests/test_results/test.html.cache.bpkl"
    generate_cache_args.sample_sizes = [10, 10]
    generate_cache_args.cpus = 1
    generate_cache_args.gpus = 0
    generate_cache_args.dimensionality = 1

    _run_generate_cache(generate_cache_args)
    os.remove(generate_cache_args.output)


@pytest.fixture
def infer_dm_args():
    pytest.fs = "tests/example_data/two_epoch_syn.fs"
    pytest.model = "three_epoch_bottleneck"
    pytest.model_file = "tests/example_data/example_models"
    pytest.p0 = [1, 0.5]
    pytest.grids = [30, 40, 50]
    pytest.ubounds = [10, 10]
    pytest.lbounds = [1e-3, 1e-3]
    pytest.constants = -1
    pytest.nomisid = True
    pytest.cov_args = []
    pytest.cov_inbreeding = []
    pytest.cuda = False
    pytest.maxeval = 200
    pytest.maxtime = 200
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo.params"
    pytest.check_convergence = 1
    pytest.force_convergence = 0
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
    _run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


@pytest.mark.parametrize("check_convergence, force_convergence, optimizations",
    [
        (10, 0, 5),
        (0, 15, 5)
    ]
)
def test_run_infer_dm_convergence(check_convergence, force_convergence, optimizations, infer_dm_args, recwarn):
    pytest.model = "two_epoch"
    pytest.model_file = None
    pytest.check_convergence = check_convergence
    pytest.force_convergence = force_convergence
    pytest.optimizations = optimizations
    pytest.output_prefix += ".convergence_update"

    _run_infer_dm(pytest)

    if check_convergence > optimizations:
        w = recwarn.pop(UserWarning)
        assert str(w.message) == "WARNING: Number of optimizations is less than the number requested before checking convergence. Convergence will not be checked. \n" +\
            "Note: if using --global-optimization, ~25% of requested optimizations are used for the gloabal optimization.\n"
        assert len([ele for ele in open(pytest.output_prefix+".InferDM.opts.0", "r").readlines() if not ele.startswith("#")]) == optimizations

    if force_convergence > 0:
        assert len([ele for ele in open(pytest.output_prefix+".InferDM.opts.0", "r").readlines() if not ele.startswith("#")]) >= force_convergence

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
    pytest.output_prefix += ".no_custom_model"
    _run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


def test_run_infer_dm_misid(infer_dm_args):
    pytest.nomisid = False
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo_misid.params"
    pytest.p0 = [1, 0.5, 1e-2]
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    _run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)

# Test LowPass
def test_run_infer_dm_lowpass(infer_dm_args):
    pytest.cov_args = ["tests/example_data/LowPass-files/cov.fs.coverage.pickle", 20, 20]
    pytest.fs = "tests/example_data/LowPass-files/cov.fs"
    pytest.model = "split_mig"
    pytest.model_file = None
    pytest.output_prefix = "tests/test_results/main.test.split_mig.demo_lowpass.params"
    pytest.p0 = [1, 1, 0.1, 1]
    pytest.ubounds = [10, 10, 1, 10]
    pytest.lbounds = [1e-3, 1e-3, 1e-3, 1e-3]
    _run_infer_dm(pytest)
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
    _run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


def boundary_test_run_infer_dm_simple_snm(infer_dm_args):
    pytest.model = "snm_1d"
    pytest.nomisid = True
    pytest.output_prefix = "tests/test_results/main.test.snm.no.boundaries.demo_misid.params"
    pytest.p0 = -1
    pytest.ubounds = None
    pytest.lbounds = None
    _run_infer_dm(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


def test_run_infer_dm_html(infer_dm_args):
    pytest.fs = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/two_epoch_syn.fs"
    pytest.model = "three_epoch_bottleneck"
    pytest.model_file = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example_models.py"
    pytest.bestfit_p0 = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example.bestfit.two_epoch.demo.params.InferDM.opts.0"
    pytest.nomisid = False
    pytest.ubounds = [10, 10, 0.999]
    pytest.lbounds = [1e-3, 1e-3, 1e-4]
    pytest.output_prefix += ".html"
    _run_infer_dm(pytest)
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
    pytest.cov_args = []
    pytest.cov_inbreeding = []
    pytest.cuda = False
    pytest.maxeval = 100
    pytest.maxtime = 300
    pytest.output_prefix = "tests/test_results/main.test.split_mig_fix_T."
    pytest.check_convergence = 1
    pytest.force_convergence = 0
    pytest.cpus = 1
    pytest.gpus = 0
    pytest.optimizations = 5
    pytest.bestfit_p0 = None
    pytest.delta_ll = 0.001
    pytest.global_optimization = False
    pytest.seed = None
    pytest.work_queue = []
    pytest.debug_wq = False
    pytest.port = 9123


def test_run_infer_dfe_1d(infer_dfe_args):
    pytest.fs = pytest.fs_1d_lognorm
    pytest.pdf2d = None
    pytest.cache2d = None
    pytest.mix_pdf = None
    pytest.output_prefix += "1d_lognormal_dfe"
    _run_infer_dfe(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


@pytest.mark.parametrize("check_convergence, force_convergence, optimizations",
    [
        (10, 0, 5),
        (0, 15, 5)
    ]
)
def test_run_infer_dfe_convergence(check_convergence, force_convergence, optimizations, infer_dfe_args, recwarn):
    pytest.fs = pytest.fs_1d_lognorm
    pytest.pdf2d = None
    pytest.cache2d = None
    pytest.mix_pdf = None

    pytest.check_convergence = check_convergence
    pytest.force_convergence = force_convergence
    pytest.optimizations = optimizations
    pytest.output_prefix += "1d_lognormal_dfe.convergence_update"

    _run_infer_dfe(pytest)

    if check_convergence > optimizations:
        w = recwarn.pop(UserWarning)
        assert str(w.message) == "WARNING: Number of optimizations is less than the number requested before checking convergence. Convergence will not be checked. \n" +\
            "Note: if using --global-optimization, ~25% of requested optimizations are used for the gloabal optimization.\n"
        assert len([ele for ele in open(pytest.output_prefix+".InferDFE.opts.0", "r").readlines() if not ele.startswith("#")]) == optimizations

    if force_convergence > 0:
        assert len([ele for ele in open(pytest.output_prefix+".InferDFE.opts.0", "r").readlines() if not ele.startswith("#")]) >= force_convergence

    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


def test_run_infer_dfe_1d_gamma(infer_dfe_args):
    pytest.fs = pytest.fs_1d_lognorm
    pytest.pdf1d = "gamma"
    pytest.pdf2d = None
    pytest.cache2d = None
    pytest.mix_pdf = None
    pytest.output_prefix += "1d_gamma_dfe"

    _run_infer_dfe(pytest)
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

    _run_infer_dfe(pytest)
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

    _run_infer_dfe(pytest)
    fids = glob.glob(pytest.output_prefix+"*")
    print(fids)
    opt = open(fids[-1],'r').readlines()
    fix_check = [float(ele.split('\t')[3]) == 0.0 for ele in opt if not ele.startswith("#")]
    for ele in fix_check:
        assert(ele)
    for fi in fids:
        os.remove(fi)


def test_run_infer_dfe_mix_html(infer_dfe_args):
    pytest.fs = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/split_mig_non_2d.fs"
    pytest.demo_popt = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    pytest.cache1d = "https://github.com/xin-huang/dadi-cli/blob/master/tests/example_data/cache_split_mig_1d.bpkl?raw=true"
    pytest.cache2d = "https://github.com/xin-huang/dadi-cli/blob/master/tests/example_data/cache_split_mig_2d.bpkl?raw=true"
    pytest.bestfit_p0 = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example.split_mig.dfe.lognormal_mixture.params.with.misid.InferDFE.bestfits"
    pytest.mix_pdf = 'mixture_lognormal'
    pytest.output_prefix += "mix_lognormal_dfe_html"
    pytest.nomisid = False
    # pytest.p0 = None
    pytest.ubounds = [10, 10, None, 0.999, 0.4]
    pytest.lbounds = [1e-3, 1e-3, None, 1e-3, 1e-3]
    pytest.constants = [None, None, 0, None, None]

    _run_infer_dfe(pytest)
    fids = glob.glob(pytest.output_prefix+"*")
    opt = open(fids[-1],'r').readlines()
    fix_check = [float(ele.split('\t')[3]) == 0.0 for ele in opt if not ele.startswith("#")]
    for ele in fix_check:
        assert(ele)
    for fi in fids:
        os.remove(fi)


# Test LowPass
@pytest.mark.skip(reason="Finish later")
def test_run_infer_dfe_lowpass(infer_dm_args):
    pytest.cov_args = ["tests/example_data/LowPass-files/cov.fs.coverage.pickle", 20, 20]
    pytest.fs = "tests/example_data/LowPass-files/cov.fs"
    # pytest.model = "split_mig"
    # pytest.model_file = None
    pytest.output_prefix = "tests/test_results/main.test.split_mig.dfe_lowpass.params"
    # pytest.p0 = [1, 1, 0.1, 1]
    # pytest.ubounds = [10, 10, 1, 10]
    # pytest.lbounds = [1e-3, 1e-3, 1e-3, 1e-3]
    _run_infer_dfe(pytest)
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


# May want third top_tops test to make sure log-likelihood sorted, but that would require changing the function
def test_top_opts_error():
    filename = "tests/example_data/_top_opts_test_files/top_opts.empty.txt"
    with pytest.raises(ValueError) as exc_info:
        top_opts(filename)

    print(f"Fits not found in file {filename}.")
    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == f"Fits not found in file {filename}."


def test_top_opts_func():
    filename = "tests/example_data/_top_opts_test_files/top_opts.bestfits.txt"
    opts = top_opts(filename)
    opt = list(opts[0])
    for ele in opts[1:]:
        assert opt != list(ele)


try:
    import work_queue as wq
    wqskip = False
except:
    wqskip = True

if os.path.exists("/home/runner/work/dadi-cli/dadi-cli"):
    wqskip = True


@pytest.mark.skipif(wqskip, reason="Could not load Work Queue or in GitAction environments")
def test_run_infer_dm_workqueue(infer_dm_args):
    import subprocess
    factory = subprocess.Popen(
        "work_queue_factory -T local -M pytest-dadi-cli -P ./tests/mypwfile --workers-per-cycle=0 --cores=1  -w 3 -W 3",
        shell=True,
    )
    pytest.output_prefix = "tests/test_results/main.test.two_epoch.demo_wq.params"
    pytest.work_queue = ['pytest-dadi-cli', 'tests/mypwfile']

    _run_infer_dm(pytest)
    factory.kill()
    for ele in glob.glob(pytest.output_prefix+"*"):
        os.remove(ele)


def test_run_stat_demography():
    def stat_args():
        return
    stat_args.fs="tests/example_data/split_mig_syn.fs"
    stat_args.model="split_mig"
    stat_args.model_file=None
    stat_args.bootstrapping_dir="tests/example_data/split_mig_bootstrap_syn/"
    stat_args.grids=[30, 40, 50]
    stat_args.nomisid=True
    stat_args.demo_popt="tests/example_data/example.split_mig.demo.params.InferDM.bestfits"
    stat_args.constants=-1
    stat_args.logscale=False
    stat_args.output="tests/test_results/main_demo_godambe.txt"
    stat_args.eps=[0.1]

    _run_stat_demography(stat_args)
    os.remove(stat_args.output)


def test_run_stat_dfe():
    def stat_args():
        return
    stat_args.fs="tests/example_data/split_mig_non.fs"
    stat_args.model="split_mig"
    stat_args.model_file=None
    stat_args.cache1d="tests/example_data/cache_split_mig_1d.bpkl"
    stat_args.cache2d=None
    stat_args.pdf1d="lognormal"
    stat_args.pdf2d=None
    stat_args.bootstrapping_syn_dir="tests/example_data/split_mig_bootstrap_syn/"
    stat_args.bootstrapping_non_dir="tests/example_data/split_mig_bootstrap_non/bootstrap_non_1d/"
    stat_args.grids=[30, 40, 50]
    stat_args.nomisid=True
    stat_args.dfe_popt="tests/example_data/example.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits"
    stat_args.constants=-1
    stat_args.logscale=False
    stat_args.output="tests/test_results/main_dfe_godambe.txt"
    stat_args.eps=[0.1]

    _run_stat_dfe(stat_args)
    os.remove(stat_args.output)


@pytest.fixture
def plot_args():
    pytest.model = "split_mig"
    # pytest.fs1_1d = "tests/example_data/two_epoch_syn.fs"
    # pytest.fs2_1d = "tests/example_data/two_epoch_non.fs"
    pytest.pdf1d = "lognormal"
    pytest.pdf2d = "biv_lognormal"
    pytest.output = "tests/test_results/main_test_plot.pdf"
    # pytest.demo_popt = "tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    # pytest.fs1d_cache1d = "tests/example_data/cache_two_epoch_1d.bpkl"
    pytest.fs = "tests/example_data/split_mig_syn.fs"
    pytest.fs2 = "tests/example_data/split_mig_non_1d.fs"
    # plot_args.fs2_2d = "tests/example_data/split_mig_non_2d.fs"
    # plot_args.fs_mixture = "tests/example_data/split_mig_non_mix.fs"
    pytest.demo_popt = "tests/example_data/example.split_mig.demo.params.InferDM.bestfits"
    pytest.dfe_popt = "tests/example_data/example.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits"
    pytest.cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    pytest.cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pytest.vmin = 1e-3
    pytest.resid_range = 10
    pytest.projections = None
    pytest.model_file = None
    pytest.interactive = False


def test_plot_mut_prop(plot_args):
    pytest.fs = None

    _run_plot(pytest)
    os.remove(pytest.output)


def test_plot_fitted_dfe(plot_args):
    _run_plot(pytest)
    os.remove(pytest.output)


def test_plot_fitted_demography(plot_args):
    pytest.dfe_popt = None

    _run_plot(pytest)
    os.remove(pytest.output)

# Unit test code start incase html functionality for Plot is requested
# def test_plot_fitted_demography_html(plot_args):
#     pytest.dfe_popt = None
#     pytest.fs = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/two_epoch_syn.fs"
#     pytest.model = "three_epoch_bottleneck"
#     pytest.model_file = "https://raw.githubusercontent.com/xin-huang/dadi-cli/master/tests/example_data/example_models.py"
#     pytest.demo_popt
#     dcli.run_plot(pytest)
#     # os.remove(pytest.output)


@pytest.mark.skipif(version('dadi') <= '2.3.3', reason="Version of dadi doesn't support interactive plot display for single SFS")
def test_plot_single_sfs(plot_args):
    pytest.dfe_popt = None
    pytest.demo_popt = None
    pytest.fs2 = None

    _run_plot(pytest)
    os.remove(pytest.output)

def test_plot_comparison(plot_args):
    pytest.dfe_popt = None
    pytest.demo_popt = None

    _run_plot(pytest)
    os.remove(pytest.output)

@pytest.mark.parametrize("dir_path, dir_exists",
    [
        ("fake.fs", False),
        ("tests/test_results/make_dir/fake.fs", True)
    ]
)
def test_make_dir(dir_path, dir_exists):
    make_dir(dir_path)
    parent_dir = os.path.dirname(dir_path)
    assert os.path.exists(parent_dir) == dir_exists
    if os.path.exists(parent_dir):
        os.rmdir(parent_dir)
