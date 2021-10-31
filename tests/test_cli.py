import pytest
import src.__main__ as cli

def test_generate_fs_args():
    parser = cli.dadi_cli_parser()
    cmd = "GenerateFs"
    vcf = "test.vcf"
    pop_infos = "test.info"
    output = "test.output"
    args = parser.parse_args([cmd, "--vcf", vcf, "--pop-info", pop_infos, "--pop-ids", "YRI", "--projections", "216", "--output", output])
    assert args.vcf == vcf
    assert args.pop_info == pop_infos
    assert args.pop_ids == ['YRI']
    assert args.projections == [216]
    assert args.output == output
