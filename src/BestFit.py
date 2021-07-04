import numpy as np
import glob

def get_bestfit_params(path, lbounds, ubounds, output):
   
    files = glob.glob(path)
    res = {} 
    for f in files:
        for line in open(f, 'r').readlines():
            line = line.rstrip().split()
            ll = line[0]
            popt = line[1:]
            if ll != '--':
                ll = float(ll)
                if ll not in res:
                    res[ll] = []
                res[ll].append(popt)

    ll = sorted(res)
    opt_ll = ll[-1]
    if len(res[opt_ll]) > 1: d = 0
    elif len(ll) < 2: d = np.inf
    else: d = ll[-1] - ll[-2]
    opt_params = res[opt_ll]

    if d < 0.05:
        if opt_params_converged(opt_params):
            if close2boundaries(opt_params[0], lbounds, ubounds):
                print("WARNING: The optimized parameters are close to the boundaries")
            print("CONVERGED RESULT FOUND!")
            print("The maximum likelihood: " + str(opt_ll))
            print("The best fit parameters: ")
            print("\t".join(opt_params[0]))
            with open(output, 'w') as f:
                f.write(str(opt_ll) + "\t" + "\t".join(opt_params[0]) + '\n')
        else:
            print("NO CONVERGENCE: Multiple optimized parameters found")
            print("The maximum likelihood: " + str(opt_ll))
            print("The optimized parameters:")
            for i in range(len(opt_params)):
                print("\t".join(opt_params[i]))
        return 0
    else:
        print("NO CONVERGENCE: Likelihoods are not converged")
        print("The maximum likelihood: " + str(opt_ll))
        print("The parameters with the maximum likelihood: ")
        print("\t".join(opt_params[0]))
        with open(output, 'w') as f:
            f.write(str(opt_ll) + "\t" + "\t".join(opt_params[0]) + '\n')
        return 1

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
