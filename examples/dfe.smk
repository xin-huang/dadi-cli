"""
Snakefile for running dadi-cli DFE inference pipeline.
"""


rule all:
    input:
        "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci",
        "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci",
        "results/plots/1KG.YRI.CEU.20.syn.pdf",
        "results/plots/1KG.YRI.CEU.20.syn.split_mig.pdf",
        "results/plots/1KG.YRI.CEU.20.non.1D_lognormal.pdf",


rule generate_dadi_fs:
    input:
        syn_vcf = "data/1KG.YRI.CEU.syn.vcf.gz",
        non_vcf = "data/1KG.YRI.CEU.non.vcf.gz",
        popinfo = "data/1KG.YRI.CEU.popfile.txt",
    output:
        syn_fs = "results/fs/1KG.YRI.CEU.20.syn.fs",
        non_fs = "results/fs/1KG.YRI.CEU.20.non.fs",
    shell:
        """
        dadi-cli GenerateFs --vcf {input.syn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --output {output.syn_fs}
        dadi-cli GenerateFs --vcf {input.non_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --output {output.non_fs}
        """


rule dadi_infer_dm:
    input:
        fs = rules.generate_dadi_fs.output.syn_fs,
    output:
        bestfit = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits",
    params:
        output_prefix = "results/demog/1KG.YRI.CEU.20.split_mig.demog.params",
    resources:
        cpus = 8,
    shell:
        """
        dadi-cli InferDM --fs {input.fs} --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5 --force-convergence 10 --cpus {resources.cpus} --output {params.output_prefix}
        """


rule dadi_generate_cache:
    input: 
        dm_bestfit= rules.dadi_infer_dm.output.bestfit,
    output:
        cache = "results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl",
    resources:
        cpus = 8,
    shell:
        """
        dadi-cli GenerateCache --model split_mig_sel_single_gamma --demo-popt {input.dm_bestfit} --sample-size 20 20 --grids 280 290 300 --cpus {resources.cpus} --output {output.cache}
        """


rule dadi_infer_dfe:
    input:
        fs = rules.generate_dadi_fs.output.non_fs,
        cache = rules.dadi_generate_cache.output.cache,
        dm_bestfit = rules.dadi_infer_dm.output.bestfit,
    output:
        bestfit = "results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits",
    params:
        output_prefix = "results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params",
    shell:
        """
        dadi-cli InferDFE --fs {input.fs} --cache1d {input.cache} --demo-popt {input.dm_bestfit} --pdf1d lognormal --lbounds -10 0.01 0 --ubounds 10 10 0.5 --ratio 2.31 --cpus 8 --force-convergence 10 --output {params.output_prefix}
        """


rule dadi_stat:
    input:
        syn_vcf = "data/1KG.YRI.CEU.syn.vcf.gz",
        non_vcf = "data/1KG.YRI.CEU.non.vcf.gz",
        popinfo = "data/1KG.YRI.CEU.popfile.txt",
        syn_fs = rules.generate_dadi_fs.output.syn_fs,
        non_fs = rules.generate_dadi_fs.output.non_fs,
        cache = rules.dadi_generate_cache.output.cache,
        dm_bestfit = rules.dadi_infer_dm.output.bestfit,
        dfe_bestfit = rules.dadi_infer_dfe.output.bestfit,
    output:
        dm_godambe_ci = "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci",
        dfe_godambe_ci = "results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci",
    params:
        syn_dir = "results/fs/bootstrapping_syn",
        non_dir = "results/fs/bootstrapping_non",
        syn_prefix = "results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold",
        non_prefix = "results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold",
    shell:
        """
        mkdir {params.syn_dir}
        mkdir {params.non_dir}
        dadi-cli GenerateFs --vcf {input.syn_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 100 --chunk-size 1000000 --seed 42 --output {params.syn_prefix}
        dadi-cli GenerateFs --vcf {input.non_vcf} --pop-info {input.popinfo} --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 100 --chunk-size 1000000 --seed 42 --output {params.non_prefix}
        dadi-cli StatDM --fs {input.syn_fs} --model split_mig --demo-popt {input.dm_bestfit} --grids 60 80 100 --bootstrapping-dir {params.syn_dir} --output {output.dm_godambe_ci}
        dadi-cli StatDFE --fs {input.non_fs} --dfe-popt {input.dfe_bestfit} --cache1d {input.cache} --pdf1d lognormal --bootstrapping-nonsynonymous-dir {params.non_dir} --bootstrapping-synonymous-dir {params.syn_dir} --output {output.dfe_godambe_ci}
        """


rule dadi_plot:
    input:
        syn_fs = rules.generate_dadi_fs.output.syn_fs,
        non_fs = rules.generate_dadi_fs.output.non_fs,
        dm_bestfit = rules.dadi_infer_dm.output.bestfit,
        dfe_bestfit = rules.dadi_infer_dfe.output.bestfit,
        cache = rules.dadi_generate_cache.output.cache,
    output:
        fs = "results/plots/1KG.YRI.CEU.20.syn.pdf",
        demo = "results/plots/1KG.YRI.CEU.20.syn.split_mig.pdf",
        dfe = "results/plots/1KG.YRI.CEU.20.non.1D_lognormal.pdf",
    shell:
        """
        dadi-cli Plot --fs {input.syn_fs} --output {output.fs}
        dadi-cli Plot --fs {input.syn_fs} --model split_mig --demo-popt {input.dm_bestfit} --output {output.demo}
        dadi-cli Plot --fs {input.non_fs} --dfe-popt {input.dfe_bestfit} --cache1d {input.cache} --pdf1d lognormal --output {output.dfe}
        """
