import dadi
import subprocess
import pytest
import numpy as np
import os
import pickle
import glob

try:
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
except:
    pass

def test_GenerateFs(capsys):
    subprocess.run(["dadi-cli", "GenerateFs", 
        "--vcf", "./tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf", 
        "--pop-info", "./examples/data/1KG.YRI.CEU.popfile.txt", 
        "--pop-ids", "YRI","CEU", "--projections", "216","198", "--polarized", 
        "--output", "./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs"
    ])
    dadi.cli_fs = dadi.Spectrum.from_file('./tests/test_results/1KG.YRI.CEU.synonymous.snps.unfold.short.fs')

    datafile = './tests/example_data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.short.vcf'
    popfile = './examples/data/1KG.YRI.CEU.popfile.txt'
    dd = dadi.Misc.make_data_dict_vcf(datafile, popfile)
    pop_ids, ns = ['YRI','CEU'], [216,198]
    dadi_fs = dadi.Spectrum.from_data_dict(dd, pop_ids, ns)

    assert np.allclose(dadi.cli_fs, dadi_fs)

def test_InferDM(capsys):
    threads = 3
    subprocess.run(
        "dadi-cli InferDM " + 
        "--fs ./tests/example_data/two_epoch_syn.fs --model two_epoch_1d " +
        "--grids 120 140 160 --p0 1 .5 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.demo.params --thread " + str(threads), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.InferDM.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits

def test_BestFit_DM(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./tests/test_results/simulation.two_epoch.demo.params.InferDM " +
        "--model two_epoch_1d --lbounds 10e-3 10e-3 --ubounds 10 10", shell=True
    )
    assert os.path.exists("./tests/test_results/simulation.two_epoch.demo.params.InferDM.bestfits")

def test_GenerateCache(capsys):
    min_gamma_bound = 2000
    gamma_pts = 50
    subprocess.run(
        "dadi-cli GenerateCache --demo-popt ./tests/test_results/simulation.two_epoch.demo.params.InferDM.bestfits " +
        "--gamma-bounds 1e-4 " + str(min_gamma_bound) + " --gamma-pts " + str(gamma_pts) + 
        " --grids 120 140 160 --model two_epoch " + 
        "--output ./tests/test_results/cache_large_two_epoch.bpkl --sample-sizes 20", shell=True
    )
    assert os.path.exists("./tests/test_results/cache_large_two_epoch.bpkl")
    s = pickle.load(open('./tests/test_results/cache_large_two_epoch.bpkl','rb'))
    assert int(np.min(s.gammas)) == -1*min_gamma_bound
    assert len(s.gammas) == gamma_pts

def test_InferDFE(capsys):
    threads = 3
    fits_fid = glob.glob("./tests/test_results/simulation.two_epoch.demo.params.InferDM.bestfits")[0]
    subprocess.run(
        "dadi-cli InferDFE " + 
        "--fs ./tests/example_data/two_epoch_non.fs --cache1d ./tests/example_data/cache_two_epoch_1d.bpkl " +
        "--demo-popt " + fits_fid + " --pdf1d lognormal --ratio 2.31 " +
        "--p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 " + 
        "--output-prefix ./tests/test_results/simulation.two_epoch.dfe.params --thread " + str(threads), shell=True
    )
    fits = glob.glob("./tests/test_results/simulation.two_epoch.dfe.params.InferDFE.opts.*")
    number_of_fits = sum([ele.startswith('#') != True for ele in open(fits[-1]).readlines()])
    assert threads == number_of_fits

def test_BestFit_DFE(capsys):
    subprocess.run(
        "dadi-cli BestFit --input-prefix ./tests/test_results/simulation.two_epoch.dfe.params.InferDFE " +
        "--pdf lognormal --lbounds 10e-3 10e-3 --ubounds 10 10", shell=True
    )
    assert os.path.exists("./tests/test_results/simulation.two_epoch.dfe.params.InferDFE.bestfits")











