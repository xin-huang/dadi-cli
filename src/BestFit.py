import glob

def get_bestfit_params(path, lbounds, ubounds, output):
   
    files = glob.glob(path + '/*')
    res = []
    for f in files:
        line = open(f, 'r').readline().rstrip().split()
        ll = line[0]
        if ll != '--':
            popt = []
            for l in line:
                popt.append(float(l))
            res.append(popt)

    opt = sorted(res, key=lambda x: x[0])
    d = opt[-1] - opt[-2]
    opt_ll = opt[-1][0]
    opt_params = opt[-1][1:]

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
    else:
        print("NO CONVERGENCE: Likelihoods are not converged")
        print("The maximum likelihood: " + str(opt_ll))
        print("The parameters with the maximum likelihood: ")
        print("\t".join(opt_params[0]))
        with open(output, 'w') as f:
            f.write(str(opt_ll) + "\t" + "\t".join(opt_params[0]) + '\n')

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
