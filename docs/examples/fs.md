# Generating allele frequency spectra

`dadi-cli` only accepts VCF files to generate allele frequency spectra. To generate a spectrum, users can use

```
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs

dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs
```

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

```
NA12718 CEU
NA12748 CEU
NA12775 CEU
NA19095 YRI
NA19096 YRI
NA19107 YRI
```

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haplotypes for YRI and CEU respectively. We use a lower sample size here, because it allows us to speed up examples.

By default, `dadi-cli` generates folded spectra. To generate unfolded spectra, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

While making the spectrum, users can also mask the singleton calls that are exclusive to the population(s) with `--mask-singleton` or mask the exclusive and shared singleton calls with `--mask-singleton-shared`.
