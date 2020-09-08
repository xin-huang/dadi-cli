import dadi

def generate_fs(vcf, fs, output, pop_ids, pop_info, projections, polarized):
    
    if vcf != None:
        dd = dadi.Misc.make_data_dict_vcf(vcf_filename=vcf, popinfo_filename=pop_info)
        fs = dadi.Spectrum.from_data_dict(dd, pop_ids=pop_ids, projections=projections, polarized=polarized)
    else:
       fs = dadi.Spectrum.from_file(fs)
       fs = fs.project(projections)
       
    fs.to_file(output)
