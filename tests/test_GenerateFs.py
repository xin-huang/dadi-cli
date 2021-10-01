import dadi
import subprocess
import pytest
import numpy as np

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
