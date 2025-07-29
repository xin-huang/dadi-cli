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
    pytest.woaa_vcf = "./tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.woanc.strict.short.vcf"
    pytest.pop_info = "./examples/data/1KG.YRI.CEU.popfile.txt"
    pytest.three_pop_info = "./tests/example_data/three.popfile.txt"
    pytest.four_pop_info = "./tests/example_data/four.popfile.txt"
    pytest.folded_output = (
        "./tests/test_results/1KG.YRI.CEU.synonymous.snps.fold.short.fs"
    )
    pytest.unfolded_output = (
        "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs"
    )
    pytest.subsample_output = (
        "./tests/test_results/1KG.YRI.CEU.synonymous.snps.subsample.unfold.short.fs"
    )
    pytest.bootstrap_output = (
        "./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short"
    )
    pytest.singleton_mask_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.singleton_mask.fs"
    pytest.shared_singleton_mask_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.shared_singleton_mask.fs"
    pytest.marginalize_CEU_output = "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.marginalize_CEU.fs"


def test_generate_fs(data):
    # Unfolded
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.unfolded_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.unfolded_output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ["YRI", "CEU"], [216, 198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)

    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Folded
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.folded_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=None,
        subsample=[],
        polarized=False,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.folded_output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ["YRI", "CEU"], [216, 198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns, polarized=False)

    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Projection
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.unfolded_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[30, 20],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.unfolded_output)

    assert dadi_cli_fs.sample_sizes[0] == 30
    assert dadi_cli_fs.sample_sizes[1] == 20

@pytest.mark.skip()
def test_generate_fs_failure(data):
    with pytest.raises(ValueError) as excinfo:
        generate_fs(
            vcf=pytest.vcf,
            output=pytest.unfolded_output,
            pop_ids=["YRI", "CEU"],
            pop_info=pytest.pop_info,
            projections=[216],
            marginalize_pops=None,
            subsample=[],
            polarized=True,
            bootstrap=None,
            chunk_size=None,
            masking="",
            calc_coverage=False,
            seed=None,
        )

    assert "The lengths of `pop_ids` and `projections` must match." in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        generate_fs(
            vcf=pytest.woaa_vcf,
            output=pytest.unfolded_output,
            pop_ids=["YRI", "CEU"],
            pop_info=pytest.pop_info,
            projections=[216, 198],
            marginalize_pops=None,
            subsample=[],
            polarized=True,
            bootstrap=None,
            chunk_size=None,
            masking="",
            calc_coverage=False,
            seed=None,
        )

    assert "The AA (Ancestral allele) INFO field cannot be found" in str(excinfo.value)


def test_generate_fs_subsample(data):
    pop_ids, projections = ["YRI", "CEU"], [216, 198]
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.subsample_output,
        pop_ids=pop_ids,
        pop_info=pytest.pop_info,
        projections=projections,
        marginalize_pops=None,
        subsample=[108, 99],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.subsample_output)

    subsample_dict = {
        "YRI": 108,
        "CEU": 99,
    }
    dd = dadi.Misc.make_data_dict_vcf(
        pytest.vcf, pytest.pop_info, subsample=subsample_dict
    )
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, projections, polarized=True)

    assert np.allclose(dadi_cli_fs, dadi_fs)


def test_generate_fs_bootstrap(data):
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.bootstrap_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=10,
        chunk_size=100000,
        masking="",
        calc_coverage=False,
        seed=123,
    )

    for i in range(10):
        fs = dadi.Spectrum.from_file(
            "./tests/test_results/bootstrap/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."
            + str(i)
            + ".fs"
        )
        exp_fs = dadi.Spectrum.from_file(
            "./tests/example_data/bootstrap_exp/1KG.YRI.CEU.synonymous.snps.unfold.short.bootstrapping."
            + str(i)
            + ".fs"
        )
        assert np.allclose(fs, exp_fs)


def test_generate_fs_masks(data):
    # Mask singletons in 1d sfs
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.marginalize_CEU_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=["CEU"],
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="singletons",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.marginalize_CEU_output)

    assert dadi_cli_fs.mask[1] == True
    assert dadi_cli_fs.mask[-2] == True

    # Mask singletons in 2d sfs
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.singleton_mask_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="singletons",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.singleton_mask_output)

    assert dadi_cli_fs.mask[1, 0] == True
    assert dadi_cli_fs.mask[-2, -1] == True
    assert dadi_cli_fs.mask[0, 1] == True
    assert dadi_cli_fs.mask[-1, -2] == True

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ["YRI", "CEU"], [216, 198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)
    dadi_fs.mask[1, 0] = True
    dadi_fs.mask[-2, -1] = True
    dadi_fs.mask[0, 1] = True
    dadi_fs.mask[-1, -2] = True

    assert np.allclose(dadi_cli_fs, dadi_fs)

    generate_fs(
        vcf=pytest.vcf,
        output=pytest.shared_singleton_mask_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="shared",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.shared_singleton_mask_output)

    assert dadi_cli_fs.mask[1, 0] == True
    assert dadi_cli_fs.mask[-2, -1] == True
    assert dadi_cli_fs.mask[0, 1] == True
    assert dadi_cli_fs.mask[-1, -2] == True
    assert dadi_cli_fs.mask[1, 1] == True
    assert dadi_cli_fs.mask[-2, -2] == True

    dadi_fs.mask[1, 1] = True
    dadi_fs.mask[-2, -2] = True

    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Mask singletons in 3d sfs
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.shared_singleton_mask_output,
        pop_ids=["pop0", "pop1", "pop2"],
        pop_info=pytest.three_pop_info,
        projections=[98, 216, 100],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="singletons",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.shared_singleton_mask_output)

    assert dadi_cli_fs.mask[1, 0, 0] == True
    assert dadi_cli_fs.mask[-2, -1, -1] == True
    assert dadi_cli_fs.mask[0, 1, 0] == True
    assert dadi_cli_fs.mask[-1, -2, -1] == True
    assert dadi_cli_fs.mask[0, 0, 1] == True
    assert dadi_cli_fs.mask[-1, -1, -2] == True

    generate_fs(
        vcf=pytest.vcf,
        output=pytest.shared_singleton_mask_output,
        pop_ids=["pop0", "pop1", "pop2"],
        pop_info=pytest.three_pop_info,
        projections=[98, 216, 100],
        marginalize_pops=None,
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="shared",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.shared_singleton_mask_output)

    assert dadi_cli_fs.mask[1, 1, 0] == True
    assert dadi_cli_fs.mask[1, 0, 1] == True
    assert dadi_cli_fs.mask[1, 1, 1] == True
    assert dadi_cli_fs.mask[-2, -2, -1] == True
    assert dadi_cli_fs.mask[-2, -1, -2] == True
    assert dadi_cli_fs.mask[-2, -2, -2] == True

    # Mask singletons in sfs with more than three populations.
    with pytest.raises(ValueError) as e_info:
        generate_fs(
            vcf=pytest.vcf,
            output=pytest.shared_singleton_mask_output,
            pop_ids=["pop0", "pop1", "pop2", "pop3"],
            pop_info=pytest.four_pop_info,
            projections=[98, 196, 100, 20],
            marginalize_pops=None,
            subsample=[],
            polarized=True,
            bootstrap=None,
            chunk_size=None,
            masking="shared",
            calc_coverage=False,
            seed=None,
        )

    assert (
        str(e_info.value)
        == "Masking singletons is only supported for a frequency spectrum with no more than 3 populations."
    )


def test_generate_fs_marginalize(data):
    generate_fs(
        vcf=pytest.vcf,
        output=pytest.marginalize_CEU_output,
        pop_ids=["YRI", "CEU"],
        pop_info=pytest.pop_info,
        projections=[216, 198],
        marginalize_pops=["CEU"],
        subsample=[],
        polarized=True,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=False,
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file(pytest.marginalize_CEU_output)

    dd = dadi.Misc.make_data_dict_vcf(pytest.vcf, pytest.pop_info)
    pop_ids, ns = ["YRI", "CEU"], [216, 198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)
    dadi_fs = dadi_fs.marginalize([1])

    assert np.allclose(dadi_cli_fs, dadi_fs)

    with pytest.raises(ValueError) as excinfo:
        generate_fs(
            vcf=pytest.vcf,
            output=pytest.marginalize_CEU_output,
            pop_ids=["YRI", "CEU"],
            pop_info=pytest.pop_info,
            projections=[216, 198],
            marginalize_pops=["CHB"],
            subsample=[],
            polarized=True,
            bootstrap=None,
            chunk_size=None,
            masking="",
            calc_coverage=False,
            seed=None,
        )

    assert "All populations to marginalize must be in the list of population ids." in str(excinfo.value)


def test_generate_fs_lowpass_dd(data):
    generate_fs(
        vcf="tests/example_data/LowPass-files/cov_gatk_Replicate_8_filtered_2D-GT-update.vcf",
        output="tests/test_results/cov-test.fs",
        pop_ids=["pop1", "pop2"],
        pop_info="tests/example_data/LowPass-files/cov_popfile_2D.txt",
        projections=[20, 20],
        marginalize_pops=None,
        subsample=[],
        polarized=False,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=[20, 20],
        seed=None,
    )
    import pickle
    cov_dist, nseq = pickle.load(open("tests/test_results/cov-test.fs.coverage.pickle", "rb"))

    assert nseq == [20, 20]

def test_generate_fs_lowpass_fs(data):
    generate_fs(
        vcf="tests/example_data/LowPass-files/cov_gatk_Replicate_8_filtered_2D-GT-update.vcf",
        output="tests/test_results/cov-test.fs",
        pop_ids=["pop1", "pop2"],
        pop_info="tests/example_data/LowPass-files/cov_popfile_2D.txt",
        projections=[20, 20],
        marginalize_pops=None,
        subsample=[],
        polarized=False,
        bootstrap=None,
        chunk_size=None,
        masking="",
        calc_coverage=[20, 20],
        seed=None,
    )
    dadi_cli_fs = dadi.Spectrum.from_file("tests/test_results/cov-test.fs")

    dd = dadi.Misc.make_data_dict_vcf("tests/example_data/LowPass-files/cov_gatk_Replicate_8_filtered_2D-GT-update.vcf", "tests/example_data/LowPass-files/cov_popfile_2D.txt", calc_coverage=True)
    pop_ids, ns = ["pop1", "pop2"], [20, 20]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns, polarized=False)

    assert np.allclose(dadi_cli_fs, dadi_fs)


