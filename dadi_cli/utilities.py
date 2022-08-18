import dadi
import numpy as np

def pts_l_func(fs):
    """
    Description:
        Calculates plausible grid sizes for modeling a frequency spectrum.

    Arguments:
        fs dadi.Spectrum: Frequency spectrum for modeling.

    Returns:
        grid_sizes tuple: Grid sizes for modeling.
    """
    n = max(fs.sample_sizes)
    grid_sizes = (int(n*1.1)+2, int(n*1.2)+4, int(n*1.3)+6)
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
    if inference_input == -1: inference_input = [inference_input]*p0_len
    inference_input = list(np.where(np.array(inference_input) == -1, None, np.array(inference_input)))
    return inference_input


def get_opts_and_theta(filename, nomisid):
    """
    Description:
        Obtains optimized parameters and theta.

    Arguments:
        filename str: Name of the file.
        nomisisid bool: True if no misid parameter is in the optimized parameters;
                        False if a misid parameter is in the optimized parameters.

    Returns:
        opts list: Optimized parameters.
        theta float: Population-scaled mutation rate.
    """
    opts = []
    fid = open(filename, 'r')
    for line in fid.readlines():
        if line.startswith('# Top'): break
        elif line.startswith('#'): continue
        else:
            try:
                opts.append([float(_) for _ in line.rstrip().split()])
            except ValueError:
                pass
    fid.close()

    theta = 0
    if len(opts) == 0:
        print('No optimization results found.')
    else:
        theta = opts[0][-1]
        if not nomisid: opts = opts[0][1:-2]
        else: opts = opts[0][1:-1]

    return opts, theta
