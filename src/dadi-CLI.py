import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='Commands', dest='command')

# subparser for generating frequency spectrum
generate_fs_parser = subparsers.add_parser('GenerateFs', help='generate frequency spectrum from VCF files')
generate_fs_parser.add_argument('--output', type=str, required=True, help='the name of the output file')
generate_fs_parser.add_argument('--polarized', default=False, action='store_true', help='determine whether the resulting frequency spectrum is polarized or not')
generate_fs_parser.add_argument('--pop_ids', type=str, nargs='+', required=True, help='the population names for the samples')
generate_fs_parser.add_argument('--pop_info', type=str, required=True, help='the name of the file containing the population name of each sample')
generate_fs_parser.add_argument('--projections', type=int, nargs='+', required=True, help='the sample sizes after projection')
generate_fs_parser.add_argument('--vcf', type=str, required=True, help='the VCF file for generating frequency spectrum')
generate_fs_parser.add_argument('--bootstrap', type=int, help='the times to perform bootstrapping')
generate_fs_parser.add_argument('--chunk_size', type=int, help='the chunk size to divide the genomes for bootstrapping')
generate_fs_parser.set_defaults(generate_fs_parser=True)

# subparser for generating cache
generate_cache_parser = subparsers.add_parser('GenerateCache', help='generate selection coefficient cache for inferring DFE')
generate_cache_parser.add_argument('--additional_gammas', type=float, nargs='+', default=[], help='the additional positive population-scaled selection coefficients to cache for; default: []')
generate_cache_parser.add_argument('--demography_params', type=float, nargs='+', default=[], help='the parameters for the demographic model; default: []')
generate_cache_parser.add_argument('--gamma_bounds', type=float, nargs=2, default=[1e-4, 2000], help='the range of population-scaled selection coefficients to cache; default: [1e-4, 2000]')
generate_cache_parser.add_argument('--gamma_pts', type=int, default=50, help='the number of gamma grid points over which to integrate; default: 50')
generate_cache_parser.add_argument('--grids', type=int, nargs=3, default=[100, 200, 300], help='the sizes of grids; default: [100, 200, 300]')
generate_cache_parser.add_argument('--model', type=str, required=True, help='the name of the demographic model with selection')
generate_cache_parser.add_argument('--mp', default=False, action='store_true', help='determine whether generating cache with multiprocess or not; default: False')
generate_cache_parser.add_argument('--output', type=str, required=True, help='the name of the output file')
generate_cache_parser.add_argument('--sample_sizes', type=int, nargs='+', required=True, help='the sample sizes')
generate_cache_parser.set_defaults(generate_cache_parser=True)

# subparser for inferring demography
infer_demo_parser = subparsers.add_parser('InferDemography', help='infer demographic models from frequency spectrum')
infer_demo_parser.add_argument('--cuda', default=False, action='store_true', help='determine whether using GPUs to accelerate inference or not')
infer_demo_parser.add_argument('--fixed_params', type=str, nargs='+', default=[], help='')
infer_demo_parser.add_argument('--fs', type=str, required=True, help='the frequency spectrum used for inference')
infer_demo_parser.add_argument('--grids', type=float, nargs=3, default=[], help='')
infer_demo_parser.add_argument('--lower_bounds', type=float, nargs='+', required=True, help='the lower bounds of the inferred parameters')
infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
infer_demo_parser.add_argument('--model', type=str, required=True, help='the name of the demographic model')
infer_demo_parser.add_argument('--p0', type=float, nargs='+', required=True, help='the initial parameters for inference')
infer_demo_parser.add_argument('--upper_bounds', type=float, nargs='+', required=True, help='the upper bounds of the inferred parameters')
infer_demo_parser.add_argument('--output_dir', type=str, required=True, help='')
infer_demo_parser.add_argument('--output_prefix', type=str, required=True, help='')
infer_demo_parser.set_defaults(infer_demo_parser=True)

# subparser for inferring DFE
infer_dfe_parser = subparsers.add_parser('InferDFE', help='infer distribution of fitness effects from frequency spectrum')
infer_dfe_parser.add_argument('--cache1d', type=str, help='')
infer_dfe_parser.add_argument('--cache2d', type=str, help='')
infer_dfe_parser.add_argument('--cuda', default=False, action='store_true', help='')
infer_dfe_parser.add_argument('--fixed_params', type=str, nargs='+', default=[], help='')
infer_dfe_parser.add_argument('--fs', type=str, required=True, help='')
infer_dfe_parser.add_argument('--lower_bounds', type=float, nargs='+', required=True, help='the lower bounds of the inferred parameters')
infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
infer_dfe_parser.add_argument('--mixture', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
infer_dfe_parser.add_argument('--p0', type=float, nargs='+', required=True, help='the initial parameters for inference')
infer_dfe_parser.add_argument('--sele_dist', type=str, help='')
infer_dfe_parser.add_argument('--sele_dist2', type=str, help='')
infer_dfe_parser.add_argument('--theta', type=float, required=True, help='')
infer_dfe_parser.add_argument('--upper_bounds', type=float, nargs='+', required=True, help='the upper bounds of the inferred parameters')
infer_dfe_parser.set_defaults(infer_dfe_parser=True)

# subparser for plotting
plot_parser = subparsers.add_parser('Plot', help='plot 1D/2D frequency spectrum')
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
plot_parser.set_defaults(plot_parser=True)

# subparser for statistics and uncertainty analysis
stat_parser = subparsers.add_parser('Stat', help='perform statistical tests or generate simple statistics')
stat_parser.add_argument('--fs', type=str, help='...')
stat_parser.set_defaults(plot_parser=True)

model_parser = subparsers.add_parser('Model', help='display available demographic models')
dist_parser = subparsers.add_parser('Distrib', help='display available probability density functions for distribution of fitness effects')

args = parser.parse_args()

if args.command == 'GenerateFs':

    from GenerateFs import generate_fs
    generate_fs(vcf=args.vcf, output=args.output, bootstrap=args.bootstrap, chunk_size=args.chunk_size,
                pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

elif args.command == 'GenerateCache':

    if len(args.sample_sizes) > 2: raise Exception('Cannot generate cache with more than two populations')

    from GenerateCache import generate_cache
    generate_cache(model=args.model, grids=args.grids, demo_params=args.demography_params,
                   gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                   output=args.output, sample_sizes=args.sample_sizes, mp=args.mp)

elif args.command == 'InferDemography':

    from InferDemography import infer_demography
    infer_demography(fs=args.fs, model=args.model, grids=args.grids, output_dir=args.output_dir, 
                     output_prefix=args.output_prefix, p0=args.p0, upper_bounds=args.upper_bounds,
                     lower_bounds=args.lower_bounds, fixed_params=args.fixed_params, misid=args.misid, cuda=args.cuda)

elif args.command == 'InferDFE':

    from InferDFE import infer_dfe
    infer_dfe(fs=args.fs, cache1d=args.cache1d, cache2d=args.cache2d, sele_dist=args.sele_dist, sele_dist2=args.sele_dist2,
              output_dir=args.output_dir, output_prefix=args.output_prefix, p0=args.p0, upper_bounds=args.upper_bounds,
              lower_bounds=args.lower_bounds, fixed_params=args.fixed_params, mixture=args.mixture, misid=args.misid, cuda=args.cuda)

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

    from Stat import simple_stat, godambe_stat

elif args.command == 'Model':
    
    from Models import print_available_models
    print_available_models()

elif args.command == 'Distrib':

    from Distribs import print_available_distribs
    print_available_distribs()
