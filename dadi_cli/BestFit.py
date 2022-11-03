import glob, sys
import numpy as np
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf_params


def get_bestfit_params(path, lbounds, ubounds, output, delta, Nclose=3, Nbest=100):
    """
    Description:
        Obtains bestfit parameters.

    Arguments:
        path str: Path to results of inference.
        lbounds list: Lower bounds of the optimized parameters.
        ubounds list: Upper bounds of the optimized parameters.
        output str: Name of the output file.
        delta float: Max percentage difference for log-likliehoods compared to the best optimization
                     log-likliehood to be consider convergent.
        Nclose int: Number of best-fit results to be consider convergent. 
        Nbest int: Number of best-fit results to be displayed.
    """
    files = glob.glob(path)
    if files == []:
        raise ValueError(
            "No files or incorrect path naming (--input-prefix path name should end with InferDM)."
        )
    res, comments = [], []

    for f in files:
        fid = open(f, "r")
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
        fid.close()

    if len(res) == 0:
        print("No optimization results found.")
        return

    res = np.array(sorted(res, reverse=True))
    opt_ll = res[0][0]
    # Filter out those results within delta threshold
    close_enough = res[1 - (opt_ll / res[:, 0]) <= delta]

    with open(output, "w") as fid:
        # Output command line
        fid.write("# {0}\n".format(" ".join(sys.argv)))
        # Output all comment lines found
        fid.write("\n".join(comments) + "\n")

        if len(close_enough) >= Nclose:
            print("Converged")
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


def close2boundaries(params, lbounds, ubounds):
    """
    Description:
        Helper function for detemining whether a parameter is close to the boundaries.

    Arguments:
        params list: Inferred parameters.
        lbounds list: Lower bounds for the parameters.
        ubounds list: Upper bounds for the parameters.

    Returns:
        is_close2boundaries: True, if any parameter is close to the boundaries;
                             False, otherwise.
    """
    is_close2boundaries = False
    for i in range(len(params)):
        if ubounds[i] is not None and lbounds[i] is not None:
            bound_range = ubounds[i] - lbounds[i]
            if (params[i] - lbounds[i]) / bound_range < 0.01 or (
                ubounds[i] - params[i]
            ) / bound_range < 0.01:
                is_close2boundaries = True
    return is_close2boundaries
