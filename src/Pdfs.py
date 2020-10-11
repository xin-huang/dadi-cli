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
        raise Exception('Probability density function ' + pdf + ' is not available!')

def print_available_pdfs():
    print('Probability density functions:')
    print('- beta')
    print('- biv_ind_gamma')
    print('- biv_lognormal')
    print('- exponential')
    print('- gamma')
    print('- lognormal')
    print('- normal')

def print_pdf_details(pdf_name):
    
    beta = '''
        Beta probability density function.
  
        params = [alpha, beta]
    '''
    biv_ind_gamma = '''
        Bivariate independent gamma probability density function.
    '''
    biv_lognormal = '''
        Bivariate lognormal probability density function.
    '''
    exponential = '''
        Exponential probability density function.
    '''
    gamma = '''
        Gamma probability density function.
    '''
    lognormal = '''
        Lognormal probability density function.
    '''
    normal = '''
        Normal probability density function.
    '''

    if pdf_name == beta: print('- beta:\n' + beta)
    elif pdf_name == biv_ind_gamma: print('- biv_ind_gamma:\n' + biv_ind_gamma)
    elif pdf_name == biv_lognormal: print('- biv_lognormal:\n' + biv_lognormal)
    elif pdf_name == exponential: print('- exponential:\n' + exponential)
    elif pdf_name == gamma: print('- gamma:\n' + gamma)
    elif pdf_name == lognormal: print('- lognormal:\n' + lognormal)
    elif pdf_name == normal: print('- normal:\n' + normal)
    else: raise Exception('Probability density function ' + pdf_name + ' is not available!')
