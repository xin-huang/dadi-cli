import dadi
import glob
import matplotlib
import pytest
import subprocess
from dadi_cli.Plot import plot_single_sfs
from dadi_cli.Plot import plot_comparison
from dadi_cli.Plot import plot_fitted_demography
from dadi_cli.Plot import plot_fitted_dfe
from dadi_cli.Plot import plot_mut_prop
import os

matplotlib.use("Agg")


try:
    if not os.path.exists("./tests/test_results"):
        os.makedirs("./tests/test_results")
except:
    pass


@pytest.fixture
def files():
    pytest.fs1_1d = "tests/example_data/two_epoch_syn.fs"
    pytest.fs2_1d = "tests/example_data/two_epoch_non.fs"
    pytest.fs1d_demo_popt = (
        "tests/example_data/example.two_epoch.demo.params.InferDM.bestfits"
    )
    pytest.fs1d_cache1d = "tests/example_data/cache_two_epoch_1d.bpkl"
    pytest.fs_syn_2d = "tests/example_data/split_mig_syn.fs"
    pytest.fs1_2d = "tests/example_data/split_mig_non_1d.fs"
    pytest.fs2_2d = "tests/example_data/split_mig_non_2d.fs"
    pytest.fs_mixture = "tests/example_data/split_mig_non_mix.fs"
    pytest.fs2d_demo_popt = (
        "tests/example_data/example.split_mig.demo.params.InferDM.bestfits"
    )
    pytest.fs2d_dfe_popt = "tests/example_data/example.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits"
    pytest.fs2d_cache1d = "tests/example_data/cache_split_mig_1d.bpkl"
    pytest.fs2d_cache2d = "tests/example_data/cache_split_mig_2d.bpkl"


def test_plot_single_sfs(files):
    plot_single_sfs(
        fs=pytest.fs1_1d,
        projections=[8],
        output="tests/test_results/plot_single_sfs_1d_w_proj.png",
        vmin=0,
    )
    plot_single_sfs(
        fs=pytest.fs1_1d,
        projections=None,
        output="tests/test_results/plot_single_sfs_1d_no_proj.png",
        vmin=0,
    )
    plot_single_sfs(
        fs=pytest.fs1_2d,
        projections=[8, 8],
        output="tests/test_results/plot_single_sfs_2d_w_proj.png",
        vmin=1e-3,
    )
    plot_single_sfs(
        fs=pytest.fs1_2d,
        projections=None,
        output="tests/test_results/plot_single_sfs_2d_no_proj.png",
        vmin=1e-3,
    )


def test_plot_comparison(files):
    plot_comparison(
        fs=pytest.fs1_1d,
        fs2=pytest.fs2_1d,
        projections=[8],
        output="tests/test_results/plot_comparison_1d_w_proj.png",
        vmin=0,
        resid_range=3,
    )
    plot_comparison(
        fs=pytest.fs1_1d,
        fs2=pytest.fs2_1d,
        projections=None,
        output="tests/test_results/plot_comparison_1d_no_proj.png",
        vmin=0,
        resid_range=3,
    )
    plot_comparison(
        fs=pytest.fs1_2d,
        fs2=pytest.fs2_2d,
        projections=[8, 8],
        output="tests/test_results/plot_comparison_2d_w_proj.png",
        vmin=1e-3,
        resid_range=3,
    )
    plot_comparison(
        fs=pytest.fs1_2d,
        fs2=pytest.fs2_2d,
        projections=None,
        output="tests/test_results/plot_comparison_2d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
    )


def test_plot_fitted_demography(files):
    plot_fitted_demography(
        fs=pytest.fs1_1d,
        model="two_epoch",
        popt=pytest.fs1d_demo_popt,
        projections=[8],
        nomisid=True,
        output="tests/test_results/plot_plot_fitted_demography_1d_w_proj.png",
        vmin=0,
        resid_range=3,
    )
    plot_fitted_demography(
        fs=pytest.fs_syn_2d,
        model="split_mig",
        popt=pytest.fs2d_demo_popt,
        projections=[8, 8],
        nomisid=True,
        output="tests/test_results/plot_plot_fitted_demography_2d_w_proj.png",
        vmin=1e-3,
        resid_range=3,
    )
    plot_fitted_demography(
        fs=pytest.fs1_1d,
        model="two_epoch",
        popt=pytest.fs1d_demo_popt,
        projections=None,
        nomisid=True,
        output="tests/test_results/plot_plot_fitted_demography_1d_no_proj.png",
        vmin=0,
        resid_range=3,
    )
    plot_fitted_demography(
        fs=pytest.fs_syn_2d,
        model="split_mig",
        popt=pytest.fs2d_demo_popt,
        projections=None,
        nomisid=True,
        output="tests/test_results/plot_plot_fitted_demography_2d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
    )


def test_plot_fitted_dfe(files):
    # plot_fitted_dfe(fs, cache1d=pytest.fs1d_cache1d, cache2d=None, demo_popt=pytest.fs1d_demo_popt, sele_popt, projections, pdf, pdf2, nomisid, output, vmin, resid_range)
    plot_fitted_dfe(
        fs=pytest.fs_mixture,
        cache1d=pytest.fs2d_cache1d,
        cache2d=pytest.fs2d_cache2d,
        demo_popt=pytest.fs2d_demo_popt,
        sele_popt=pytest.fs2d_dfe_popt,
        projections=[8, 8],
        pdf="lognormal",
        pdf2="biv_lognormal",
        nomisid=True,
        output="tests/test_results/plot_fitted_dfe_mixture_w_proj.png",
        vmin=1e-3,
        resid_range=3,
    )


def test_plot_mut_prop(files):
    plot_mut_prop(
        dfe_popt=pytest.fs2d_dfe_popt,
        nomisid=True,
        mut_rate=1.8e-8,
        seq_len=38157840,
        ratio=2.31,
        output="tests/test_results/plot_mut_prop.png",
    )
