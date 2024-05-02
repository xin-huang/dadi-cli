import argparse
from dadi_cli.parsers.common_arguments import *
from dadi_cli.parsers.argument_validation import *
from dadi_cli.GenerateFs import *


def _run_generate_fs(args: argparse.Namespace) -> None:
    """
    Executes the generation of a frequency spectrum from a VCF file based on the specified
    parameters contained in 'args'. This function configures the settings for the frequency
    spectrum generation, handles directory creation for output, and invokes the generation process.

    Parameters
    ----------
    args : argparse.Namespace
        A namespace object from argparse containing all the necessary parameters to configure
        the frequency spectrum generation. Expected attributes include:
        - mask_shared : bool
            If True, uses a 'shared' mask.
        - mask : bool
            If True and mask_shared is False, uses a 'singletons' mask.
        - output : str
            The output directory to save results.
        - vcf : str
            Path to the VCF file from which the frequency spectrum is generated.
        - bootstrap : int
            Number of bootstrap resamples to perform.
        - chunk_size : int
            Size of the chunks for processing the VCF file.
        - seed : int
            Random seed for bootstrap resampling.
        - pop_ids : list
            List of population identifiers.
        - pop_info : str
            Information about populations.
        - projections : list
            List of integers representing projected sample sizes per population.
        - polarized : bool
            Whether to use polarized allele frequencies.
        - marginalize_pops : list
            Marginalize over a list of populations.
        - subsample : bool
            Whether to subsample data.

    """
    if args.mask_shared:
        mask = "shared"
    elif args.mask:
        mask = "singletons"
    else:
        mask = ""

    make_dir(args.output)

    generate_fs(
        vcf=args.vcf,
        output=args.output,
        bootstrap=args.bootstrap,
        chunk_size=args.chunk_size,
        seed=args.seed,
        pop_ids=args.pop_ids,
        pop_info=args.pop_info,
        projections=args.projections,
        polarized=args.polarized,
        marginalize_pops=args.marginalize_pops,
        subsample=args.subsample,
        masking=mask,
    )


def add_generate_fs_parsers(subparsers: argparse.ArgumentParser) -> None:
    """
    Adds command-line argument parsers for the 'GenerateFs' command to an existing collection of subparsers.
    This function configures various options needed to generate a frequency spectrum from VCF files.

    Parameters
    ----------
    subparsers : argparse.ArgumentParser
        The subparsers object from an ArgumentParser where the new 'GenerateFs' subparser will be added.

    """
    parser = subparsers.add_parser(
        "GenerateFs", help="Generate frequency spectrum from VCF files."
    )

    parser.add_argument(
        "--polarized",
        default=False,
        action="store_true",
        help="Determine whether the resulting frequency spectrum is polarized or not; Default: False.",
    )

    parser.add_argument(
        "--pop-ids",
        type=str,
        nargs="+",
        required=True,
        help="Population names for the samples.",
        dest="pop_ids",
    )

    parser.add_argument(
        "--pop-info",
        type=existed_file,
        required=True,
        help="Name of the file containing the population name of each sample.",
        dest="pop_info",
    )

    parser.add_argument(
        "--projections",
        type=positive_int,
        nargs="+",
        required=True,
        help="Sample sizes after projection; If you do not want to project down your data, please input the original sample sizes of your data.",
    )

    parser.add_argument(
        "--vcf",
        type=existed_file,
        required=True,
        help="Name of the VCF file for generating frequency spectrum.",
    )

    parser.add_argument(
        "--bootstrap", type=positive_int, help="Times to perform bootstrapping."
    )

    parser.add_argument(
        "--chunk-size",
        type=positive_int,
        help="Chunk size to divide the genomes for bootstrapping.",
        dest="chunk_size",
    )

    parser.add_argument(
        "--subsample",
        default=False,
        action="store_true",
        dest="subsample",
        help="Subsample from the VCF when generating the fs using the given pop-ids and subsample calls based on the projections passed in. Default: None.",
    )

    parser.add_argument(
        "--mask-singletons",
        default=False,
        action="store_true",
        dest="mask",
        help="Mask the singletons that are exclusive to each population. Default: None.",
    )

    parser.add_argument(
        "--mask-shared-singletons",
        default=False,
        action="store_true",
        dest="mask_shared",
        help="Mask the singletons that are exclusive to each population and shared between populations. Default: None.",
    )

    parser.add_argument(
        "--marginalize-pop-ids",
        type=str,
        nargs="+",
        help="Population names you want to marginalize (remove) from the full fs. Default: None.",
        dest="marginalize_pops",
    )

    add_output_argument(parser)
    add_seed_argument(parser)
    parser.set_defaults(runner=_run_generate_fs)
