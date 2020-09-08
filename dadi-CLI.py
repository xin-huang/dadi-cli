import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='Commands', dest='command')

# subparser for generating frequency spectrum
generate_fs_parser = subparsers.add_parser('GenerateFs', help='generate frequency spectrum from VCF files or project down frequency spectrum')
generate_fs_parser.add_argument('--fs', type=str, help='the frequency spectrum for projection')
generate_fs_parser.add_argument('--output', type=str, required=True, help='the name of the output file')
generate_fs_parser.add_argument('--polarized', default=False, action='store_true', help='determine whether the resulting frequency spectrum is polarized or not')
generate_fs_parser.add_argument('--pop_ids', type=str, nargs='+', help='the population names for the samples')
generate_fs_parser.add_argument('--pop_info', type=str, help='the name of the file containing the population name of each sample')
generate_fs_parser.add_argument('--projections', type=int, nargs='+', required=True, help='the sample sizes after projection')
generate_fs_parser.add_argument('--vcf', type=str, help='the VCF file for generating frequency spectrum')
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
infer_demo_parser = subparsers.add_parser('InferDemography', help='infer demography')
infer_demo_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
infer_demo_parser.set_defaults(infer_demo_parser=True)

# subparser for inferring DFE
infer_dfe_parser = subparsers.add_parser('InferDFE', help='infer DFE')
infer_dfe_parser.add_argument('--misid', default=False, action='store_true', help='determine whether adding a parameter for misidentifying ancestral alleles or not')
infer_dfe_parser.set_defaults(infer_dfe_parser=True)

# subparser for plotting
plot_parser = subparsers.add_parser('Plot', help='plot frequency spectrum')
plot_parser.add_argument('cmd5_options', type=int, help='...')
plot_parser.set_defaults(plot_parser=True)

# subparser for statistics and uncertainty analysis
stat_parser = subparsers.add_parser('Stat', help='...')
stat_parser.add_argument('cmd5_options', type=int, help='...')
stat_parser.set_defaults(plot_parser=True)

args = parser.parse_args()

if args.command == 'GenerateFs':

    if (args.vcf != None) and (args.fs != None): raise Exception('Cannot use --vcf and --fs at the same time')
    if args.vcf != None:
          if (args.pop_info == None) and (args.pop_ids == None): 
              raise Exception('--pop_info and --pop_ids are required when using --vcf')
          elif args.pop_info == None: raise Exception('--pop_info is required when using --vcf')
          elif args.pop_ids == None: raise Exception('--pop_ids is required when using --vcf')

    from GenerateFs import generate_fs
    generate_fs(vcf=args.vcf, fs=args.fs, output=args.output, 
                pop_ids=args.pop_ids, pop_info=args.pop_info, projections=args.projections, polarized=args.polarized)

elif args.command == 'GenerateCache':

    if len(args.sample_sizes) > 2: raise Exception('Cannot generate cache with more than two populations')

    from GenerateCache import generate_cache
    generate_cache(model=args.model, grids=args.grids, demo_params=args.demography_params,
                   gamma_bounds=args.gamma_bounds, gamma_pts=args.gamma_pts, additional_gammas=args.additional_gammas,
                   output=args.output, sample_sizes=args.sample_sizes, mp=args.mp)

elif args.command == 'InferDemography':
    print("InferDemography")
elif args.command == 'InferDFE':
    print("InferDFE")
elif args.command == 'Plot':
    print("Plot")
elif args.command == 'Stat':
    print("Stat")
