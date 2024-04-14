import dadi
import numpy as np
from typing import Optional


def pts_l_func(
    sample_sizes: list[int]
) -> tuple[int]:
    """
    Calculates plausible grid sizes for modeling a frequency spectrum based on the maximum sample size.

    Parameters
    ----------
    sample_sizes : list[int]
        List of sample sizes for which to calculate the grid sizes.

    Returns
    -------
    tuple[int]
        Calculated grid sizes for numerical integration, slightly increasing with each step to ensure
        coverage and accuracy.

    """
    n = max(sample_sizes)
    grid_sizes = (int(n * 1.1) + 2, int(n * 1.2) + 4, int(n * 1.3) + 6)
    return grid_sizes


def cache_pts_l_func(
    sample_sizes: list[int]
) -> tuple[int]:
    """
    Calculates plausible grid sizes for modeling a frequency spectrum by scaling up the maximum sample size.

    Parameters
    ----------
    sample_sizes : list[int]
        List of sample sizes for which to calculate the grid sizes.

    Returns
    -------
    tuple[int]
        A tuple of integers representing the grid sizes for modeling. These sizes are scaled versions
        of the maximum sample size, incremented by small constants to ensure computational robustness.

    """
    n = max(sample_sizes)
    grid_sizes = (int(n * 2.2) + 2, int(n * 2.4) + 4, int(n * 2.6) + 6)
    return grid_sizes


def convert_to_None(
    inference_input: list[float], 
    p0_len: int
) -> list[Optional[float]]:
    """
    Converts '-1' values in a list of input parameters to 'None', typically used to 
    signify missing or undefined values for parameter inference.

    Parameters
    ----------
    inference_input : list[float]
        List of input parameters for inference, where '-1' signifies a value to be converted to 'None'.
    p0_len : int
        Expected length of the list of initial parameters. Ensures the output list matches this length.

    Returns
    -------
    list[Optional[float]]
        A new list of input parameters where '-1' values have been replaced with 'None'.

    """
    if inference_input == -1:
        inference_input = [inference_input] * p0_len
    inference_input = list(
        np.where(np.array(inference_input) == -1, None, np.array(inference_input))
    )
    return inference_input


def get_opts_and_theta(
    filename: str, 
    gen_cache: bool = False
) -> tuple[list[float], float]:
    """
    Parses a file to obtain optimized parameters and the population-scaled mutation rate (theta).

    Parameters
    ----------
    filename : str
        The path to the file containing the optimization results.
    gen_cache : bool, optional
        If True, generates a cache that excludes the misidentification parameter, if present.

    Returns
    -------
    tuple[list[float], float]
        A tuple containing a list of the optimized parameters and the value of theta.
        If the 'gen_cache' is True and 'misid' is found, 'misid' is excluded from the returned parameters.

    Notes
    -----
    The file should contain lines starting with '# Converged' to indicate convergence,
    '# Log(likelihood)' followed by parameter names, and other lines with numerical values
    for parameters. The function checks for convergence and reads the parameters accordingly.

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
