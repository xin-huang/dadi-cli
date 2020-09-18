import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='Commands', dest='command')

# subparser for generating frequency spectrum
generate_fs_parser = subparsers.add_parser('GenerateFs', help='Generate frequency spectrum from VCF files')
generate_fs_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
generate_fs_parser.add_argument('--polarized', default=False, action='store_true', help='Determine whether the resulting frequency spectrum is polarized or not; Default: False')
generate_fs_parser.add_argument('--pop_ids', type=str, nargs='+', required=True, help='The population names for the samples')
generate_fs_parser.add_argument('--pop_info', type=str, required=True, help='The name of the file containing the population name of each sample')
generate_fs_parser.add_argument('--projections', type=int, nargs='+', required=True, help='The sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data')
generate_fs_parser.add_argument('--vcf', type=str, required=True, help='The VCF file for generating frequency spectrum')
generate_fs_parser.add_argument('--bootstrap', type=int, help='The times to perform bootstrapping')
generate_fs_parser.add_argument('--chunk_size', type=int, help='The chunk size to divide the genomes for bootstrapping')

# subparser for generating cache
generate_cache_parser = subparsers.add_parser('GenerateCache', help='Generate selection coefficient cache for inferring DFE')
generate_cache_parser.add_argument('--additional_gammas', type=float, nargs='+', default=[], help='The additional positive population-scaled selection coefficients to cache for; Default: []')
generate_cache_parser.add_argument('--popt', type=str, help='')
generate_cache_parser.add_argument('--gamma_bounds', type=float, nargs=2, default=[1e-4, 2000], help='The range of population-scaled selection coefficients to cache; Default: [1e-4, 2000]')
generate_cache_parser.add_argument('--gamma_pts', type=int, default=50, help='The number of gamma grid points over which to integrate; Default: 50')
generate_cache_parser.add_argument('--grids', type=int, nargs=3, help='The sizes of grids; Default: None')
generate_cache_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether removing the last demographic parameter for misidentifying ancestral alleles or not; Default: False')
generate_cache_parser.add_argument('--model', type=str, required=True, help='The name of the demographic model with selection')
generate_cache_parser.add_argument('--mp', default=False, action='store_true', help='Determine whether generating cache with multiprocess or not; Default: False')
generate_cache_parser.add_argument('--output', type=str, required=True, help='The name of the output file')
generate_cache_parser.add_argument('--sample_sizes', type=int, nargs='+', required=True, help='The sample sizes')

# subparser for inferring demography
infer_demo_parser = subparsers.add_parser('InferDemography', help='Infer demographic models from frequency spectrum')
infer_demo_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
infer_demo_parser.add_argument('--constants', type=str, nargs='+', help='The fixed parameters during the inference, please use -1 to indicate a parameter is NOT fixed; Default: None')
infer_demo_parser.add_argument('--fs', type=str, required=True, help='The frequency spectrum used for inference; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`')
infer_demo_parser.add_argument('--grids', type=float, nargs=3, help='The sizes of the grids; Default: [sample_size[0]+10, sample_size[0]+20, sample_size[0]+30]')
infer_demo_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
infer_demo_parser.add_argument('--model', type=str, required=True, help='The name of the demographic model; To check available demographic models, please use `dadi-CLI Model`')
infer_demo_parser.add_argument('--p0', type=float, nargs='+', required=True, help='The initial parameters for inference')
infer_demo_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the inferred parameters, please use -1 to indicate a parameter without upper bound')
infer_demo_parser.add_argument('--output', type=str, required=True, help='The name of the output file')

# subparser for inferring DFE
infer_dfe_parser = subparsers.add_parser('InferDFE', help='Infer distribution of fitness effects from frequency spectrum')
infer_dfe_parser.add_argument('--cache1d', type=str, help='The name of the 1D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
infer_dfe_parser.add_argument('--cache2d', type=str, help='The name of the 2D DFE cache; To generate the cache, please use `dadi-CLI GenerateCache`')
infer_dfe_parser.add_argument('--cuda', default=False, action='store_true', help='Determine whether using GPUs to accelerate inference or not; Default: False')
infer_dfe_parser.add_argument('--constants', type=float, nargs='+', help='The fixed parameters during the inference, please use -1 to indicate a parameter is NOT fixed; Default: None')
infer_dfe_parser.add_argument('--popt', type=str, help='')
infer_dfe_parser.add_argument('--fs', type=str, required=True, help='The name of the frequency spectrum; To generate the frequency spectrum, please use `dadi-CLI GenerateFs`')
infer_dfe_parser.add_argument('--lbounds', type=float, nargs='+', required=True, help='The lower bounds of the inferred parameters, please use -1 to indicate a parameter without lower bound')
infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
infer_dfe_parser.add_argument('--p0', type=float, nargs='+', required=True, help='The initial parameters for inference')
infer_dfe_parser.add_argument('--pdf', type=str, required=True, help='The 1D probability density function for the DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
infer_dfe_parser.add_argument('--pdf2', type=str, help='The 2D probability density function for the joint DFE inference; To check available probability density functions, please use `dadi-CLI Distrib`')
infer_dfe_parser.add_argument('--ns_s', type=float, required=True, help='The ratio for the nonsynonymous mutations vs. the synonymous mutations')
infer_dfe_parser.add_argument('--ubounds', type=float, nargs='+', required=True, help='The upper bounds of the inferred parameters, please use -1 to indicate a parameter with no upper bound, please use -1 to indicate a parameter without upper bound')
infer_dfe_parser.add_argument('--output', type=str, required=True, help='The name of the output file')

# subparser for plotting
plot_parser = subparsers.add_parser('Plot', help='Plot 1D/2D frequency spectrum')
plot_parser.add_argument('--demography_params', type=float, nargs='+', default=[], help='the parameters for the demographic model; default: []')
plot_parser.add_argument('--selection_params', type=float, nargs='+', default=[], help='the parameters for the distribution of fitness effects; default: []')
plot_parser.add_argument('--cache1d', type=str, help='...')
plot_parser.add_argument('--cache2d', type=str, help='...')
plot_parser.add_argument('--fs', type=str, required=True, help='...')
plot_parser.add_argument('--fs2', type=str, help='...')
plot_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
plot_parser.add_argument('--model', type=str, help='')
plot_parser.add_argument('--output', type=str, help='...')
plot_parser.add_argument('--projection', type=int, nargs='+', default=[20, 20], help='')
plot_parser.add_argument('--sele_dist', type=str, help='')
plot_parser.add_argument('--sele_dist2', type=str, help='')
plot_parser.add_argument('--theta', type=float, help='')

# subparser for statistics and uncertainty analysis
stat_parser = subparsers.add_parser('Stat', help='Perform statistical tests using Godambe Information Matrix')
stat_parser.add_argument('--fs', type=str, help='The ')
stat_parser.add_argument('--model', type=str, help='')
stat_parser.add_argument('--misid',  default=False, action='store_true', help='Determine whether adding a parameter for misidentifying ancestral alleles or not; Default: False')
stat_parser.add_argument('--cache1d', type=str)
stat_parser.add_argument('--cache2d', type=str)
stat_parser.add_argument('--bootstrap_dir', type=str, required=True, help='the directory for boostrapping spectra')
stat_parser.add_argument('--pdf', type=str)
stat_parser.add_argument('--pdf2', type=str)
stat_parser.add_argument('--pi', type=int)
stat_parser.add_argument('--popt', type=str, required=True)
stat_parser.add_argument('--popt_simple', type=str)
stat_parser.add_argument('--ns_s', type=float, required=True)
stat_parser.add_argument('--output', type=str, required=True)
stat_parser.add_argument('--logscale', default=False, action='store_true')
stat_parser.add_argument('--lrt', default=False, action='store_true')

bestfit_parser = subparsers.add_parser('Bestfit', help='Obtain the bestfit parameters')
bestfit_parser.add_argument('--dir', type=str, help='')
bestfit_parser.add_argument('--output', type=str, help='')

model_parser = subparsers.add_parser('Model', help='Display available demographic models')
dist_parser = subparsers.add_parser('Distrib', help='Display available probability density functions for distribution of fitness effects')

args = parser.parse_args()

def check_params(params):
    new_params = []
    for p in params:
        if p == -1.0: new_params.append(None)
        else: new_params.append(p)
    return new_params

if args.command == 'GenerateFs':

    from GenerateFs import generate_fs
    generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size,
                pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

elif args.command == 'GenerateCache':

    if len(args.sample_sizes) > 2: raise Exception('Cannot generate cache with more than two populations')

    from GenerateCache import generate_cache
    generate_cache(model=args.model, grids=args.grids, popt=args.popt,
                   gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                   output=args.output, sample_sizes=args.sample_sizes, misid=args.misid, mp=args.mp)

elif args.command == 'InferDemography':

    if args.constants != None: args.constants = check_params(args.constants)
    if args.lbounds != None: args.lbounds = check_params(args.lbounds)
    if args.ubounds != None: args.ubounds = check_params(args.ubounds)

    from InferDemography import infer_demography
    infer_demography(fs=args.fs, model=args.model, grids=args.grids, 
                     output=args.output, p0=args.p0, upper_bounds=args.ubounds,
                     lower_bounds=args.lbounds, fixed_params=args.constants, misid=args.misid, cuda=args.cuda)

elif args.command == 'InferDFE':
   
    if args.constants != None: args.constants = check_params(args.constants)
    if args.lbounds != None: args.lbounds = check_params(args.lbounds)
    if args.ubounds != None: args.ubounds = check_params(args.ubounds)

    from InferDFE import infer_dfe
    infer_dfe(fs=args.fs, cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf, sele_dist2=args.pdf2,
              output=args.output, p0=args.p0, upper_bounds=args.ubounds, popt=args.popt, ns_s=args.ns_s,
              lower_bounds=args.lbounds, fixed_params=args.constants, misid=args.misid, cuda=args.cuda)

elif args.command == 'Plot':

    from Plot import plot_comparison, plot_fitted_demography, plot_fitted_dfe, plot_single_sfs
    if args.fs2 == None:
        plot_single_sfs(fs=args.fs, projections=args.projections, output=args.output)
    elif len(args.demography_params) != 0:
        plot_fitted_demography(fs=args.fs, model=args.model, demography_params=args.demography_params, 
                               projections=args.projections, misid=args.misid, output=args.output)
    elif len(args.selection_params) != 0:
        plot_fitted_dfe()
    else:
        plot_comparison(fs=args.fs, fs2=args.fs2, projections=args.projections, output=args.output)

elif args.command == 'Stat':

    from Stat import godambe_stat
    godambe_stat(fs=args.fs, model=args.model, bootstrap_dir=args.bootstrap_dir, 
                 cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.pdf, ns_s=args.ns_s,
                 sele_dist2=args.pdf2, popt=args.popt, misid=args.misid, pi=args.pi,
                 popt_simple=args.popt_simple, lrt=args.lrt, logscale=args.logscale, output=args.output)

elif args.command == 'Bestfit':

    from Bestfit import get_bestfit_params
    get_bestfit_params(dir=args.dir, output=args.output)

elif args.command == 'Model':
    
    from Models import print_available_models
    print_available_models()

elif args.command == 'Distrib':

    from Distribs import print_available_distribs
    print_available_distribs()
