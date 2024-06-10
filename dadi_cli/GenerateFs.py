import dadi, random


def generate_fs(
    vcf: str,
    output: str,
    pop_ids: list[str],
    pop_info: str,
    projections: list[int],
    subsample: bool,
    polarized: bool,
    marginalize_pops: list[str],
    bootstrap: int,
    chunk_size: int,
    masking: str,
    seed: int,
) -> None:
    """
    Generates a frequency spectrum from a VCF file using various settings for data manipulation and analysis.

    Parameters
    ----------
    vcf : str
        Name of the VCF file containing genotype data.
    output : str
        Name of the output file containing frequency spectra.
    pop_ids : list[str]
        List of population ids.
    pop_info : str
        Name of the file containing population information.
    projections : list[int]
        List of sample sizes after projection.
    subsample : bool
        If True, spectrum is generated with sub-samples; otherwise, spectrum is generated with all samples.
    polarized : bool
        If True, unfolded spectrum is generated; otherwise, folded spectrum is generated.
    marginalize_pops : list[str]
        List of population ids to remove from the frequency spectrum. If None, no populations are marginalized.
    bootstrap : int
        Number of times to perform bootstrapping. If None, bootstrapping is not performed.
    chunk_size : int
        Chunk size to divide the genomes for bootstrapping.
    masking : str
        Determines the masking method for singletons:
        'singleton' - Masks singletons in each population,
        'shared' - Masks singletons in each population and those shared across populations,
        '' - No masking is applied.
    seed : int
        Seed for generating random numbers. If None, a random seed is used.

    Raises
    ------
    ValueError
        If the lengths of `pop_ids` and `projections` do not match.
        If the VCF file does not contain the AA INFO field and `polarized` is True.

    """
    if len(pop_ids) != len(projections):
        raise ValueError("The lengths of `pop_ids` and `projections` must match.")

    if polarized:
        try:
            from cyvcf2 import VCF
            if not VCF(vcf).contains('AA'):
                raise ValueError(
                    f'The AA (Ancestral allele) INFO field cannot be found in the header of {vcf}, ' +
                    'but an unfolded frequency spectrum is requested.'
                )
        except ModuleNotFoundError:
            print("Unable to load cyvcf2 and check if ancestral alleles are in provided VCF.\n"+
                  "Generated FS may be empty if ancestral allele not found.")
        except ImportError:
            print("Error importing cyvcf2")

    if subsample:
        subsample_dict = {}
        for i in range(len(pop_ids)):
            subsample_dict[pop_ids[i]] = projections[i]
        dd = dadi.Misc.make_data_dict_vcf(
            vcf_filename=vcf, popinfo_filename=pop_info, subsample=subsample_dict
        )
    else:
        dd = dadi.Misc.make_data_dict_vcf(vcf_filename=vcf, popinfo_filename=pop_info)

    if bootstrap is None:
        fs = dadi.Spectrum.from_data_dict(
            dd, pop_ids=pop_ids, projections=projections, polarized=polarized
        )
        if marginalize_pops is not None:
            fs = _marginalized_fs(fs, marginalize_pops, pop_ids)
        if masking != "":
            _mask_entries(fs, masking)
        fs.to_file(output)
    else:
        if seed is not None:
            random.seed(seed)
        fragments = dadi.Misc.fragment_data_dict(dd, chunk_size)
        bootstrap_list = dadi.Misc.bootstraps_from_dd_chunks(
            fragments, bootstrap, pop_ids, projections, polarized
        )
        for fs, b in zip(bootstrap_list, range(len(bootstrap_list))):
            if marginalize_pops is not None:
                fs = _marginalized_fs(fs, marginalize_pops, pop_ids)
            if masking != "":
                _mask_entries(fs, masking)
            fs.to_file(output + ".bootstrapping." + str(b) + ".fs")


def _mask_entries(fs: dadi.Spectrum, masking: str) -> None:
    """
    Masks entries in the frequency spectrum based on the number of populations and the specified masking strategy.

    Parameters
    ----------
    fs : dadi.Spectrum
        The frequency spectrum object, which contains genotype frequency data across populations.
    masking : str
        Masking shared singletons if masking == 'shared'.

    Raises
    ------
    ValueError
        If the frequency spectrum contains more than 3 populations, as the current implementation does not support more.

    """
    if len(fs.sample_sizes) == 1:
        fs.mask[1] = True
        fs.mask[-2] = True
    elif len(fs.sample_sizes) == 2:
        fs.mask[1, 0] = True
        fs.mask[-2, -1] = True
        fs.mask[0, 1] = True
        fs.mask[-1, -2] = True
        if masking == "shared":
            fs.mask[1, 1] = True
            fs.mask[-2, -2] = True
    elif len(fs.sample_sizes) == 3:
        fs.mask[1, 0, 0] = True
        fs.mask[-2, -1, -1] = True
        fs.mask[0, 1, 0] = True
        fs.mask[-1, -2, -1] = True
        fs.mask[0, 0, 1] = True
        fs.mask[-1, -1, -2] = True
        if masking == "shared":
            fs.mask[1, 1, 0] = True
            fs.mask[1, 0, 1] = True
            fs.mask[1, 1, 1] = True
            fs.mask[-2, -2, -1] = True
            fs.mask[-2, -1, -2] = True
            fs.mask[-2, -2, -2] = True
    else:
        raise ValueError(
            "Masking singletons is only supported for a frequency spectrum with no more than 3 populations."
        )


def _marginalized_fs(fs: dadi.Spectrum, marginalize_pops: list[str], 
                     pop_ids: list[str]) -> dadi.Spectrum:
    """
    Generates a marginalized frequency spectrum by removing specified populations.

    Parameters
    ----------
    fs : dadi.Spectrum
        Frequency spectrum for marginalization.
    marginalize_pops : list[str]
        List of population ids to remove from the frequency spectrum.
    pop_ids : list[str]
        List of all the population ids in the frequency spectrum.

    Returns
    -------
    dadi.Spectrum
        Marginalized frequency spectrum.

    Raises
    ------
    ValueError
        If any of the populations in marginalize_pops are not in pop_ids.

    """
    if not set(marginalize_pops).issubset(set(pop_ids)):
        raise ValueError("All populations to marginalize must be in the list of population ids.")

    marginalize_list = [pop_ids.index(pop) for pop in marginalize_pops]
    mfs = fs.marginalize(marginalize_list)
    return mfs
