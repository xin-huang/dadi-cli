import glob

def get_bestfit_params(dir, output):
    files = glob.glob(dir + '/*')
    res = {}
    for f in files:
        line = open(f, 'r').readline().rstrip().split()
        if line[0] != '--':
            res.update({float(line[0]): line})

    with open(output, 'w') as f:
        f.write("\t".join(res[sorted(res)[-1]]) + '\n')
