import glob

def get_bestfit_params(path, lbounds, ubounds, output):
    files = glob.glob(path + '/*')
    res = {}
    counts = {}
    for f in files:
        line = open(f, 'r').readline().rstrip().split()
        ll = line[0]
        params = line[1:]
        if ll != '--':
            ll = float(ll)
            res.update({ll: params})

    ll = sorted(res)
    d = ll[-1] - ll[-2]
    opt_ll = ll[-1]
    opt_params = res[opt_ll]

    if d < 0.05:
        if close2boundaries(opt_params, lbounds, ubounds):
             print("WARNING: The optimized parameters are closed to the boundaries")
        with open(output, 'w') as f:
            f.write(opt_ll + "\t" + "\t".join(opt_params) + '\n')
    else:
        print("NO CONVERGENCE: Cannot find the optimized parameters")

def close2boundaries(params, lbounds, ubounds):
    for i in range(len(params)):
        if (ubounds[i] - params[i]) < 0.05: return True
        if (params[i] - lbounds[i]) < 0.05: return True

    return False
