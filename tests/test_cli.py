import pytest
import dadi_cli.__main__ as cli
import os

try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


def test_generate_fs_args():
    parser = cli.dadi_cli_parser()
    cmd = "GenerateFs"
    vcf = "test.vcf"
    pop_infos = "test.info"
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
    pass


def test_infer_dm_args():
    parser = cli.dadi_cli_parser()
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
    threads = 5
    delta_ll = 0.01
    cuda = True
    model = "split_mig_fix_T"
    model_file = "tests/example_data/example_models"
    grids = [130, 140, 150]
    nomisid = False
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
            "--check-convergence",
            "--force-convergence",
            "--work-queue",
            "cli-test", "tests/mypwfile",
            "--debug-wq",
            "--maxeval",
            str(maxeval),
            "--maxtime",
            str(maxtime),
            "--threads",
            str(threads),
            "--delta-ll",
            str(delta_ll),
            "--cuda",
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
    assert args.check_convergence == True
    assert args.force_convergence == True
    assert args.work_queue == ["cli-test", "tests/mypwfile"]
    assert args.debug_wq == True
    assert args.maxeval == maxeval
    assert args.maxtime == maxtime
    assert args.threads == threads
    assert args.delta_ll == delta_ll
    assert args.cuda == True
    assert args.model == model
    assert args.model_file == model_file
    assert args.grids == grids
    assert args.nomisid == False
    assert args.constants == -1
    assert args.lbounds == lbounds
    assert args.ubounds == ubounds
    assert args.global_optimization == True
    assert args.seed == seed


def test_infer_dfe_args():
    pass


def test_bestfit_args():
    pass


def test_plot_args():
    pass


def test_stat_args():
    pass


def test_model_args():
    parser = cli.dadi_cli_parser()
    cmd = "Model"
    args = parser.parse_args([cmd, "--names", "two_epoch"])
    assert args.names == "two_epoch"


def test_pdf_args():
    pass
