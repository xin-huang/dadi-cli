'''
Library module of custom dadi models
'''
from dadi import Numerics, PhiManip, Integration, Spectrum


def out_of_africa(params, ns, pts):
    '''
    Gutenkunst et al. 2009 Out-of-Africa model.
    
    params = (nuAf, nuB, nuEu0, nuEu, nuAs0, nuAs, mAfB, mAfEu, mAfAs, mEuAs, TAf, TB, TEuAs)
    ns = (n1,n2,n3)

    Instantanous size change followed by exponential growth with no population
    split.

    nuAf: Ratio of population 1 size after instantanous change to ancient
          population size
    nuB: Ratio of bottleneck population size to ancient populatiuon after
         split from nuAf
    nuEu0: Ratio of population 2 size to ancient population size after
           split from nuB
    nuEu: Ratio of population 2 size to ancient population size after
          time TEuAs
    nuAs0: Ratio of population 3 size to ancient population size after
           split from nuB
    nuAs: Ratio of population 3 size to ancient population size after
          time TEuAs
    mAfB: Migration rate between population 1 and bottleneck population
    mAfEu: Migration rate between population 1 and population 2
    mAfAs: Migration rate between population 1 and population 3
    mEuAs: Migration rate between population 2 and population 3
    TAf: Time in the past at which instantaneous change happened for
         population 1 (in units of 2*Na generations) 
    TB: Time in the past at which instantaneous change happened for
         bottleneck population (in units of 2*Na generations) 
    TEuAs: Time in the past at which instantaneous change happened for
           population 2 and population 3 (in units of 2*Na generations) 

    n1,n2,n3: Sample sizes of resulting Spectrum
    pts: Number of grid points to use in integration.
    '''
    nuAf, nuB, nuEu0, nuEu, nuAs0, nuAs, \
        mAfB, mAfEu, mAfAs, mEuAs, \
        TAf, TB, TEuAs = params
    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = Integration.one_pop(phi, xx, TAf, nu=nuAf)

    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(
        phi, xx, TB, nu1=nuAf, nu2=nuB, m12=mAfB, m21=mAfB)

    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)

    def nuEu_func(t):
        return nuEu0 * (nuEu/nuEu0) ** (t/TEuAs)
    def nuAs_func(t):
        return nuAs0 * (nuAs/nuAs0) ** (t/TEuAs)
    phi = Integration.three_pops(phi, xx, TEuAs, nu1=nuAf, nu2=nuEu_func,
                                 nu3=nuAs_func, m12=mAfEu, m13=mAfAs,
                                 m21=mAfEu, m23=mEuAs, m31=mAfAs, m32=mEuAs)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
out_of_africa.__param_names__ = ['nuAf', 'nuB', 'nuEu0',
                                 'nuEu', 'nuAs0', 'nuAs',
                                 'mAfB', 'mAfEu', 'mAfAs', 'mEuAs',
                                 'TAf', 'TB', 'TEuAs']


def out_of_africa_no_mig(params, ns, pts):
    '''
    Gutenkunst et al. 2009 Out-of-Africa model with migration rates set to 0.
    '''
    nuAf, nuB, nuEu0, nuEu, nuAs0, nuAs, TAf, TB, TEuAs = params
    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = Integration.one_pop(phi, xx, TAf, nu=nuAf)

    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(
        phi, xx, TB, nu1=nuAf, nu2=nuB, m12=0, m21=0)

    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)

    def nuEu_func(t):
        return nuEu0 * (nuEu/nuEu0) ** (t/TEuAs)
    def nuAs_func(t):
        return nuAs0 * (nuAs/nuAs0) ** (t/TEuAs)
    phi = Integration.three_pops(phi, xx, TEuAs, nu1=nuAf, nu2=nuEu_func,
                                 nu3=nuAs_func, m12=0, m13=0,
                                 m21=0, m23=0, m31=0, m32=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
out_of_africa_no_mig.__param_names__ = ['nuAf', 'nuB', 'nuEu0',
                                        'nuEu', 'nuAs0', 'nuAs',
                                        'TAf', 'TB', 'TEuAs']