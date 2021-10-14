import dadi
import pytest
import numpy as np
from src.GenerateFs import generate_fs

@pytest.fixture
def data():
    pytest.vcf = "./tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf"
    pytest.pop_info = "./examples/data/1KG.YRI.CEU.popfile.txt"
    pytest.output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs"
    pytest.bootstrap_output = "./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short"

def test_generate_fs(data):
    generate_fs(pytest.vcf, pytest.output, ['YRI', 'CEU'], pytest.pop_info, [216, 198], True, None, 100000, None)
    dadi.cli_fs = dadi.Spectrum.from_file('./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs')

    datafile = './tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf'
    popfile = './examples/data/1KG.YRI.CEU.popfile.txt'
    dd = dadi.Misc.make_data_dict_vcf(datafile, popfile)
    pop_ids, ns = ['YRI','CEU'], [216,198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)

    assert np.allclose(dadi.cli_fs, dadi_fs)

def test_generate_fs_bootstrap(data):
    generate_fs(pytest.vcf, pytest.bootstrap_output, ['YRI', 'CEU'], pytest.pop_info, [216, 198], True, 10, 100000, 123)

    for i in range(10):
        fs = dadi.Spectrum.from_file("./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."+str(i)+".fs")
        exp_fs = dadi.Spectrum.from_file("./tests/test_results/bootstrap_exp/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."+str(i)+".fs")
        assert np.allclose(fs, exp_fs)
