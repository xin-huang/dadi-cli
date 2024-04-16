import dadi, multiprocessing
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


# Worker functions for multiprocessing with demography/DFE inference
def worker_func(
    func: callable, 
    in_queue: multiprocessing.Queue, 
    out_queue: multiprocessing.Queue, 
    args: list, 
    use_gpu: bool = False
) -> None:
    """
    Worker function for multiprocessing that processes tasks defined by a function
    and its arguments, and uses queues for input and output handling.

    Parameters
    ----------
    func : callable
        The function to be executed. This function should accept the arguments specified
        by `args` and any additional parameters passed through the `in_queue`.
    in_queue : multiprocessing.Queue
        The input queue from which the worker retrieves tasks or seeds.
    out_queue : multiprocessing.Queue
        The output queue where the worker puts the results after processing.
    args : list
        A list of arguments that are passed to `func` when called. These should include
        all necessary parameters needed by `func` except those dynamically provided by
        the `in_queue`.
    use_gpu : bool, optional
        A flag that enables or disables GPU acceleration within the `func`. The default
        is False, which means GPU acceleration is not used unless explicitly enabled.

    """
    dadi.cuda_enabled(use_gpu)
    while True:
        new_seed = in_queue.get()
        np.random.seed(new_seed)
        results = func(*args)
        out_queue.put(results)


def calc_p0_from_bounds(
    lb: list[float], 
    ub: list[float]
) -> list[float]:
    """
    Calculates initial parameter values for optimization based on lower and upper bounds.

    Parameters
    ----------
    lb : list[float]
        List of lower bounds for each parameter.
    ub : list[float]
        List of upper bounds for each parameter.

    Returns
    -------
    list[float]
        A list of initial parameter estimates calculated from the provided bounds.

    """
    p0 = []
    for l, u in zip(lb, ub):
        if l == 0:
            p0.append((l + u) / 2)
        elif l*u > 0:
            p0.append(np.sqrt(l * u))
        else:
            p0.append((l+u) / 2)

    return p0


def top_opts(filename: str) -> list[list[float]]:
    """
    Reads and extracts optimized parameters from a file that logs parameter optimizations.

    Parameters
    ----------
    filename : str
        Name of the file containing the logged parameter optimizations. Each relevant line
        in this file should contain values separated by tabs, where the first value is the
        log-likelihood, followed by the parameter values, and ending with the theta value.

    Returns
    -------
    list[list[float]]
        A list of lists where each inner list contains the parameter values from one line of
        the file. These parameter values are sorted by their corresponding log-likelihood in
        descending order to show the best fits first.

    Raises
    ------
    ValueError
        If no fitting data is found in the file, indicating an issue with the file's content
        or format.

    """
    fid = open(filename, 'r')
    for line in fid.readlines():
        if line.startswith('# Log'):
            # Reset opts variable to avoid repeating entries.
            opts = []
            continue
        elif line.startswith('#'):
            continue
        else:
            try:
                opts.append([float(_) for _ in line.rstrip().split("\t")])
            except ValueError:
                pass
    fid.close()

    try:
        # Sort entries by log-likelihood
        opts = np.array(sorted(opts, reverse=True))
        # Remove log-likelihood and theta
        opts = [opt[1:-1] for opt in opts]
    except UnboundLocalError:
        raise ValueError(f"Fits not found in file {filename}.")

    return opts
