import glob, sys
import numpy as np
from typing import Optional
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf_params


def get_bestfit_params(
    path: str, 
    lbounds: list[float], 
    ubounds: list[float], 
    output: str, 
    delta: float, 
    Nclose: int = 3, 
    Nbest: int = 100
) -> Optional[np.array]:
    """
    Obtains best-fit parameters from optimization results, filters them based on log-likelihood
    differences, boundaries, and ranks them, finally outputs the results to a specified file.

    Parameters
    ----------
    path : str
        Path to results of inference.
    lbounds : list[float]
        Lower bounds of the optimized parameters.
    ubounds : list[float]
        Upper bounds of the optimized parameters.
    output : str
        Name of the output file where results will be written.
    delta : float
        Maximum difference for log-likelihoods compared to the best optimization
        log-likelihood to be considered convergent.
    Nclose : int, optional
        Number of best-fit results to be considered convergent (default is 3).
    Nbest : int, optional
        Number of best-fit results to be displayed (default is 100).

    Returns
    -------
    np.array | None
        Array of close enough results if the convergence criteria are met, None otherwise.

    Raises
    ------
    ValueError
        If no files are found at the specified path or if an incorrect path naming convention is used.

    """
    files = glob.glob(path)
    if files == []:
        raise ValueError(
            "No files or incorrect path naming (--input-prefix path name should end with InferDM)."
        )
    res, comments = [], []

    for file in files:
        with open(file, "r") as fid:
            for line in fid.readlines():
                if line.startswith("#"):
                    if line.startswith("# Log(likelihood)"):
                        params = line.rstrip()
                    else:
                        comments.append(line.rstrip())
                    continue
                # Parse numerical result
                try:
                    res.append([float(_) for _ in line.rstrip().split()])
                except ValueError:
                    # Ignore lines with a parsing error
                    pass

    if len(res) == 0:
        print("No optimization results found.")
        return

    # Need to have res as a numpy array for boundary filter
    res = np.array(sorted(res, reverse=True))

    # Filter results by boundary
    if ubounds is not None and lbounds is not None:
        res = boundary_filter(res, ubounds, lbounds)

    try:
        opt_ll = res[0][0]
    except IndexError:
        return

    # Filter out those results within delta threshold
    close_enough = res[1 - (opt_ll / res[:, 0]) <= delta]

    with open(output, "w") as fid:
        # Output command line
        fid.write("# {0}\n".format(" ".join(sys.argv)))
        # Output all comment lines found
        fid.write("\n".join(comments) + "\n")

        if len(close_enough) >= Nclose:
            print("Converged")
            if ubounds is not None and lbounds is not None:
                if close2boundaries(close_enough[0][1:-1], lbounds, ubounds):
                    print("WARNING: The converged parameters are close to the boundaries")
            # Spacer
            fid.write("#\n# Converged results\n")
            fid.write(params + "\n")
            for result in close_enough:
                fid.write("{0}\n".format("\t".join([str(_) for _ in result])))
        else:
            print("No convergence")

        fid.write("#\n# Top {0} results\n".format(Nbest))
        fid.write(params + "\n")
        for result in res[:Nbest]:
            fid.write("{0}\n".format("\t".join([str(_) for _ in result])))

    if len(close_enough) >= Nclose:
        return close_enough


def close2boundaries(
    params: list[float], 
    lbounds: list[float], 
    ubounds: list[float],
    threshold: float = 0.01
) -> bool:
    """
    Determines whether any parameter is close to its boundaries within a specified threshold.

    Parameters
    ----------
    params : list[float]
        Inferred parameters.
    lbounds : list[float]
        Lower bounds for the parameters.
    ubounds : list[float]
        Upper bounds for the parameters.
    threshold : float, optional
        Proportion of the boundary range that defines closeness (default is 0.01).

    Returns
    -------
    bool
        True if any parameter is within the threshold of its boundaries, False otherwise.

    """
    is_close2boundaries = False
    for i in range(len(params)):
        if ubounds[i] is not None and lbounds[i] is not None:
            bound_range = ubounds[i] - lbounds[i]
            if (params[i] - lbounds[i]) / bound_range < threshold or (
                ubounds[i] - params[i]
            ) / bound_range < threshold:
                is_close2boundaries = True
    return is_close2boundaries


def boundary_filter(
    res: np.array, 
    ubounds: list[float], 
    lbounds: list[float]
) -> np.array:
    """
    Filters inference results to exclude those where any parameter is outside specified boundaries.

    Parameters
    ----------
    res : np.array
        Inference results stored as an array, where each row represents an inference result and
        columns correspond to different parameters.
    lbounds : list[float]
        Lower bounds for each parameter.
    ubounds : list[float]
        Upper bounds for each parameter.

    Returns
    -------
    np.array
        Array with rows filtered based on boundaries.

    Raises
    ------
    ValueError
        If the number of upper boundaries does not match the number of lower boundaries,
        or if the number of boundaries does not match the number of parameters.

    """
    # Filter out results where the params are outside the boundaries
    # Doing this before getting opt_ll so it doesn't throw off convergence check
    if len(ubounds) != len(lbounds):
        raise ValueError("Number of upper boundaries do not match number of lower boundaries.")
    if len(ubounds) != len(res[0,1:-1]):
        raise ValueError("Number of boundaries do not match number of model parameters.")
    # ub_bool = res[:,1] <= ubounds[0]
    # lb_bool = res[:,1] >= lbounds[0]
    bool_filter = (res[:,1] <= ubounds[0]) & (res[:,1] >= lbounds[0])
    for i in range(1,len(res[0,1:-1])):
        if ubounds[i] is not None and lbounds[i] is not None:
            # ub_bool = np.logical_and(ub_bool, res[:,i+1] <= ubounds[i])
            # lb_bool = np.logical_and(lb_bool, res[:,i+1] >= lbounds[i])
            bool_filter = np.logical_and(bool_filter, (res[:,i+1] <= ubounds[i]) & (res[:,i+1] >= lbounds[i]))
    # return res[np.logical_and(ub_bool, lb_bool)]
    return res[bool_filter]
