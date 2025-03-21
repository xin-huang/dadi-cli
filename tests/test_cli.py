import pytest
import dadi_cli.__main__ as cli
import os, ast


try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


def test_generate_fs_args():
    parser = cli._dadi_cli_parser()
    cmd = "GenerateFs"
    vcf = "tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf"
    pop_infos = "tests/example_data/four.popfile.txt"
    output = "test.output"
    args = parser.parse_args(
        [
            cmd,
            "--vcf",
            vcf,
            "--pop-info",
            pop_infos,
            "--pop-ids",
            "YRI",
            "--projections",
            "216",
            "--output",
            output,
        ]
    )
    assert args.vcf == vcf
    assert args.pop_info == pop_infos
    assert args.pop_ids == ["YRI"]
    assert args.projections == [216]
    assert args.output == output


def test_generate_cache_args():
    parser = cli._dadi_cli_parser()
    cmd = "GenerateCache"
    model = "split_mig_fix_T_one_s"
    model_file = "tests/example_data/example_models.py"
    grids = [20, 40, 60]
    demo_popt = "tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    gamma_bounds = [1e-4, 10.0]
    gamma_pts = 5
    additional_gammas = []
    output = "tests/test_results/test.cache.bpkl"
    sample_sizes = [10, 10]
    cpus = 1
    gpus = 0
    cache_type = 'cache2d'

    args = parser.parse_args(
        [
            cmd,
            "--gamma-bounds",
            "1e-4", "10",
            "--gamma-pts",
            "5",
            "--cpus",
            "1",
            "--gpus",
            "0",
            "--sample-sizes",
            "10", "10",
            "--grids",
            "20", "40", "60",
            "--model-file",
            model_file,
            "--model",
            model,
            "--output",
            output,
            "--demo-popt",
            demo_popt,
            "--cache-type",
            cache_type,
        ]
    )
    assert args.gamma_bounds == gamma_bounds
    assert args.gamma_pts == gamma_pts
    assert args.cpus == cpus
    assert args.gpus == gpus
    assert args.sample_sizes == sample_sizes
    assert args.grids == grids
    assert args.model_file == model_file
    assert args.model == model
    assert args.output == output
    assert args.demo_popt == demo_popt
    assert args.additional_gammas == additional_gammas
    assert args.cache_type == cache_type


def test_simulate_dm_args():
    parser = cli._dadi_cli_parser()
    cmd = "SimulateDM"
    model = "two_epoch"
    model_file = None
    p0 = [1, 0.5]
    sample_sizes = [10]
    grids = [20, 30, 40]
    nomisid = True
    output = "tests/test_results/simulate_cli_two_epoch.fs"
    inference_file = True

    args = parser.parse_args(
        [
            cmd,
            "--model",
            model,
            "--p0",
            "1", "0.5",
            "--sample-sizes",
            "10",
            "--grids",
            "20", "30", "40",
            "--output",
            output,
            "--inference-file",
            "--nomisid"
        ]
    )

    assert args.model == model
    assert args.model_file == model_file
    assert args.p0 == p0
    assert args.sample_sizes == sample_sizes
    assert args.grids == grids
    assert args.nomisid == nomisid
    assert args.output == output
    assert args.inference_file == inference_file


def test_simulate_dfe_args():
    parser = cli._dadi_cli_parser()
    cmd = "SimulateDFE"
    cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pdf1d = "lognormal"
    pdf2d = "biv_lognormal"
    ratio = 2
    p0 = [1, 1.4, 0, 0.97, 0.02]
    nomisid = False
    output = "tests/test_results/simulate_cli_dfe_split_mig_mix_s_lognormal.fs"

    args = parser.parse_args(
        [
            cmd,
            "--cache1d",
            cache1d,
            "--cache2d",
            cache2d,
            "--pdf1d",
            pdf1d,
            "--pdf2d",
            pdf2d,
            "--ratio",
            str(ratio),
            "--p0",
            "1", "1.4", "0", "0.97", "0.02",
            "--output",
            output
        ]
    )

    assert args.cache1d == cache1d
    assert args.cache2d == cache2d
    assert args.pdf1d == pdf1d
    assert args.pdf2d == pdf2d
    assert args.ratio == ratio
    assert args.p0 == p0
    assert args.nomisid == nomisid
    assert args.output == output


try:
    import demes
    skip = False
except:
    skip = True


@pytest.mark.skipif(skip, reason="Could not load Demes")
def test_simulate_demes_args():
    parser = cli._dadi_cli_parser()
    cmd = "SimulateDemes"
    demes_file = "examples/data/gutenkunst_ooa.yml"
    sample_sizes = [10, 10, 10]
    grids = [20, 30, 40]
    pop_ids = ["YRI", "CEU", "CHB"]
    output = "tests/test_results/demes_gutenkunst_ooa_simulation.fs"

    args = parser.parse_args(
        [
            cmd,
            "--demes-file",
            demes_file,
            "--sample-sizes",
            "10", "10", "10",
            "--grids",
            "20", "30", "40",
            "--pop-ids",
            "YRI", "CEU", "CHB",
            "--output",
            output,
        ]
    )

    assert args.demes_file == demes_file
    assert args.sample_sizes == sample_sizes
    assert args.grids == grids
    assert args.pop_ids == pop_ids
    assert args.output == output


@pytest.mark.parametrize("model, model_file, nomisid",
    [
        ("split_mig_fix_T", "tests/example_data/example_models.py", False),
        ("snm_1d", None, True)
    ]
)
def test_infer_dm_args(model, model_file, nomisid):
    parser = cli._dadi_cli_parser()
    cmd = "InferDM"
    fs = "tests/example_data/two_epoch_syn.fs"
    p0 = [1, 1, 0.01, 1, 0.05]
    output_prefix = "tests/test_results/cli_test.split_mig.params"
    optimizations = 5
    check_convergence = True
    force_convergence = True
    work_queue = ["cli-test", "tests/mypwfile"]
    debug_wq = True
    maxeval = 100
    maxtime = 6000
    cpus = 5
    delta_ll = 0.01
    gpus = 0
    # model = "split_mig_fix_T"
    # model_file = "tests/example_data/example_models"
    grids = [130, 140, 150]
    # nomisid = False
    constants = "-1"
    lbounds = [0.01, 0.01, 0.0001, 0.1, 0.001]
    ubounds = [3, 3, 1, 3, 1]
    global_optimization = True
    seed = 12345

    args = parser.parse_args(
        [
            cmd,
            "--fs",
            fs,
            "--p0",
            "1", "1", "0.01", "1", "0.05",
            "--output-prefix",
            output_prefix,
            "--optimizations",
            str(optimizations),
            "--check-convergence", "5",
            "--force-convergence", "5",
            "--work-queue",
            "cli-test", "tests/mypwfile",
            "--debug-wq",
            "--maxeval",
            str(maxeval),
            "--maxtime",
            str(maxtime),
            "--cpus",
            str(cpus),
            "--delta-ll",
            str(delta_ll),
            "--gpus",
            str(gpus),
            "--model",
            model,
            "--model-file",
            model_file,
            "--grids",
            "130", "140", "150",
            "--lbounds",
            "0.01", "0.01", "0.0001", "0.1", "0.001",
            "--ubounds",
            "3", "3", "1", "3", "1",
            "--global-optimization",
            "--seed",
            str(seed),
        ]
    )

    assert args.fs == fs
    assert args.p0 == p0
    assert args.output_prefix == output_prefix
    assert args.optimizations == optimizations
    assert args.check_convergence == 5
    assert args.force_convergence == 5
    assert args.work_queue == ["cli-test", "tests/mypwfile"]
    assert args.debug_wq == True
    assert args.maxeval == maxeval
    assert args.maxtime == maxtime
    assert args.cpus == cpus 
    assert args.delta_ll == delta_ll
    assert args.gpus == gpus
    assert args.model == model
    #assert args.model_file == str(model_file)
    assert args.model_file == model_file
    assert args.grids == grids
    assert args.nomisid == False
    assert args.constants == -1
    assert [ast.literal_eval(ele) for ele in args.lbounds] == lbounds
    assert [ast.literal_eval(ele) for ele in args.ubounds] == ubounds
    assert args.global_optimization == True
    assert args.seed == seed


def test_infer_dfe_args():
    parser = cli._dadi_cli_parser()
    cmd = "InferDFE"
    fs_mix = "tests/example_data/split_mig_non_mix.fs"
    fs_1d_lognorm = "tests/example_data/split_mig_non_1d.fs"
    fs_2d_lognorm = "tests/example_data/split_mig_non_2d.fs"
    model = "split_mig_fix_T"
    model_file = "tests/example_data/example_models"
    demo_popt = "tests/example_data/example.split_mig_fix_T.demo.params.InferDM.bestfits"
    cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pdf1d = "lognormal"
    pdf2d = "biv_lognormal"
    mix_pdf = "mixture_lognormal"
    ratio = 2.31
    pdf_file = False
    p0 = [1, 1, 0, 0.001]
    grids = [120, 140, 160]
    ubounds = [5, 5, None, 0.999]
    lbounds = [1e-4, 1e-4, None, 1e-4]
    constants = [None, None, 0, None]
    nomisid = True
    cuda = False
    maxeval = 100
    maxtime = 300
    output_prefix = "tests/test_results/example.split_mig_fix_T."
    check_convergence = True
    force_convergence = False
    cpus = 1
    gpus = 0
    optimizations = 3
    bestfit_p0 = None
    delta_ll = 0.001
    seed = None
    work_queue = []
    debug_wq = False
    port = 9123
    seed = 12345

    args = parser.parse_args(
        [
            cmd,
            "--fs",
            fs_mix,
            "--demo-popt",
            demo_popt,
            "--cache1d",
            cache1d,
            "--cache2d",
            cache2d,
            "--pdf1d",
            pdf1d,
            "--pdf2d",
            pdf2d,
            "--mix-pdf",
            mix_pdf,
            "--ratio",
            str(ratio),
            "--p0",
            "1", "1", "0", "0.001",
            "--output-prefix",
            output_prefix,
            "--optimizations",
            str(optimizations),
            "--check-convergence", "3",
            "--force-convergence", "3",
            "--work-queue",
            "cli-dfe-test", "tests/mypwfile",
            "--debug-wq",
            "--maxeval",
            str(maxeval),
            "--maxtime",
            str(maxtime),
            "--cpus",
            str(cpus),
            "--delta-ll",
            str(delta_ll),
            "--gpus",
            str(gpus),
            "--delta-ll",
            str(delta_ll),
            "--nomisid",
            "--constants",
            "None", "None", "0", "None",
            "--lbounds",
            "1e-4", "1e-4", "None", "1e-4",
            "--ubounds",
            "5", "5", "None", "0.999",
            "--seed",
            str(seed),
        ]
    )

    assert args.fs == fs_mix
    assert args.p0 == p0
    assert args.output_prefix == output_prefix
    assert args.optimizations == optimizations
    assert args.check_convergence == 3
    assert args.force_convergence == 3
    assert args.work_queue == ["cli-dfe-test", "tests/mypwfile"]
    assert args.debug_wq == True
    assert args.maxeval == maxeval
    assert args.maxtime == maxtime
    assert args.cpus == cpus
    assert args.delta_ll == delta_ll
    assert args.gpus == gpus
    assert args.nomisid == True
    assert [ast.literal_eval(ele) for ele in args.constants] == constants
    assert [ast.literal_eval(ele) for ele in args.lbounds] == lbounds
    assert [ast.literal_eval(ele) for ele in args.ubounds] == ubounds
    assert args.seed == seed
    assert args.port == 9123
    assert args.pdf_file == None
    assert args.bestfit_p0 == None


def test_bestfit_args():
    parser = cli._dadi_cli_parser()
    cmd = "BestFit"
    input_prefix = "tests/example_data/example.split_mig.demo.params.InferDM"
    args = parser.parse_args(
        [
            cmd,
            "--input-prefix",
            input_prefix,
            "--lbounds",
            "1e-4", "1e-4", "1e-4", "1e-4",
            "--ubounds",
            "10", "10", "1", "5",
            "--delta-ll",
            "0.0001",
        ]
    )
    assert args.input_prefix == input_prefix
    assert args.lbounds == [1e-4, 1e-4, 1e-4, 1e-4]
    assert args.ubounds == [10, 10, 1, 5]
    assert args.delta_ll == 1e-4


def test_plot_args():
    parser = cli._dadi_cli_parser()
    cmd = "Plot"
    fs = "tests/example_data/split_mig_non_1d.fs"
    fs2 = "tests/example_data/split_mig_non_2d.fs"
    demo_popt = "tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    dfe_popt = "tests/example_data/example.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits"
    model = "split_mig"
    cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pdf1d = "lognormal"
    pdf2d = "biv_lognormal"
    output = "tests/test_results/plot_cli_test.png"
    projections = [10, 10]
    resid_range = 3
    vmin = 1e-5

    args = parser.parse_args(
        [
            cmd,
            "--fs",
            fs,
            "--fs2",
            fs2,
            "--demo-popt",
            demo_popt,
            "--dfe-popt",
            dfe_popt,
            "--model",
            model,
            "--cache1d",
            cache1d,
            "--cache2d",
            cache2d,
            "--pdf1d",
            pdf1d,
            "--pdf2d",
            pdf2d,
            "--output",
            output,
            "--projections",
            "10", "10",
            "--resid-range",
            str(resid_range),
            "--vmin",
            str(vmin),
        ]
    )

    assert args.fs == fs
    assert args.fs2 == fs2
    assert args.demo_popt == demo_popt
    assert args.dfe_popt == dfe_popt
    assert args.model == model
    assert args.cache1d == cache1d
    assert args.cache2d == cache2d
    assert args.pdf1d == pdf1d
    assert args.pdf2d == pdf2d
    assert args.output == output
    assert args.projections == projections
    assert args.resid_range == resid_range
    assert args.vmin == vmin


def test_stat_dm_args():
    parser = cli._dadi_cli_parser()
    cmd = "StatDM"
    fs = "tests/example_data/split_mig_syn.fs"
    model = "split_mig"
    grids = [60, 80, 100]
    output = "tests/test_results/example.cli.split_mig.demo.params.ci"
    constants = -1
    demo_popt = "tests/example_data/example.split_mig.demo.params.InferDM.bestfits"
    model_file = None
    bootstrapping_dir = "tests/example_data/split_mig_bootstrap_syn"
    logscale = True

    args = parser.parse_args(
        [
            cmd,
            "--fs",
            fs,
            "--model",
            model,
            "--grids",
            "60", "80", "100",
            "--output",
            output,
            "--demo-popt",
            demo_popt,
            "--bootstrapping-dir",
            bootstrapping_dir,
            "--logscale"
        ]
    )

    assert args.fs == fs
    assert args.model == model
    assert args.grids == grids
    assert args.output == output
    assert args.constants == constants
    assert args.demo_popt == demo_popt
    assert args.model_file == model_file
    assert args.bootstrapping_dir == bootstrapping_dir
    assert args.logscale == logscale


def test_stat_dfe_args():
    parser = cli._dadi_cli_parser()
    cmd = "StatDFE"
    fs = "tests/example_data/split_mig_non_mix.fs"
    cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    cache2d = "tests/example_data/cache_split_mig_2d.bpkl"
    pdf1d = "lognormal"
    pdf2d = "biv_lognormal"
    output = "./tests/test_results/example.split_mig.dfe.mixture_lognormal.params.ci"
    bootstrapping_synonymous_dir = "tests/example_data/split_mig_bootstrap_syn/"
    bootstrapping_nonsynonymous_dir = "tests/example_data/split_mig_bootstrap_non/bootstrap_non_mix/"
    dfe_popt = "tests/example_data/example.split_mig.dfe.lognormal_mixture.params.with.misid.InferDFE.bestfits"
    constants = [None, None, 0, None, None]
    logscale = False

    args = parser.parse_args(
        [
            cmd,
            "--fs",
            fs,
            "--cache1d",
            cache1d,
            "--cache2d",
            cache2d,
            "--pdf1d",
            pdf1d,
            "--pdf2d",
            pdf2d,
            "--output",
            output,
            "--constants",
            "None", "None", "0", "None", "None",
            "--dfe-popt",
            dfe_popt,
            "--bootstrapping-synonymous-dir",
            bootstrapping_synonymous_dir,
            "--bootstrapping-nonsynonymous-dir",
            bootstrapping_nonsynonymous_dir,
        ]
    )

    assert args.fs == fs
    assert args.cache1d == cache1d
    assert args.cache2d == cache2d
    assert args.pdf1d ==  pdf1d
    assert args.pdf2d == pdf2d
    assert args.output == output
    assert [ast.literal_eval(ele) for ele in args.constants] == constants
    assert args.dfe_popt == dfe_popt
    assert args.bootstrapping_syn_dir == bootstrapping_synonymous_dir
    assert args.bootstrapping_non_dir == bootstrapping_nonsynonymous_dir
    assert args.logscale == logscale


def test_model_args():
    parser = cli._dadi_cli_parser()
    cmd = "Model"
    args = parser.parse_args([cmd, "--names", "two_epoch"])
    assert args.names == "two_epoch"


def test_pdf_args():
    pass
