from dadi import Numerics, Integration, PhiManip, Spectrum


def split_mig_fix_T(params, ns, pts):
    """
    Instantaneous split into two populations of specified size, with symmetric migration and a fixed time point.
    """
    nu1, nu2, m = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, 0.3, nu1, nu2, m12=m, m21=m)

    fs = Spectrum.from_phi(phi, ns, (xx, xx))
    return fs


split_mig_fix_T.__param_names__ = ["nu1", "nu2", "m"]


def split_mig_fold(params, ns, pts):
    """
    Instantaneous split into two populations of specified size, with symmetric migration and a fixed time point.
    """
    nu1, nu2, T, m = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T, nu1, nu2, m12=m, m21=m)

    fs = Spectrum.from_phi(phi, ns, (xx, xx))
    fs = fs.fold()
    return fs


split_mig_fold.__param_names__ = ["nu1", "nu2", "T", "m"]


def split_no_mig(params, ns, pts):
    """
    Instantaneous split into two populations of specified size, with symmetric migration and a fixed time point.
    """
    nu1, nu2, T = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T, nu1, nu2, m12=0, m21=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx))
    return fs


split_no_mig.__param_names__ = ["nu1", "nu2", "T"]

# Selection models for split_mig_fix_T
def split_mig_fix_T_sel(params, ns, pts):
    """
    split_mig_fix_T with independent selection
    """
    nu1, nu2, m, gamma1, gamma2 = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx, gamma=gamma1)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(
        phi, xx, 0.3, nu1, nu2, m12=m, m21=m, gamma1=gamma1, gamma2=gamma2
    )

    fs = Spectrum.from_phi(phi, ns, (xx, xx))
    return fs


split_mig_fix_T_sel.__param_names__ = ["nu1", "nu2", "m", "gamma1", "gamma2"]


def split_mig_fix_T_one_s(params, ns, pts):
    """
    split_mig_fix_T with shared selection
    """
    nu1, nu2, m, gamma = params
    return split_mig_fix_T_sel([nu1, nu2, m, gamma, gamma], ns, pts)


split_mig_fix_T_one_s.__param_names__ = ["nu1", "nu2", "m", "gamma"]
