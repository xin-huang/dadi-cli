import dadi
import random


def generate_fs(
    vcf,
    output,
    pop_ids,
    pop_info,
    projections,
    subsample,
    polarized,
    marginalize_pops,
    bootstrap,
    chunk_size,
    masking,
    seed,
):
    """
    Description:
        Generates a frequency spectrum from a VCF file.

    Arguments:
        vcf str: Name of the VCF file containing genotype data.
        output str: Name of the output file containing frequency spectra.
        pop_ids list: List of population ids.
        pop_info str: Name of the file containing population information.
        projections list: List of sample sizes after projection.
        subsample bool: If True, spectrum is generated with sub-samples;
                        Otherwise, spectrum is generated with all the samples.
        polarized bool: If True, unfolded spectrum is generated;
                        Otherwise, folded spectrum is generated.
        margnialize_pops list: List of population ids to remove from the frequency spectrum.
        bootstrap int: Times to perform bootstrapping.
        chunk_size int: Chunk size to divide the genomes for bootstrapping.
        masking str: If masking == 'singleton', singletons in each population are masked;
                     If masking == 'shared', singletons in each population and shared across populations are masked;
                     Otherwise, singletons are not masked.
        seed int: Seed for generating random numbers.
    """
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
        if marginalize_pops != None:
            fs = _marginalized_fs(fs, marginalize_pops, pop_ids)
        if masking != "":
            _mask_entries(fs, masking)
        fs.to_file(output)
    else:
        if seed != None:
            random.seed(seed)
        fragments = dadi.Misc.fragment_data_dict(dd, chunk_size)
        bootstrap_list = dadi.Misc.bootstraps_from_dd_chunks(
            fragments, bootstrap, pop_ids, projections, polarized
        )
        for fs, b in zip(bootstrap_list, range(len(bootstrap_list))):
            if marginalize_pops != None:
                fs = _marginalized_fs(fs, marginalize_pops, pop_ids)
            if masking != "":
                _mask_entries(fs, masking)
            fs.to_file(output + ".bootstrapping." + str(b) + ".fs")

def _mask_entries(fs, masking):
    """
    Description:
        Helper function for masking singletons in a frequency spectrum.

    Arguments:
        fs dadi.Spectrum: Frequency spectrum.
        masking str: Masking shared singletons if masking == 'shared'.
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


def _marginalized_fs(fs, marginalize_pops, pop_ids):
    """
    Description:
        Helper function for generating a marginalized frequency spectrum.

    Arguments:
        fs dadi.Spectrum: Frequency spectrum for marginalization.
        marginalize_pops list: List of population ids to remove from the frequency spectrum.
        pop_ids list: List of all the population ids in the frequency spectrum.

    Returns:
        mfs dadi.Spectrum: Marginalized frequency spectrum.
    """
    marginalize_list = [pop_ids.index(pop) for pop in marginalize_pops]
    mfs = fs.marginalize(marginalize_list)
    return mfs
