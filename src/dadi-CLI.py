import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='Commands', dest='subcommand')
subparsers.required = True

# subparser for generating frequency spectrum
generate_fs_parser = subparsers.add_parser('GenerateFs', help='Generate frequency spectrum from VCF files')
generate_fs_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
generate_fs_parser.add_argument('--polarized', default=False, action='store_true', help='Determine whether the resulting frequency spectrum is polarized or not; Default: False')
generate_fs_parser.add_argument('--pop-ids', type=str, nargs='+', required=True, help='The population names for the samples', dest='pop_ids')
generate_fs_parser.add_argument('--pop-info', type=str, required=True, help='The name of the file containing the population name of each sample', dest='pop_info')
generate_fs_parser.add_argument('--projections', type=int, nargs='+', required=True, help='The sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data')
generate_fs_parser.add_argument('--vcf', type=str, required=True, help='The VCF file for generating frequency spectrum')
generate_fs_parser.add_argument('--bootstrap', type=int, help='The times to perform bootstrapping')
generate_fs_parser.add_argument('--chunk-size', type=int, help='The chunk size to divide the genomes for bootstrapping', dest='chunk_size')

# subparser for generating cache
generate_cache_parser = subparsers.add_parser('GenerateCache', help='Generate selection coefficient cache for inferring DFE')
generate_cache_parser.add_argument('--additional-gammas', type=float, nargs='+', default=[], help='The additional positive population-scaled selection coefficients to cache for; Default: []', dest='additional_gammas')
generate_cache_parser.add_argument('--demo-popt', type=float, nargs='+', default=[], help='The bestfit parameters for the demographic model; Default: []', dest='demo_popt')
generate_cache_parser.add_argument('--gamma-bounds', type=float, nargs=2, default=[1e-4, 2000], help='The range of population-scaled selection coefficients to cache; Default: [1e-4, 2000]', dest='gamma_bounds')
generate_cache_parser.add_argument('--gamma-pts', type=int, default=50, help='The number of gamma grid points over which to integrate; Default: 50', dest='gamma_pts')
generate_cache_parser.add_argument('--grids', type=int, nargs=3, help='The sizes of grids; Default: None')
generate_cache_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether removing the last demographic parameter for misidentifying ancestral alleles or not; Default: False')
generate_cache_parser.add_argument('--model', type=str, required=True, help='The name of the demographic model with selection; To check available demographic models, please use `dadi-CLI Model`')
generate_cache_parser.add_argument('--mp', default=False, action='store_true', help='Determine whether generating cache with multiprocess or not; Default: False')
generate_cache_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
generate_cache_parser.add_argument('--sample-sizes', type=int, nargs='+', required=True, help='The sample sizes of populations', dest='sample_sizes')

# subparser for inferring demography
infer_demo_parser = subparsers.add_parser('InferDemography', help='Infer demographic models from frequency spectrum')
infer_demo_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
infer_demo_parser.add_argument('--constants', type=float, nargs='+', help='The fixed parameters during the inference, please use -1 to indicate a parameter is NOT fixed; Default: None')
infer_demo_parser.add_argument('--syn-fs', type=str, required=True, help='The frequency spectrum of synonymous mutations used for inference; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`', dest='syn_fs')
infer_demo_parser.add_argument('--grids', type=float, nargs=3, help='The sizes of the grids; Default: [sample_size[0]+10, sample_size[0]+20, sample_size[0]+30]')
infer_demo_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
infer_demo_parser.add_argument('--model', type=str, required=True, help='The name of the demographic model; To check available demographic models, please use `dadi-CLI Model`')
infer_demo_parser.add_argument('--p0', type=float, nargs='+', required=True, help='The initial parameters for inference')
infer_demo_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the inferred parameters, please use -1 to indicate a parameter without upper bound')
infer_demo_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
infer_demo_parser.add_argument('--jobs', default=1, type=int, help='The number of jobs to run optimization parrallelly')

# subparser for inferring DFE
infer_dfe_parser = subparsers.add_parser('InferDFE', help='Infer distribution of fitness effects from frequency spectrum')
infer_dfe_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
infer_dfe_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
infer_dfe_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
infer_dfe_parser.add_argument('--constants', type=float, nargs='+', help='The fixed parameters during the inference, please use -1 to indicate a parameter is NOT fixed; Default: None')
infer_dfe_parser.add_argument('--demo-popt', type=str, help='The bestfit parameters for the demographic model', dest='demo_popt')
infer_dfe_parser.add_argument('--syn-fs', type=str, help='The frequency spectrum of the synonymous mutations; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`', dest='syn_fs')
infer_dfe_parser.add_argument('--non-fs', type=str, required=True, help='The frequency spectrum of the non-synonymous mutations; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`', dest='non_fs')
infer_dfe_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
infer_dfe_parser.add_argument('--nuisance', default=False, action='store_true', help='Determine whether inferring DFE with nuisance parameters or not; Default: False')
infer_dfe_parser.add_argument('--nlopt', default=False, action='store_true', help='Determine whether using nlopt or not; Default: False')
infer_dfe_parser.add_argument('--p0', type=float, nargs='+', required=True, help='The initial parameters for inference')
infer_dfe_parser.add_argument('--pdf1d', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
infer_dfe_parser.add_argument('--pdf2d', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
infer_dfe_parser.add_argument('--ratio', type=float, help='The ratio for the nonsynonymous mutations vs. the synonymous mutations')
infer_dfe_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the inferred parameters, please use -1 to indicate a parameter with no upper bound, please use -1 to indicate a parameter without upper bound')
infer_dfe_parser.add_argument('--output', type=str, help='The name of the output file')
infer_dfe_parser.add_argument('--jobs', default=1, type=int, help='The number of jobs to run optimization parrallelly')

# subparser for plotting
plot_parser = subparsers.add_parser('Plot', help='Plot 1D/2D frequency spectrum')
plot_parser.add_argument('--demo-popt', type=str, help='The file containing the bestfit parameters for the demographic model, generated by `dadi-CLI Bestfit`', dest='demo_popt')
plot_parser.add_argument('--sel-popt', type=str, help='The file containing the bestfit parameters for the distribution of fitness effects, generated by `dadi-CLI Bestfit`', dest='sel_popt')
plot_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
plot_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
plot_parser.add_argument('--fs', type=str, required=True, help='The name of the frequency spectrum; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`')
plot_parser.add_argument('--fs2', type=str, help='The name of the second frequency spectrum for comparison; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`')
plot_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
plot_parser.add_argument('--model', type=str, help='The name of the demographic model; To check available demographic models, please use `dadi-CLI Model`')
plot_parser.add_argument('--ratio', type=float, help='The ratio for nonsynonymous to synonymous mutations')
plot_parser.add_argument('--output', type=str, help='The name of the output file')
plot_parser.add_argument('--projections', type=int, nargs='+', help='The sample sizes after projection')
plot_parser.add_argument('--resid-range', type=float, help='The ranges of the residual plots', dest='resid_range')
plot_parser.add_argument('--pdf', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
plot_parser.add_argument('--pdf2', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-CLI Distrib')
plot_parser.add_argument('--vmin', type=float, default=0.1, help='The minimum value to be plotted in the frequency spectrum; Default: 0.1')

# subparser for statistics and uncertainty analysis
stat_parser = subparsers.add_parser('Stat', help='Perform statistical tests using Godambe Information Matrix')
stat_parser.add_argument('--fs', type=str, required=True, help='The name of the frequency spectrum; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`')
stat_parser.add_argument('--model', type=str, help='The name of the demographic model; To check available demographic models, please use `dadi-CLI Model`')
stat_parser.add_argument('--misid',  default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
stat_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
stat_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
stat_parser.add_argument('--bootstrap-dir', type=str, required=True, help='The Directory containing boostrapping spectra', dest='bootstrap_dir')
stat_parser.add_argument('--pdf', type=str, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
stat_parser.add_argument('--pdf2', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-CLI Distrib')
stat_parser.add_argument('--pi', type=int, help='The index of the nested parameter in the complex model')
stat_parser.add_argument('--demo-popt', type=str, help='The file containing the bestfit parameters for the demographic model, generated by `dadi-CLI Bestfit`', dest='demo_popt')
stat_parser.add_argument('--popt-complex', type=str, required=True, help='The file containing the bestfit parameters for the complex model, generated by `dadi-CLI Bestfit`', dest='popt_complex')
stat_parser.add_argument('--popt-simple', type=str, help='The file containing the bestfit parameters for the simple model, generated by `dadi-CLI Bestfit`', dest='popt_simple')
stat_parser.add_argument('--ratio', type=float, help='The ratio for nonsynonymous to synonymous mutations')
stat_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
stat_parser.add_argument('--logscale', default=False, action='store_true', help='Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False')
stat_parser.add_argument('--lrt', default=False, action='store_true', help='Determine whether perform likelihood ratio test; Default: False')
stat_parser.add_argument('--eps', type=float, help='Fractional stepsize to use when taking finite-difference derivatives in likelihood ratio test')

bestfit_parser = subparsers.add_parser('BestFit', help='Obtain the best fit parameters')
bestfit_parser.add_argument('--dir', type=str, required=True, help='The directory containing the inferred demographic/dfe parameters')
bestfit_parser.add_argument('--output', type=str, required=True, help='The name of the ouput file')
bestfit_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the optimized parameters, please use -1 to indicate a parameter without lower bound')
bestfit_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the optimized parameters, please use -1 to indicate a parameter without upper bound')

model_parser = subparsers.add_parser('Model', help='Display available demographic models')
model_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='Show the details of a given model')
dist_parser = subparsers.add_parser('Pdf', help='Display available probability density functions for distribution of fitness effects')
dist_parser.add_argument('--names', type=str, nargs='?', default=None, required=True, help='Show the details of a given probability density distribution')

args = parser.parse_args()

def check_params(params):
    new_params = []
    for p in params:
        if p == -1.0: new_params.append(None)
        else: new_params.append(p)
    return new_params

if args.subcommand == 'GenerateFs':

    from GenerateFs import generate_fs
    generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size,
                pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

elif args.subcommand == 'GenerateCache':

    if len(args.sample_sizes) > 2: raise Exception('Cannot generate cache with more than two populations')

    from GenerateCache import generate_cache
    generate_cache(model=args.model, grids=args.grids, popt=args.demo_popt,
                   gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                   output=args.output, sample_sizes=args.sample_sizes, misid=args.misid, mp=args.mp)

elif args.subcommand == 'InferDemography':

    if args.constants != None: args.constants = check_params(args.constants)
    if args.lbounds != None: args.lbounds = check_params(args.lbounds)
    if args.ubounds != None: args.ubounds = check_params(args.ubounds)
   
    from multiprocessing import Manager, Process 
    from InferDemography import infer_demography
    #infer_demography(fs=args.syn_fs, model=args.model, grids=args.grids, 
    #                 output=args.output, p0=args.p0, upper_bounds=args.ubounds,
    #                 lower_bounds=args.lbounds, fixed_params=args.constants, misid=args.misid, cuda=args.cuda)
    with Manager() as manager:
        results = manager.list()

        pool = []
        for i in range(args.jobs):
            p = Process(target=infer_demography, 
                        args=(results, args.syn_fs, args.model, args.grids, args.p0, 
                              args.ubounds, args.lbounds, args.constants, args.misid, args.cuda))
            p.start()
            pool.append(p)
        
        for p in pool:
            p.join()

        with open(args.output, 'w') as f:
            for r in results:
                f.write(r + "\n")

elif args.subcommand == 'InferDFE':
   
    if args.constants != None: args.constants = check_params(args.constants)
    if args.lbounds != None: args.lbounds = check_params(args.lbounds)
    if args.ubounds != None: args.ubounds = check_params(args.ubounds)

    from InferDFE import infer_dfe, infer_dfe_nuisance_1d
    if args.nuisance:
        infer_dfe_nuisance_1d(syn_fs=args.syn_fs, non_fs=args.non_fs, pdf1d=args.pdf1d, cache1d=args.cache1d, 
                              misid=args.misid, is_nlopt=args.nlopt, fixed_params=args.constants, 
                              p0=args.p0, ubounds=args.ubounds, lbounds=args.lbounds, output=args.output)
    else:
        infer_dfe(fs=args.non_fs, cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf1d, sele_dist2=args.pdf2d,
                  output=args.output, p0=args.p0, upper_bounds=args.ubounds, popt=args.demo_popt, ns_s=args.ratio,
                  lower_bounds=args.lbounds, fixed_params=args.constants, misid=args.misid, cuda=args.cuda)

elif args.subcommand == 'Plot':

    from Plot import plot_comparison, plot_fitted_demography, plot_fitted_dfe, plot_single_sfs
    
    if args.sel_popt != None:
        plot_fitted_dfe(fs=args.fs, cache1d=args.cache1d, cache2d=args.cache2d, pdf=args.pdf, pdf2=args.pdf2, misid=args.misid,
                        demo_popt=args.demo_popt, sele_popt=args.sel_popt, vmin=args.vmin, resid_range=args.resid_range,
                        ns_s=args.ratio, projections=args.projections, output=args.output)
    elif args.demo_popt != None:
        plot_fitted_demography(fs=args.fs, model=args.model, popt=args.demo_popt, vmin=args.vmin,
                               projections=args.projections, misid=args.misid, resid_range=args.resid_range, output=args.output)
    elif args.fs2 == None:
        plot_single_sfs(fs=args.fs, projections=args.projections, output=args.output, vmin=args.vmin)
    else:
        plot_comparison(fs=args.fs, fs2=args.fs2, projections=args.projections, output=args.output, vmin=args.vmin, resid_range=args.resid_range)

elif args.subcommand == 'Stat':

    from Stat import godambe_stat
    godambe_stat(fs=args.fs, model=args.model, bootstrap_dir=args.bootstrap_dir, 
                 cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf, ns_s=args.ratio, eps=args.eps,
                 sele_dist2=args.pdf2, popt=args.popt_complex, misid=args.misid, pi=args.pi, demo_popt=args.demo_popt,
                 popt_simple=args.popt_simple, lrt=args.lrt, logscale=args.logscale, output=args.output)

elif args.subcommand == 'BestFit':

    args.lbounds = check_params(args.lbounds)
    args.ubounds = check_params(args.ubounds)

    from BestFit import get_bestfit_params
    get_bestfit_params(path=args.dir, lbounds=args.lbounds, ubounds=args.ubounds, output=args.output)

elif args.subcommand == 'Model':
    
    from Models import print_available_models, print_model_details
    if args.names == None:
        print_available_models()
    else:
        print_model_details(args.names)

elif args.subcommand == 'Pdf':

    from Pdfs import print_available_pdfs, print_pdf_details
    if args.names == None:
        print_available_pdfs()
    else:
        print_pdf_details(args.names)
