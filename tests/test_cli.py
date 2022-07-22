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
    pass


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
