import dadi, glob, matplotlib, os, pytest, subprocess, pickle
from dadi_cli.Plot import plot_single_sfs
from dadi_cli.Plot import plot_comparison
from dadi_cli.Plot import plot_fitted_demography
from dadi_cli.Plot import plot_fitted_dfe
from dadi_cli.Plot import plot_mut_prop
from importlib.metadata import version

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

    pytest.fs3d_model = "tests/example_data/ooa.fs"
    pytest.fs3d_sampled = "tests/example_data/ooa_10000_sampled.fs"
    pytest.fs3d_popt = "tests/example_data/example.ooa.donni.pseudofit"


@pytest.mark.skipif(version('dadi') <= '2.3.3', reason="Version of dadi doesn't support interactive plot display for single SFS")
def test_plot_single_sfs(files):
    plot_single_sfs(
        fs=pytest.fs1_1d,
        projections=[8],
        output="tests/test_results/plot_single_sfs_1d_w_proj.png",
        vmin=0,
        show=False,
    )
    plot_single_sfs(
        fs=pytest.fs1_1d,
        projections=None,
        output="tests/test_results/plot_single_sfs_1d_no_proj.png",
        vmin=0,
        show=False,
    )
    plot_single_sfs(
        fs=pytest.fs1_2d,
        projections=[8, 8],
        output="tests/test_results/plot_single_sfs_2d_w_proj.png",
        vmin=1e-3,
        show=False,
    )
    plot_single_sfs(
        fs=pytest.fs1_2d,
        projections=None,
        output="tests/test_results/plot_single_sfs_2d_no_proj.png",
        vmin=1e-3,
        show=False,
    )


def test_plot_comparison(files):
    plot_comparison(
        fs=pytest.fs1_1d,
        fs2=pytest.fs2_1d,
        projections=[8],
        output="tests/test_results/plot_comparison_1d_w_proj.png",
        vmin=0,
        resid_range=3,
        show=False,
    )
    plot_comparison(
        fs=pytest.fs1_1d,
        fs2=pytest.fs2_1d,
        projections=None,
        output="tests/test_results/plot_comparison_1d_no_proj.png",
        vmin=0,
        resid_range=3,
        show=False,
    )
    plot_comparison(
        fs=pytest.fs1_2d,
        fs2=pytest.fs2_2d,
        projections=[8, 8],
        output="tests/test_results/plot_comparison_2d_w_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    plot_comparison(
        fs=pytest.fs1_2d,
        fs2=pytest.fs2_2d,
        projections=None,
        output="tests/test_results/plot_comparison_2d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    plot_comparison(
        fs=pytest.fs3d_model,
        fs2=pytest.fs3d_sampled,
        projections=None,
        output="tests/test_results/plot_comparison_3d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )


def test_plot_fitted_demography(files):
    plot_fitted_demography(
        fs=pytest.fs1_1d,
        func=dadi.Demographics1D.two_epoch,
        popt=pytest.fs1d_demo_popt,
        projections=[8],
        nomisid=True,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_fitted_demography_1d_w_proj.png",
        vmin=0,
        resid_range=3,
        show=False,
    )
    plot_fitted_demography(
        fs=pytest.fs_syn_2d,
        func=dadi.Demographics2D.split_mig,
        popt=pytest.fs2d_demo_popt,
        projections=[8, 8],
        nomisid=True,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_fitted_demography_2d_w_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    plot_fitted_demography(
        fs=pytest.fs1_1d,
        func=dadi.Demographics1D.two_epoch,
        popt=pytest.fs1d_demo_popt,
        projections=None,
        nomisid=True,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_fitted_demography_1d_no_proj.png",
        vmin=0,
        resid_range=3,
        show=False,
    )
    plot_fitted_demography(
        fs=pytest.fs_syn_2d,
        func=dadi.Demographics2D.split_mig,
        popt=pytest.fs2d_demo_popt,
        projections=None,
        nomisid=True,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_fitted_demography_2d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    plot_fitted_demography(
        fs=pytest.fs3d_sampled,
        func=dadi.Demographics3D.out_of_africa,
        popt=pytest.fs3d_popt,
        projections=None,
        nomisid=False,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_fitted_demography_3d_no_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    # Test LowPass
    plot_fitted_demography(
        fs="tests/example_data/LowPass-files/cov.fs",
        func=dadi.Demographics2D.split_mig,
        popt=pytest.fs2d_demo_popt,
        projections=None,
        nomisid=True,
        cov_args=[pickle.load(open("./tests/example_data/LowPass-files/cov.fs.coverage.pickle", 'rb')), 20, 20],
        cov_inbreeding=[],
        output="tests/test_results/plot_plot_low-pass_demography.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )


def test_plot_fitted_dfe(files):
    # plot_fitted_dfe(fs, cache1d=pytest.fs1d_cache1d, cache2d=None, demo_popt=pytest.fs1d_demo_popt, sele_popt, projections, pdf, pdf2, nomisid, output, vmin, resid_range)
    plot_fitted_dfe(
        fs=pytest.fs_mixture,
        cache1d=pytest.fs2d_cache1d,
        cache2d=pytest.fs2d_cache2d,
        sele_popt=pytest.fs2d_dfe_popt,
        projections=[8, 8],
        pdf="lognormal",
        pdf2="biv_lognormal",
        nomisid=True,
        cov_args=[],
        cov_inbreeding=[],
        output="tests/test_results/plot_fitted_dfe_mixture_w_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )
    # Test LowPass
    plot_fitted_dfe(
        fs="tests/example_data/LowPass-files/cov.fs",
        cache1d=pytest.fs2d_cache1d,
        cache2d=pytest.fs2d_cache2d,
        sele_popt=pytest.fs2d_dfe_popt,
        projections=[8, 8],
        pdf="lognormal",
        pdf2="biv_lognormal",
        nomisid=True,
        cov_args=[pickle.load(open("./tests/example_data/LowPass-files/cov.fs.coverage.pickle", 'rb')), 20, 20],
        cov_inbreeding=[],
        output="tests/test_results/plot_fitted_dfe_mixture_w_proj.png",
        vmin=1e-3,
        resid_range=3,
        show=False,
    )

def test_plot_mut_prop(files):
    plot_mut_prop(
        pdf='lognormal',
        dfe_popt=pytest.fs2d_dfe_popt,
        output="tests/test_results/plot_mut_prop.png",
        show=False,
    )
