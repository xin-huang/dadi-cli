import dadi
import dadi.DFE as DFE

def get_dadi_pdf(pdf):
    if pdf == 'beta':
        return DFE.PDFs.beta
    elif pdf == 'biv_ind_gamma':
        return DFE.PDFs.biv_ind_gamma
    elif pdf == 'biv_lognormal':
        return DFE.PDFs.biv_lognormal
    elif pdf == 'exponential':
        return DFE.PDFs.exponential
    elif pdf == 'gamma':
        return DFE.PDFs.gamma
    elif pdf == 'lognormal':
        return DFE.PDFs.lognormal
    elif pdf == 'normal':
        return DFE.PDFs.normal
    else:
        raise Exception('Cannot find probability density function: ' + pdf)

def print_available_distribs():
    print('Probability density functions:')
    print('- beta')
    print('- biv_ind_gamma')
    print('- biv_lognormal')
    print('- exponential')
    print('- gamma')
    print('- lognormal')
    print('- normal')
