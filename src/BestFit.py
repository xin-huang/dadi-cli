def get_bestfit_params(params, lbounds, ubounds, output):
    
    with open(params, 'r') as f:
        res = {}
        for line in f:
            line = line.rstrip().split()
            ll = line[0]
            popt = line[1:]
            if ll != '--':
                ll = float(ll)
                if ll not in res:
                    res[ll] = []
                res[ll].append(popt)

    ll = sorted(res)
    d = ll[-1] - ll[-2]
    opt_ll = ll[-1]
    opt_params = res[opt_ll]

    if d < 0.05:
        if opt_params_converged(opt_params):
            if close2boundaries(opt_params[0], lbounds, ubounds):
                print("WARNING: The optimized parameters are close to the boundaries")
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

def opt_params_converged(params):
    for i in range(len(params)):
        for j in range(len(params[0])):
            if abs(float(params[0][j]) - float(params[i][j])) > 1: return False
    
    return True


def close2boundaries(params, lbounds, ubounds):
    for i in range(len(params)):
        if (ubounds[i] - float(params[i])) < 1: return True
        if (float(params[i]) - lbounds[i]) < 1: return True

    return False
