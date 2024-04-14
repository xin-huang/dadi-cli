import dadi
import dadi.DFE as DFE
import pickle
import pytest
import os
import numpy as np
from dadi_cli.SimulateFs import simulate_demography
from dadi_cli.SimulateFs import simulate_dfe
from dadi_cli.SimulateFs import simulate_demes
from dadi_cli.Pdfs import get_dadi_pdf


try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


def test_simulate_demography_code():
    model = "two_epoch"
    model_file = None
    p0 = [1, 0.5]
    ns = [10]
    pts_l = [20, 30, 40]
    misid = False
    output = "tests/test_results/simulate_two_epoch.fs"
    inference_file = False
    simulate_demography(
        model=model, 
        model_file=model_file, 
        p0=p0, 
        ns=ns, 
        pts_l=pts_l, 
        misid=misid, 
        output=output, 
        inference_file=inference_file
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output)
    dadi_fs = dadi.Numerics.make_extrap_func(dadi.Demographics1D.two_epoch)(
        p0, ns, pts_l
    )
    assert np.allclose(dadi_cli_fs, dadi_fs)

def test_simulate_custom_demography_code():
    model = "three_epoch_bottleneck"
    model_file = "tests/example_data/example_models"
    p0 = [1, 0.5]
    ns = [10]
    pts_l = [20, 30, 40]
    misid = False
    output = "tests/test_results/simulate_three_epoch_bottleneck.fs"
    inference_file = False
    simulate_demography(
        model=model, 
        model_file=model_file, 
        p0=p0, 
        ns=ns, 
        pts_l=pts_l, 
        misid=misid, 
        output=output, 
        inference_file=inference_file
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output)
    from tests.example_data.example_models import three_epoch_bottleneck
    dadi_fs = dadi.Numerics.make_extrap_func(three_epoch_bottleneck)(
        p0, ns, pts_l
    )
    assert np.allclose(dadi_cli_fs, dadi_fs)

def test_simulate_demography_misid_code():
    model = "two_epoch"
    model_file = None
    p0 = [1, 0.5, 0.1]
    ns = [10]
    pts_l = [20, 30, 40]
    misid = True
    output = "tests/test_results/simulate_two_epoch_with_misid.fs"
    inference_file = True
    simulate_demography(
        model=model, 
        model_file=model_file, 
        p0=p0, 
        ns=ns, 
        pts_l=pts_l, 
        misid=misid, 
        output=output, 
        inference_file=inference_file
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output)
    dadi_fs = dadi.Numerics.make_extrap_func(
        dadi.Numerics.make_anc_state_misid_func(dadi.Demographics1D.two_epoch)
    )(p0, ns, pts_l)
    assert np.allclose(dadi_cli_fs, dadi_fs)
    assert os.path.exists("tests/test_results/simulate_two_epoch_with_misid.fs.SimulateDM.pseudofit")


def test_simulate_dfe_code():
    p0_1d = [1, 1.5]
    p0_2d = [1, 1.2, 0.9]
    p0_mix = [1, 1.4, 0, 0.97]
    p0_1d_misid = [1, 1.5, 0.02]
    cache1d = pickle.load(open("tests/example_data/cache_split_mig_1d.bpkl", "rb"))
    cache2d = pickle.load(open("tests/example_data/cache_split_mig_2d.bpkl", "rb"))
    sele_dist = "lognormal"
    sele_dist2 = "biv_lognormal"
    theta_ns = 2.31
    misid = False
    output_1d = "tests/test_results/simulate_dfe_split_mig_one_s_lognormal.fs"
    output_2d = "tests/test_results/simulate_dfe_split_mig_two_s_lognormal.fs"
    output_mix = "tests/test_results/simulate_dfe_split_mig_mix_s_lognormal.fs"
    output_1d_misid = (
        "tests/test_results/simulate_dfe_split_mig_one_s_lognormal_misid.fs"
    )

    # Test 1D
    simulate_dfe(p0_1d, cache1d, None, sele_dist, None, theta_ns, misid, output_1d)
    dadi_cli_fs = dadi.Spectrum.from_file(output_1d)
    dadi_fs = cache1d.integrate(p0_1d, None, get_dadi_pdf(sele_dist), theta_ns)
    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Test 2D
    simulate_dfe(p0_2d, None, cache2d, None, sele_dist2, theta_ns, misid, output_2d)
    dadi_cli_fs = dadi.Spectrum.from_file(output_2d)
    dadi_fs = cache2d.integrate(p0_2d, None, get_dadi_pdf(sele_dist2), theta_ns, None)
    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Test mix
    simulate_dfe(
        p0_mix, cache1d, cache2d, sele_dist, sele_dist2, theta_ns, misid, output_mix
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output_mix)
    dadi_fs = DFE.mixture(
        p0_mix,
        None,
        cache1d,
        cache2d,
        get_dadi_pdf(sele_dist),
        get_dadi_pdf(sele_dist2),
        theta_ns,
        None,
    )
    assert np.allclose(dadi_cli_fs, dadi_fs)

    # Test 1D misid
    simulate_dfe(
        p0_1d_misid, cache1d, None, sele_dist, None, theta_ns, True, output_1d_misid
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output_1d_misid)
    dadi_fs = dadi.Numerics.make_anc_state_misid_func(cache1d.integrate)(
        p0_1d_misid, None, get_dadi_pdf(sele_dist), theta_ns
    )
    assert np.allclose(dadi_cli_fs, dadi_fs)

try:
    import demes
    skip = False
except:
    skip = True

@pytest.mark.skipif(skip, reason="Could not load Demes")
def test_simulate_demes_code():
    demes_file = "examples/data/gutenkunst_ooa.yml"
    ns = [10, 10, 10]
    pts_l = [20, 30, 40]
    pop_ids = ["YRI", "CEU", "CHB"]
    output = "tests/test_results/demes_gutenkunst_ooa_simulation.fs"
    simulate_demes(
        demes_file=demes_file, 
        ns=ns, 
        pts_l=pts_l, 
        pop_ids=pop_ids, 
        output=output
    )
    dadi_cli_fs = dadi.Spectrum.from_file(output)
    dadi_fs = dadi.Spectrum.from_demes(
        demes_file, sampled_demes=pop_ids, sample_sizes=ns, pts=pts_l
    )
    assert np.allclose(dadi_cli_fs, dadi_fs)
