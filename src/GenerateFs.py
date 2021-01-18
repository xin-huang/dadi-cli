import dadi

def generate_fs(vcf, output, pop_ids, pop_info, projections, polarized, bootstrap, chunk_size):
   
    dd = dadi.Misc.make_data_dict_vcf(vcf_filename=vcf, popinfo_filename=pop_info)
    if bootstrap == None: 
        fs = dadi.Spectrum.from_data_dict(dd, pop_ids=pop_ids, projections=projections, polarized=polarized)
        fs.to_file(output)
    else:
        for b in range(bootstrap):
            fs = generate_bootstrap_fs(dd, chunk_size, pop_ids, projections, polarized)
            fs.to_file(output + '.bootstrapping.' + str(b) + '.fs')

def generate_bootstrap_fs(dd, chunk_size, pop_ids, projections, polarized):
    import random
    # split the dictionary by chromosome name
    ndd = {}
    for k in dd.keys():
        chrname, pos = k.split("_")
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
