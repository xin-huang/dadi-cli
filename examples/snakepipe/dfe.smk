"""
Snakefile for running dadi-cli DFE inference pipeline.
"""


rule all:
    input:
        "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci",
        "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci"


rule generate_dadi_fs:
    input:
        syn_vcf = "../data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz",
        nsyn_vcf = "../data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz",
        popinfo = "../data/1KG.YRI.CEU.popfile.txt",
    output:
        syn_fs = "results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs",
        nsyn_fs = "results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs",
    shell:
        """
        dadi-cli GenerateFs --vcf {input.syn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --output {output.syn_fs}
        dadi-cli GenerateFs --vcf {input.nsyn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --output {output.nsyn_fs}
        """


rule dadi_infer_dm:
    input:
        fs = rules.generate_dadi_fs.output.syn_fs,
    output:
        opts = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0",
    params:
        output_prefix = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params",
    resources:
        cpus = 10,
    shell:
        """
        dadi-cli InferDM --fs {input.fs} --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5  --output {params.output_prefix} --optimizations {resources.cpus}
        """


rule dadi_bestfit_dm:
    input:
        dm_opts = rules.dadi_infer_dm.output,
    output:
        bestfit = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits",
    params:
        input_prefix = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM",
    shell:
        """
        dadi-cli BestFit --input-prefix {params.input_prefix} --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
        """


rule dadi_generate_cache:
    input: 
        dm_bestfit= rules.dadi_bestfit_dm.output,
    output:
        cache = "results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl",
    resources:
        cpus = 4,
    shell:
        """
        dadi-cli GenerateCache --model split_mig_sel_single_gamma --demo-popt {input.dm_bestfit} --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output {output.cache} --cpus {resources.cpus}
        """


rule dadi_infer_dfe:
    input:
        fs = rules.generate_dadi_fs.output.nsyn_fs,
        cache = rules.dadi_generate_cache.output.cache,
        dm_bestfit = rules.dadi_bestfit_dm.output.bestfit,
    output:
        bestfit = "results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits",
    params:
        output_prefix = "results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params",
    shell:
        """
        dadi-cli InferDFE --fs {input.fs} --cache1d {input.cache} --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt {input.dm_bestfit} --ratio 2.31 --output {params.output_prefix} --optimizations 10 --maxeval 400 --check-convergence
        """


rule dadi_stat:
    input:
        syn_vcf = "../data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz",
        nsyn_vcf = "../data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz",
        popinfo = "../data/1KG.YRI.CEU.popfile.txt",
        syn_fs = "results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs",
        nsyn_fs = "results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs",
        cache = "results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl",
        dm_bestfit = rules.dadi_bestfit_dm.output.bestfit,
        dfe_bestfit = rules.dadi_infer_dfe.output.bestfit,
    output:
        dm_godambe_ci = "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci",
        dfe_godambe_ci = "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci",
    params:
        syn_dir = "results/fs/bootstrapping_syn",
        nsyn_dir = "results/fs/bootstrapping_non",
        syn_prefix = "results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold",
        nsyn_prefix = "results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold",
    shell:
        """
        mkdir {params.syn_dir}
        mkdir {params.nsyn_dir}
        dadi-cli GenerateFs --vcf {input.syn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output {params.syn_prefix}
        dadi-cli GenerateFs --vcf {input.nsyn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output {params.nsyn_prefix}
        dadi-cli StatDM --fs {input.syn_fs} --model split_mig --demo-popt {input.dm_bestfit} --grids 60 80 100 --bootstrapping-dir {params.syn_dir} --output {output.dm_godambe_ci}
        dadi-cli StatDFE --fs {input.nsyn_fs} --dfe-popt {input.dfe_bestfit} --cache1d {input.cache} --pdf1d lognormal --bootstrapping-nonsynonymous-dir {params.nsyn_dir} --bootstrapping-synonymous-dir {params.syn_dir} --output {output.dfe_godambe_ci}
        """
