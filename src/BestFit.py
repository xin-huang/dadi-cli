import glob, sys
import numpy as np

def get_bestfit_params(path, lbounds, ubounds, output, delta=0.05, Nclose=3, Nbest=100):
    files = glob.glob(path)
    res, comments = [], []
    for f in files:
        for line in open(f, 'r').readlines():
            if line.startswith('#'):
                comments.append(line.rstrip())
                continue
            # Parse numerical result
            try:
                res.append([float(_) for _ in line.rstrip().split()])
            except ValueError:
                # Ignore lines with a parsing error
                pass

    if len(res) == 0:
        print('No optimization results found')
        return

    res = np.array(sorted(res, reverse=True))
    opt_ll = res[0][0]
    # Filter out those results within delta threshold
    close_enough = res[res[:,0] > opt_ll - delta]

    with open(output, 'w') as fid:
        # Output command line
        fid.write('# {0}\n'.format(' '.join(sys.argv)))
        # Output all comment lines found
        fid.write('\n'.join(comments) + '\n')

        if len(close_enough) >= Nclose:
            print("Converged")
            # Spacer
            fid.write('#\n# Converged results\n')
            for result in close_enough:
                fid.write('{0}\n'.format(result))
        else:
            print("No convergence")

        fid.write('#\n# Top {0} results\n'.format(Nbest))
        for result in res[:Nbest]:
            fid.write('{0}\n'.format(result))

    if len(close_enough) >= Nclose:
        return close_enough

#    if d < 0.05:
#        if opt_params_converged(opt_params):
#            if close2boundaries(opt_params[0], lbounds, ubounds):
#                print("WARNING: The optimized parameters are close to the boundaries")
#            print("CONVERGED RESULT FOUND!")
#            print("The maximum likelihood: " + str(opt_ll))
#            print("The best fit parameters: ")
#            print("\t".join(opt_params[0]))
#            with open(output, 'w') as f:
#                f.write(str(opt_ll) + "\t" + "\t".join(opt_params[0]) + '\n')
#        else:
#            print("NO CONVERGENCE: Multiple optimized parameters found")
#            print("The maximum likelihood: " + str(opt_ll))
#            print("The optimized parameters:")
#            for i in range(len(opt_params)):
#                print("\t".join(opt_params[i]))
#        return True
#    else:
#        print("NO CONVERGENCE: Likelihoods are not converged")
#        print("The maximum likelihood: " + str(opt_ll))
#        print("The parameters with the maximum likelihood: ")
#        print("\t".join(opt_params[0]))
#        with open(output, 'w') as f:
#            f.write(str(opt_ll) + "\t" + "\t".join(opt_params[0]) + '\n')

def opt_params_converged(params):
    for i in range(len(params)):
        for j in range(len(params[0])):
            if abs(float(params[0][j]) - float(params[i][j])) > 1: return False
    
    return True


def close2boundaries(params, lbounds, ubounds):
    for i in range(len(params)):
        if ubounds[i] != None:
            if (ubounds[i] - float(params[i])) < 1: return True
        if lbounds[i] != None:
            if (float(params[i]) - lbounds[i]) < 1: return True

    return False
