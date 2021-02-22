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

def get_dadi_pdf_params(pdf):
    if pdf == 'beta':
        return ['alpha', 'beta']
    elif pdf == 'biv_sym_ind_gamma':
        return ['shape', 'scale']
    elif pdf == 'biv_asym_ind_gamma':
        return ['shape1', 'scale1', 'shape2', 'scale2']
    elif pdf == 'biv_sym_lognormal':
        return ['log(mu)', 'log(sigma)', 'rho']
    elif pdf == 'biv_asym_lognormal':
        return ['log(mu1)', 'log(sigma1)', 'log(mu2)', 'log(sigma2)', 'rho']
    elif pdf == 'exponential':
        return ['scale']
    elif pdf == 'gamma':
        return ['shape', 'scale']
    elif pdf == 'lognormal':
        return ['log(mu)', 'log(sigma)']
    elif pdf == 'normal':
        return ['mu', 'sigma']
    else:
        raise Exception('Probability density function ' + pdf + ' is not available!')
        
def print_available_pdfs():
    print('Available probability density functions:')
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

        If len(params) == 2, then params = [alpha, beta] by assuming alpha and beta are equal in the two populations
        If len(params) == 4, then params = [alpha1, alpha2, beta1, beta2]
        If len(params) == 3 or 5, then the last parameter is ignored
    '''
    biv_lognormal = '''
        Bivariate lognormal probability density function.

        If len(params) == 3, then params = [mu, sigma, rho] by assuming mu and sigma are equal in the two populations
        If len(params) == 5, then params = [mu1, mu2, sigma1, sigma2, rho]
    '''
    exponential = '''
        Exponential probability density function.

        params = [scale]
    '''
    gamma = '''
        Gamma probability density function.

        params = [alpha, beta] = [shape, scale]
    '''
    lognormal = '''
        Lognormal probability density function.

        params = [log(mu), log(sigma)]
    '''
    normal = '''
        Normal probability density function.

        params = [mu, sigma]
    '''

    if pdf_name == 'beta': print('- beta:\n' + beta)
    elif pdf_name == 'biv_ind_gamma': print('- biv_ind_gamma:\n' + biv_ind_gamma)
    elif pdf_name == 'biv_lognormal': print('- biv_lognormal:\n' + biv_lognormal)
    elif pdf_name == 'exponential': print('- exponential:\n' + exponential)
    elif pdf_name == 'gamma': print('- gamma:\n' + gamma)
    elif pdf_name == 'lognormal': print('- lognormal:\n' + lognormal)
    elif pdf_name == 'normal': print('- normal:\n' + normal)
    else: raise Exception('Probability density function ' + pdf_name + ' is not available!')
