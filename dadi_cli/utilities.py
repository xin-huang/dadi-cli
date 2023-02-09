import dadi
import numpy as np


def pts_l_func(sample_sizes):
    """
    Description:
        Calculates plausible grid sizes for modeling a frequency spectrum.

    Arguments:
        sample_sizes list: Sample sizes.

    Returns:
        grid_sizes tuple: Grid sizes for modeling.
    """
    n = max(sample_sizes)
    grid_sizes = (int(n * 1.1) + 2, int(n * 1.2) + 4, int(n * 1.3) + 6)
    return grid_sizes


def cache_pts_l_func(sample_sizes):
    """
    Description:
        Calculates plausible grid sizes for modeling a frequency spectrum.

    Arguments:
        sample_sizes list: Sample sizes.

    Returns:
        grid_sizes tuple: Grid sizes for modeling.
    """
    n = max(sample_sizes)
    grid_sizes = (int(n * 2.2) + 2, int(n * 2.4) + 4, int(n * 2.6) + 6)
    return grid_sizes


def convert_to_None(inference_input, p0_len):
    """
    Description:
        Converts -1 in input parameters into None.

    Arguments:
        inference_input list: Input parameters for inference.
        p0_len int: Length of the initial parameters.

    Returns:
        inference_input list: Converted input parameters.
    """
    if inference_input == -1:
        inference_input = [inference_input] * p0_len
    inference_input = list(
        np.where(np.array(inference_input) == -1, None, np.array(inference_input))
    )
    return inference_input


def get_opts_and_theta(filename, gen_cache=False):
    """
    Description:
        Obtains optimized parameters and theta.

    Arguments:
        filename str: Name of the file.
        gen_cache bool: Make True for generating a cache to remove misid parameter when present.

    Returns:
        opts list: Optimized parameters.
        theta float: Population-scaled mutation rate.
    """
    opts = []
    param_names = []
    is_converged = False
    fid = open(filename, "r")
    for line in fid.readlines():
        if line.startswith("# Converged"):
            is_converged = True
            continue
        elif line.startswith("# Log(likelihood)"):
            param_names = line.rstrip().split("\t")
            continue
        elif line.startswith("#"):
            continue
        else:
            try:
                opts = [float(_) for _ in line.rstrip().split("\t")]
                break
            except ValueError:
                pass
    fid.close()

    theta = opts[-1]
    if gen_cache and "misid" in param_names:
        opts = opts[1:-2]
    else:
        opts = opts[1:-1]

    if not is_converged:
        print("No converged optimization results found.")

    return opts, theta
