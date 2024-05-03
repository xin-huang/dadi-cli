# Generating allele frequency spectra

## Input

`dadi-cli` only accepts [VCF](https://samtools.github.io/hts-specs/VCFv4.2.pdf) files to generate allele frequency spectra. For example, we provide two sample VCF files: [1KG.YRI.CEU.syn.vcf.gz](https://github.com/xin-huang/dadi-cli/blob/master/examples/data/1KG.YRI.CEU.syn.vcf.gz) containing genotype data from synonymous SNPs, and [1KG.YRI.CEU.non.vcf.gz](https://github.com/xin-huang/dadi-cli/blob/master/examples/data/1KG.YRI.CEU.non.vcf.gz) with genotype data from non-synonymous SNPs.

To generate a spectrum, users can use:

```
dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.syn.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs

dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.non.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output examples/results/fs/1KG.YRI.CEU.20.non.snps.unfolded.fs
```

Here [1KG.YRI.CEU.popfile.txt](https://github.com/xin-huang/dadi-cli/blob/master/examples/data/1KG.YRI.CEU.popfile.txt) is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

```
NA12718 CEU
NA12748 CEU
NA12775 CEU
NA19095 YRI
NA19096 YRI
NA19107 YRI
```

## Output

The format of the output file is the same as those created by [dadi](https://dadi.readthedocs.io).

An example for an unfolded allele frequency spectrum from one population is below.

```
5 unfolded "pop1"
1 2 3 4 5
1 0 0 0 1
```

The first line contains information on population and allele frequency spectrum. Here, "5" represents the number of elements in the allele frequency spectrum, which is equal to the sample size plus 1. The term "unfolded" signifies that the allele frequency spectrum presented is unfolded. "pop1" serves as the population's name.

The second line displays the allele frequency spectrum. The first element indicates the number of variants with fixed ancestral alleles. The last element signifies the number of variants with fixed derived alleles. The other elements represent the variant numbers with different quantities of derived alleles, ranging from 1 to the sample size.

The third line acts as a "mask" that determines if an element in the allele frequency spectrum will be used during inference. Here, "1" means the corresponding element will not be used, while "0" indicates the corresponding element will be utilized. Typically, fixed variants are excluded; thus, the first and last elements are masked in the allele frequency spectrum.

An example for a folded allele frequency spectrum from one population is below.

```
5 folded "pop1"
6 6 3 0 0
1 0 0 1 1
```

## Settings

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haplotypes for YRI and CEU respectively. We use a lower sample size here, because it allows us to speed up examples.

By default, `dadi-cli` generates folded spectra. To generate unfolded spectra, users should add `--polarized` and **the VCF files should have the `AA` in the `INFO` field and header to specify the ancestral allele for each SNP**.

While making the spectrum, users can also mask the singleton calls that are exclusive to the population(s) with `--mask-singleton` or mask the exclusive and shared singleton calls with `--mask-singleton-shared`.
