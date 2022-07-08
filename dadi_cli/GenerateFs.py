import dadi

def generate_fs(vcf, output, pop_ids, pop_info, projections, subsample, polarized, marginalize_pops, bootstrap, chunk_size, masking, seed):
    if subsample:
        subsample_dict = {}
        for i in range(len(pop_ids)):
            subsample_dict[pop_ids[i]] = projections[i]
        dd = dadi.Misc.make_data_dict_vcf(vcf_filename=vcf, popinfo_filename=pop_info, subsample=subsample_dict)
    else:
        dd = dadi.Misc.make_data_dict_vcf(vcf_filename=vcf, popinfo_filename=pop_info)
    if bootstrap == None: 
        fs = dadi.Spectrum.from_data_dict(dd, pop_ids=pop_ids, projections=projections, polarized=polarized)
        if masking != '':
            mask_entries(fs, masking)
        if marginalize_pops != None: fs = marginalized_fs(fs, marginalize_pops, pop_ids)
        fs.to_file(output)
    else:
        for b in range(bootstrap):
            fs = generate_bootstrap_fs(dd, chunk_size, pop_ids, projections, polarized, seed)
            if masking != '':
                mask_entries(fs, masking)
            if marginalize_pops != None: fs = marginalized_fs(fs, marginalize_pops, pop_ids)
            fs.to_file(output + '.bootstrapping.' + str(b) + '.fs')

def generate_bootstrap_fs(dd, chunk_size, pop_ids, projections, polarized, seed):
    import random
    if seed != None: random.seed(seed)
    # split the dictionary by chromosome name
    ndd = {}
    for k in dd.keys():
        chrname, pos = '_'.join(k.split("_")[:-1]), k.split("_")[-1]
        if chrname not in ndd:
            ndd[chrname] = {}
        if pos not in ndd[chrname]:
            ndd[chrname][int(pos)] = 1

    # generate chunks with given chunk size
    chunks = {}
    for chrname in ndd.keys():
        if chrname not in chunks:
            chunks[chrname] = []
        pos = sorted(ndd[chrname])
        end = chunk_size
        chunk_index = 0
        chunks[chrname].append([])
        for p in pos:
            if p <= end: chunks[chrname][chunk_index].append(p)
            else:
                end += chunk_size
                chunk_index += 1
                chunks[chrname].append([])
                chunks[chrname][chunk_index].append(p)

    # sample the dictionary with replacement
    bdd = {}
    index = 0
    for chrname in chunks.keys():
        random_chunks = random.choices(range(len(chunks[chrname])), k=len(chunks[chrname]))
        for chunk in random_chunks:
            for pos in chunks[chrname][chunk]:
                bdd.update({index: dd[chrname + "_" + str(pos)]})
                index += 1
    fs = dadi.Spectrum.from_data_dict(bdd, pop_ids=pop_ids, projections=projections, polarized=polarized)
    return fs

def mask_entries(fs, masking):
    if len(fs.sample_sizes) == 1:
        fs.mask[1] = True
        fs.mask[-2] = True
    elif len(fs.sample_sizes) == 2:
        fs.mask[1,0] = True
        fs.mask[-2,-1] = True
        fs.mask[0,1] = True
        fs.mask[-1,-2] = True
        if masking=='shared':
            fs.mask[1,1] = True
            fs.mask[-2,-2] = True
    elif len(fs.sample_sizes) == 3:
        fs.mask[1,0,0] = True
        fs.mask[-2,-1,-1] = True
        fs.mask[0,1,0] = True
        fs.mask[-1,-2,-1] = True
        fs.mask[0,0,1] = True
        fs.mask[-1,-1,-2] = True
        if masking=='shared':
            fs.mask[1,1,0] = True
            fs.mask[1,0,1] = True
            fs.mask[1,1,1] = True
            fs.mask[-2,-2,-1] = True
            fs.mask[-2,-1,-2] = True
            fs.mask[-2,-2,-2] = True

def marginalized_fs(fs, marginalize_pops, pop_ids):
    marginalize_list = [pop_ids.index(pop) for pop in marginalize_pops]
    return(fs.marginalize(marginalize_list))






