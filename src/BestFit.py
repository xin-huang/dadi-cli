import glob, sys
import numpy as np
from src.Models import get_dadi_model_params
from src.Pdfs import get_dadi_pdf_params

def get_bestfit_params(path, misid, lbounds, ubounds, output, delta, model_name=None, pdf_name=None, pdf2d_asym=None, Nclose=3, Nbest=100):
    files = glob.glob(path)
    res, comments = [], []
    
    if pdf_name != None:
        if 'biv_' in pdf_name:
            if pdf2d_asym: pdf_name = pdf_name.replace('biv', 'biv_asym')
            else: pdf_name = pdf_name.replace('biv', 'biv_sym')
        params = '# Log(likelihood)\t' + "\t".join(get_dadi_pdf_params(pdf_name))
    elif model_name != None:
        params = '# Log(likelihood)\t' + "\t".join(get_dadi_model_params(model_name))
    else:
        params = ''

    if params != '':
        if misid: params += '\tmisid\ttheta\n'
        else: params += '\ttheta\n'

    for f in files:
        fid = open(f, 'r')
        for line in fid.readlines():
            if line.startswith('#'):
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
        print('No optimization results found')
        return

    res = np.array(sorted(res, reverse=True))
    opt_ll = res[0][0]
    # Filter out those results within delta threshold
    close_enough = res[1 - (opt_ll / res[:,0]) <= delta]

    with open(output, 'w') as fid:
        # Output command line
        fid.write('# {0}\n'.format(' '.join(sys.argv)))
        # Output all comment lines found
        fid.write('\n'.join(comments) + '\n')

        if len(close_enough) >= Nclose:
            print("Converged")
            # Spacer
            fid.write('#\n# Converged results\n')
            fid.write(params)
            for result in close_enough:
                fid.write('{0}\n'.format("\t".join([str(_) for _ in result])))
        else:
            print("No convergence")

        fid.write('#\n# Top {0} results\n'.format(Nbest))
        fid.write(params)
        for result in res[:Nbest]:
            fid.write('{0}\n'.format("\t".join([str(_) for _ in result])))

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

# def opt_params_converged(params):
#     for i in range(len(params)):
#         for j in range(len(params[0])):
#             if abs(float(params[0][j]) - float(params[i][j])) > 1: return False
    
#     return True


# def close2boundaries(params, lbounds, ubounds):
#     for i in range(len(params)):
#         if ubounds[i] != None:
#             if (ubounds[i] - float(params[i])) < 1: return True
#         if lbounds[i] != None:
#             if (float(params[i]) - lbounds[i]) < 1: return True

#     return False
