import dadi
import pytest
import numpy as np
import os
from dadi_cli.GenerateFs import generate_fs


try:
    if not os.path.exists("./tests/test_results/bootstrap"):
        os.makedirs("./tests/test_results/bootstrap")
except:
    pass


@pytest.fixture
def data():
    pytest.vcf = "./tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf"
    pytest.pop_info = "./examples/data/1KG.YRI.CEU.popfile.txt"
    pytest.output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs"
    pytest.bootstrap_output = "./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short"
    pytest.singleton_mask_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.singleton_mask.fs"
    pytest.shared_singleton_mask_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.shared_singleton_mask.fs"
    pytest.marginalize_CEU_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.marginalize_CEU.fs"


def test_generate_fs(data):
    generate_fs(vcf=pytest.vcf, output=pytest.output, pop_ids=['YRI', 'CEU'], pop_info=pytest.pop_info, 
                projections=[216, 198], marginalize_pops=None, subsample=False, polarized=True, 
                bootstrap=None, chunk_size=None, masking='', seed=None)
    dadi.cli_fs = dadi.Spectrum.from_file(pytest.output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ['YRI','CEU'], [216,198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)

    assert np.allclose(dadi.cli_fs, dadi_fs)


def test_generate_fs_bootstrap(data):
    generate_fs(vcf=pytest.vcf, output=pytest.bootstrap_output, pop_ids=['YRI', 'CEU'], pop_info=pytest.pop_info, 
                projections=[216, 198], marginalize_pops=None, subsample=False, polarized=True, 
                bootstrap=10, chunk_size=100000, masking='', seed=123)

    for i in range(10):
        fs = dadi.Spectrum.from_file("./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."+str(i)+".fs")
        exp_fs = dadi.Spectrum.from_file("./tests/example_data/bootstrap_exp/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."+str(i)+".fs")
        assert np.allclose(fs, exp_fs)


def test_generate_fs_masks(data):
    generate_fs(vcf=pytest.vcf, output=pytest.singleton_mask_output, pop_ids=['YRI', 'CEU'], pop_info=pytest.pop_info, 
                projections=[216, 198], marginalize_pops=None, subsample=False, polarized=True, 
                bootstrap=None, chunk_size=None, masking='singletons', seed=None)
    dadi.cli_fs = dadi.Spectrum.from_file(pytest.singleton_mask_output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ['YRI','CEU'], [216,198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)
    dadi_fs.mask[1,0] = True
    dadi_fs.mask[-2,-1] = True
    dadi_fs.mask[0,1] = True
    dadi_fs.mask[-1,-2] = True

    assert np.allclose(dadi.cli_fs, dadi_fs)

    generate_fs(vcf=pytest.vcf, output=pytest.shared_singleton_mask_output, pop_ids=['YRI', 'CEU'], pop_info=pytest.pop_info, 
                projections=[216, 198], marginalize_pops=None, subsample=False, polarized=True, bootstrap=None, chunk_size=None, 
                masking='shared', seed=None)
    dadi.cli_fs = dadi.Spectrum.from_file(pytest.shared_singleton_mask_output)

    dadi_fs.mask[1,1] = True
    dadi_fs.mask[-2,-2] = True

    assert np.allclose(dadi.cli_fs, dadi_fs)


def test_generate_fs_marginalize(data):
    generate_fs(vcf=pytest.vcf, output=pytest.marginalize_CEU_output, pop_ids=['YRI', 'CEU'], pop_info=pytest.pop_info, 
                projections=[216, 198], marginalize_pops=['CEU'], subsample=False, polarized=True, 
                bootstrap=None, chunk_size=None, masking='', seed=None)
    dadi.cli_fs = dadi.Spectrum.from_file(pytest.marginalize_CEU_output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ['YRI','CEU'], [216,198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)
    dadi_fs = dadi_fs.marginalize([1])

    assert np.allclose(dadi.cli_fs, dadi_fs)
