# Preparing Data Analysis

## Note on the human data

The human data reflacts the Snakemake workflows found here: 
https://github.com/xin-huang/dadi-cli-analysis

## Download the data

The 1000 Genomes VCFs can be downloaded from the [FTP website](https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/).

The mouse VCF (AllMouse.vcf_90_recalibrated_snps_raw_indels_reheader_PopSorted.PASS.vcf.gz) can be downloaded from https://wwwuser.gwdg.de/~evolbio/evolgen/wildmouse/vcf/.

## Processing 1000 Genomes Data

After downloading the 1000 Genomes Project data, we used [BCFtools](https://samtools.github.io/bcftools/) to extract biallelic single nucleotide polymorphisms (SNPs) and [ANNOVAR](https://annovar.openbioinformatics.org/en/latest/) to annotate these SNPs as synonymous and nonsynonymous mutations.
Then we stored the synonymous and nonsynonymous SNPs in compressed VCF files: `1KG.YRI.CEU.syn.vcf.gz` and `1KG.YRI.CEU.non.vcf.gz`, respectively.
To generate an unfolded AFS, we reintroduced what 1000 Genomes determined as the ancestral allele state (which is based on Ensembl multiple alignments using Ortheus) of each SNP to the INFO field of these input VCF files with the ID `AA`, using the `annotate` command in BCFtools.
(See an example [Snakemake file](https://github.com/xin-huang/dadi-cli-analysis/blob/main/workflows/step3_dfes.smk)). 
In addition, we created a text file containing the population information of each individual, as following:
\begin{verbatim}
NA12718 CEU
NA12748 CEU
NA12775 CEU
NA12777 CEU
NA12778 CEU
\end{verbatim}
The first column is the identifier of each individual and the second is the name of the population that the individual belongs to.
All the input files used in this manuscript can be found in the [dadi-cli GitHub repository](https://github.com/xin-huang/dadi-cli/tree/master/examples/data/).
The commands in the following sections for executing dadi-cli in a personal computer or a computing node of a high-performance computing cluster can be found [here](https://github.com/xin-huang/dadi-cli/blob/master/examples/dfe.smk).
\tjscomment{Let's add an "Example Data Generate" section to the readthedocs to have these links/details?}

## Processing Mouse Data

bla.

## References for Tools Used

Danecek P, Bonfield JK, Liddle J, Marshall J, Ohan V, Pollard MO, Whitwham A, Keane T, McCarthy SA, Davies RM,
Li H (2021) Twelve years of SAMtools and BCFtools. GigaScience 10:giab008.

Wang K, Li M, Hakonarson H (2010) ANNOVAR: functional annotation of genetic variants from high-throughput se-
quencing data. Nucleic Acids Research 38:e164.
