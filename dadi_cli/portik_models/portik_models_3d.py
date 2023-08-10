'''
Models for testing various three population scenarios.
Adapted from https://github.com/dportik
'''
from dadi import Numerics, PhiManip, Integration, Spectrum

###############################################################################
# Basic models of (no gene flow / gene flow)
# between (all / some) population pairs
###############################################################################


def split_nomig(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration does not occur between any population pair.
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 6 parameters
    nu1, nuA, nu2, nu3, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_nomig.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'T1', 'T2']


def split_symmig_all(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration is symmetrical between all population pairs (ie 1<->2, 2<->3,
    and 1<->3).
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1, nuA, nu2, nu3, mA, m1, m2, m3, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_symmig_all.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm1', 'm2', 'm3', 'T1', 'T2']


def split_symmig_adjacent(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Assume 2 occurs in between populations 1 and 3, which do not come in to
    contact with one another.
    Migration is symmetrical between 'adjacent' population pairs
    (ie 1<->2, 2<->3, but not 1<->3).
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 9 parameters
    nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_symmig_adjacent.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm1', 'm2', 'T1', 'T2']

################################################################################
# Various models based on forest refugia timing,
# all with symmetric gene flow estimates
###############################################################################


def refugia_adj_1(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur.
    Split between pops 2 and 3, gene flow does not occur.
    Period of symmetric secondary contact occurs between
    adjacent populations (ie 1<->2, 2<->3, but not 1<->3)
    after all splits are complete.
    'longest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3 (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    T3: The scaled time between the split of pops 2 and 3 and the present
    (in units of 2*Na generations).
    """
    # 9 parameters
    nu1, nuA, nu2, nu3, m1, m2, T1, T2, T3 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T3, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_1.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'm1', 'm2', 'T1', 'T2', 'T3']


def refugia_adj_2(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur.
    Split between pops 2 and 3, with gene flow. After appearance of 2 and 3,
    gene flow also occurs between 1 and 2.
    'shorter isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 8 parameters
    nu1, nuA, nu2, nu3, m1, m2, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_2.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'm1', 'm2', 'T1', 'T2']


def refugia_adj_3(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur,
    but then secondary contact occurs. Split between pops 2 and 3 occurs with
    gene flow, and gene flow happens between 1 and 2 as well.
    'shortest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1, nuA, nu2, nu3, mA, m1, m2, T1a, T1b, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1a, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = Integration.two_pops(phi, xx, T1b, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_3.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm1', 'm2', 'T1a', 'T1b', 'T2']

###############################################################################
# Various models based on ancient migration and contemporary isolation
###############################################################################


def ancmig_adj_3(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), with gene flow, which then stops.
    Split between pops 2 and 3, gene flow does not occur at all.
    'longest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1a: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T1b: The scaled time for no gene flow between pops 1 and (2, 3)
    (in units of 2*Na generations).
    T2: The scaled time between the cessation of gene flow and the split of
    pops 2 and 3 (in units of 2*Na generations).
    """
    # 8 parameters
    nu1, nuA, nu2, nu3, mA, T1a, T1b, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1a, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = Integration.two_pops(phi, xx, T1b, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
ancmig_adj_3.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'T1a', 'T1b', 'T2']


def ancmig_adj_2(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), with gene flow. Split
    between pops 2 and 3, and all gene flow ceases.
    'shorter isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 7 parameters
    nu1, nuA, nu2, nu3, mA, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
ancmig_adj_2.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'T1', 'T2']


def ancmig_adj_1(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), with gene flow. Split
    between pops 2 and 3 with gene flow, then all gene flow ceases.
    'shortest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3 and present
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1, nuA, nu2, nu3, mA, m1, m2, T1, T2, T3 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T3, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
ancmig_adj_1.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm1', 'm2', 'T1', 'T2', 'T3']


###############################################################################
# Simultaneous split models (with/without migration/secondary contact
# and size changes)
# Written for Barratt et al. (2018)
###############################################################################

def sim_split_no_mig(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3,
    gene flow does not occur.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    T1: The scaled time between the split and the present (in units of 2*Na generations).
    """
    # 4 parameters
    nu1, nu2, nu3, T1 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_no_mig.__param_names__ = ['nu1', 'nu2', 'nu3', 'T1']


def sim_split_no_mig_size(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3,
    gene flow does not occur, but size change does.
    nu1a: Size of population 1 after split.
    nu2a: Size of population 2 after split.
    nu3a: Size of population 3 after split.
    nu1b: Size of population 1 after size change.
    nu2b: Size of population 2 after size change.
    nu3b: Size of population 3 after size change.
    T1: The scaled time between the split and the size change
    (in units of 2*Na generations).
    T2: The scaled time between the size change and present.
    """
    # 8 parameters
    nu1a, nu2a, nu3a, nu1b, nu2b, nu3b, T1, T2 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1a, nu2=nu2a, nu3=nu3a,
        m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1b, nu2=nu2b, nu3=nu3b,
        m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_no_mig_size.__param_names__ = ['nu1a', 'nu2a', 'nu3a', 'nu1b', 'nu2b', 'nu3b', 'T1', 'T2']


def sim_split_sym_mig_all(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3
    Migration is symmetrical between all population pairs (ie 1<->2, 2<->3,
    and 1<->3).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    """
    # 7 parameters
    nu1, nu2, nu3, m1, m2, m3, T1 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=m3, m31=m3)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_sym_mig_all.__param_names__ = ['nu1', 'nu2', 'nu3', 'm1', 'm2', 'm3', 'T1']


def sim_split_sym_mig_adjacent(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3
    Migration is symmetrical between 'adjacent' population pairs (ie 1<->2,
    2<->3, but not 1<->3).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    """
    # 6 parameters
    nu1, nu2, nu3, m1, m2, T1 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_sym_mig_adjacent.__param_names__ = ['nu1', 'nu2', 'nu3', 'm1', 'm2', 'T1']


def sim_split_refugia_sym_mig_all(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3 followed by isolation.
    Period of symmetric secondary contact occurs between all populations after
    all splits are complete.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    T2: The scaled time between the migration (secondary contact)
    and the present (in units of 2*Na generations).
    """
    # 8 parameters
    nu1, nu2, nu3, m1, m2, m3, T1, T2 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3,
        m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3,
        m12=m1, m21=m1, m23=m2, m32=m2, m13=m3, m31=m3)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_refugia_sym_mig_all.__param_names__ = ['nu1', 'nu2', 'nu3', 'm1', 'm2', 'm3', 'T1', 'T2']


def sim_split_refugia_sym_mig_adjacent(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3 followed by isolation.
    Period of symmetric secondary contact occurs between adjacent populations
    (ie 1<->2, 2<->3, but not 1<->3) after all splits are complete.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    T2: The scaled time between the migration (secondary contact)
    and the present (in units of 2*Na generations).
    """
    # 7 parameters
    nu1, nu2, nu3, m1, m2, T1, T2 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3,
        m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3,
        m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_refugia_sym_mig_adjacent.__param_names__ = ['nu1', 'nu2', 'nu3', 'm1', 'm2', 'T1', 'T2']


###############################################################
# Models with extra size change step (potential human impact)
# Written for Barratt et al. (2018)
###############################################################

def split_nomig_size(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration does not occur between any population pair, size change
    nu1a: Size of population 1 after split.
    nuA: Size of ancestral population (pops 2 and 3)
    nu2a: Size of population 2 after split.
    nu3a: Size of population 3 after split.
    nu1b: Size of population 1 after size change.
    nu2b: Size of population 2 after size change.
    nu3b: Size of population 3 after size change.
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
    T3: The scaled time between the size change and the present
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1a, nuA, nu2a, nu3a, nu1b, nu2b, nu3b, T1, T2, T3 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1a, nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1a, nu2a, nu3a, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T3, nu1b, nu2b, nu3b, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_nomig_size.__param_names__ = ['nu1a', 'nuA', 'nu2a', 'nu3a', 'nu1b', 'nu2b', 'nu3b', 'T1', 'T2', 'T3']


def ancmig_2_size(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), with gene flow. Split
    between pops 2 and 3, and all gene flow ceases, then size change
    shorter isolation
    nu1a: Size of population 1 after split.
    nuA: Size of ancestral population (pops 2 and 3)
    nu2a: Size of population 2 after split.
    nu3a: Size of population 3 after split.
    nu1b: Size of population 1 after size change.
    nu2b: Size of population 2 after size change.
    nu3b: Size of population 3 after size change.
    mA: Migration rate between pops 1 and (2 and 3)
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (ancient migration)(in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
    T3: The scaled time between the size change and the present
    (in units of 2*Na generations).
    """
    # 11 parameters
    nu1a, nuA, nu2a, nu3a, nu1b, nu2b, nu3b, mA, T1, T2, T3 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1a, nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1a, nu2a, nu3a, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T3, nu1b, nu2b, nu3b, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
ancmig_2_size.__param_names__ = ['nu1a', 'nuA', 'nu2a', 'nu3a', 'nu1b', 'nu2b', 'nu3b', 'mA', 'T1', 'T2', 'T3']


def sim_split_refugia_sym_mig_adjacent_size(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3 followed by isolation.
    Period of symmetric secondary contact occurs between adjacent populations
    (ie 1<->2, 2<->3, but not 1<->3) after all splits are complete,
    and a size change.
    nu1a: Size of population 1 after split.
    nu2a: Size of population 2 after split.
    nu3a: Size of population 3 after split.
    nu1b: Size of population 1 after size change.
    nu2b: Size of population 2 after size change.
    nu3b: Size of population 3 after size change.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations) (in units of 2*Na generations).
    T2: The scaled time between the split and the migration (secondary contact)
    (in units of 2*Na generations).
    T3: The scaled time between the size change and the present
    (in units of 2*Na generations).
    """
    # 11 parameters
    nu1a, nu2a, nu3a, nu1b, nu2b, nu3b, m1, m2, T1, T2, T3 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1a, nu2a, nu3a, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1a, nu2a, nu3a, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T3, nu1b, nu2b, nu3b, m12=m1, m21=m1, m23=m2, m32=m2, m13=0, m31=0)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_refugia_sym_mig_adjacent_size.__param_names__ = ['nu1a', 'nu2a', 'nu3a', 'nu1b', 'nu2b', 'nu3b', 'm1', 'm2', 'T1', 'T2', 'T3']


###############################################################
# Variation on divergence, with pop3 geographically between
# pop1 and pop2
# Written for Firneno et al. (2020)
###############################################################

# but with pop 3 treated as 'middle' population
def refugia_adj_2_var_sym(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur.
    Split between pops 2 and 3, with gene flow. After appearance of 2 and 3,
    gene flow also occurs between 1 and 3.
    'shorter isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 8 parameters
    nu1, nuA, nu2, nu3, m2, m3, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_2_var_sym.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'm2', 'm3', 'T1', 'T2']


# but with pop 3 treated as 'middle' population
def refugia_adj_2_var_uni(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur.
    Split between pops 2 and 3. Gene flow from pop1 to pop3 (unidirectional),
    and from pop2 to pop3 (unidirectional).
    'shorter isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m32: Migration rate from pop 2 to pop3 (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 8 parameters
    nu1, nuA, nu2, nu3, m32, m31, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_2_var_uni.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'm32', 'm31', 'T1', 'T2']


# but with pop 3 treated as 'middle' population
def refugia_adj_3_var_sym(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur,
    but then secondary contact occurs. Split between pops 2 and 3 occurs with
    gene flow, and gene flow happens between 1 and 3 as well.
    'shortest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1, nuA, nu2, nu3, mA, m2, m3, T1a, T1b, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1a, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = Integration.two_pops(phi, xx, T1b, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_3_var_sym.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm2', 'm3', 'T1a', 'T1b', 'T2']


# but with pop 3 treated as 'middle' population
def refugia_adj_3_var_uni(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), gene flow does not occur, bu
    then secondary contact occurs. Gene flow from pop1 to pop3 unidirectional),
    and from pop2 to pop3 (unidirectional).
    'shortest isolation'
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m32: Migration rate from pop 2 to pop3 (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the first split and the split of pops 2 and 3
    (in units of 2*Na generations).
    """
    # 10 parameters
    nu1, nuA, nu2, nu3, mA, m32, m31, T1a, T1b, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1a, nu1=nu1, nu2=nuA, m12=0, m21=0)
    phi = Integration.two_pops(phi, xx, T1b, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
refugia_adj_3_var_uni.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm32', 'm31', 'T1a', 'T1b', 'T2']


# but with pop 3 treated as 'middle' population
def split_sym_mig_adjacent_var1(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration is symmetrical between 'adjacent' population pairs (ie 1<->3,
    2<->3, but not 1<->2).
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
   """
    # 9 parameters
    nu1, nuA, nu2, nu3, mA, m2, m3, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_sym_mig_adjacent_var1.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm2', 'm3', 'T1', 'T2']

# but with pop 3 treated as 'middle' population


def split_uni_mig_adjacent_var1(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Gene flow from pop1 to pop3 (unidirectional), and from pop2 to pop3
    (unidirectional).
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m32: Migration rate from pop 2 to pop3  (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
   """
    # 9 parameters
    nu1, nuA, nu2, nu3, mA, m32, m31, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_uni_mig_adjacent_var1.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm32', 'm31', 'T1', 'T2']

# but with pop 3 treated as 'middle' population


def split_sym_mig_adjacent_var2(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration is symmetrical between pop 1 and pop(2,3),
    then between pop1 and pop3 only.
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
   """
    # 8 parameters
    nu1, nuA, nu2, nu3, mA, m3, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_sym_mig_adjacent_var2.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm3', 'T1', 'T2']


# but with pop 3 treated as 'middle' population
def split_uni_mig_adjacent_var2(params, ns, pts):
    """
    Model with split between pop 1 and (2,3), then split between 2 and 3.
    Migration is symmetrical between pop 1 and pop(2,3), then from pop1 to pop3
    (unidirectional).
    nu1: Size of population 1 after split.
    nuA: Size of population (2,3) after split from 1.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    mA: Migration rate between population 1 and population (2,3)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split of pops 1 vs 2 and 3
    (in units of 2*Na generations).
    T2: The scaled time between the split of pops 2 and 3
    (in units of 2*Na generations).
   """
    # 8 parameters
    nu1, nuA, nu2, nu3, mA, m31, T1, T2 = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nuA, m12=mA, m21=mA)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=m31)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
split_uni_mig_adjacent_var2.__param_names__ = ['nu1', 'nuA', 'nu2', 'nu3', 'mA', 'm31', 'T1', 'T2']


###############################################################
# Variation on simultaneous split models, with pop3
# geographically between pop1 and pop2
# Written for Firneno et al. (2020)
###############################################################

# but with pop 3 treated as 'middle' population
def sim_split_sym_mig_adjacent_var(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3
    Migration is symmetrical between 'adjacent' population pairs (ie 1<->3,
    2<->3, but not 1<->2).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present (in units of 2*Na generations).
    """
    # 6 parameters
    nu1, nu2, nu3, m2, m3, T1 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_sym_mig_adjacent_var.__param_names__ = ['nu1', 'nu2', 'nu3', 'm2', 'm3', 'T1']

# but with pop 3 treated as 'middle' population


def sim_split_uni_mig_adjacent_var(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3
    Gene flow from pop1 to pop3 (unidirectional), and from pop2 to pop3
    (unidirectional).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m32: Migration rate from pop 2 to pop3 (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    """
    # 6 parameters
    nu1, nu2, nu3, m32, m31, T1 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_uni_mig_adjacent_var.__param_names__ = ['nu1', 'nu2', 'nu3', 'm32', 'm31', 'T1']


# but with pop 3 treated as 'middle' population
def sim_split_refugia_sym_mig_adjacent_var(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3 followed by isolation.
    Period of symmetric secondary contact occurs between adjacent populations
    (ie 1<->3, 2<->3, but not 1<->2) after all splits are complete.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m1: Migration rate between populations 1 and 2 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    m3: Migration rate between populations 1 and 3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    T2: The scaled time between the migration (secondary contact) and the
    present (in units of 2*Na generations).
    """
    # 7 parameters
    nu1, nu2, nu3, m2, m3, T1, T2 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_refugia_sym_mig_adjacent_var.__param_names__ = ['nu1', 'nu2', 'nu3', 'm2', 'm3', 'T1', 'T2']

# but with pop 3 treated as 'middle' population


def sim_split_refugia_uni_mig_adjacent_var(params, ns, pts):
    """
    Model with simultaneous split between pop 1, 2 and 3 followed by isolation.
    After all splits are complete, gene flow from pop1 to pop3
    (unidirectional), and from pop2 to pop3 (unidirectional).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after split.
    m32: Migration rate from pop 2 to pop3 (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split and the present
    (in units of 2*Na generations).
    T2: The scaled time between the migration (secondary contact)
    and the present (in units of 2*Na generations).
    """
    # 7 parameters
    nu1, nu2, nu3, m32, m31, T1, T2 = params
    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = PhiManip.phi_2D_to_3D_split_2(xx, phi)
    phi = Integration.three_pops(
        phi, xx, T1, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)
    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
sim_split_refugia_uni_mig_adjacent_var.__param_names__ = ['nu1', 'nu2', 'nu3', 'm32', 'm31', 'T1', 'T2']


###############################################################
# Admixed ("hybrid") origin models
# Written for Firneno et al. (2020)
###############################################################

def admix_origin_no_mig(params, ns, pts):
    """
    Model with split between pop 1 and 2, gene flow does not occur.
    Population 3 is admixed from pop 1 and 2, no gene flow occurs.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after origin.
    T1: The scaled time between the split of pops 1 vs 2 and origin of 3
    (in units of 2*Na generations).
    T2: The scaled time between the origin of pop 3  and the present
    (in units of 2*Na generations).
    f: Fraction of pop 3 derived from pop 1
    (with fraction 1-f derived from pop 2).
    """
    # 6 parameters
    nu1, nu2, nu3, T1, T2, f = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nu2, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_admix(phi, f, xx, xx, xx)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=0, m13=0, m31=0)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
admix_origin_no_mig.__param_names__ = ['nu1', 'nu2', 'nu3', 'T1', 'T2', 'f']


def admix_origin_sym_mig_adj(params, ns, pts):
    """
    Model with split between pop 1 and 2, gene flow does not occur.
    Population 3 is admixed from pop 1 and 2.
    Gene flow between pop1 and pop3, and between pop2 and pop3.
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after origin.
    m3: Migration rate between populations 1 and 3 (2*Na*m)
    m2: Migration rate between populations 2 and 3
    T1: The scaled time between the split of pops 1 vs 2 and origin of 3
    (in units of 2*Na generations).
    T2: The scaled time between the origin of pop 3  and the present
    (in units of 2*Na generations).
    f: Fraction of pop 3 derived from pop 1
    (with fraction 1-f derived from pop 2).
    """
    # 8 parameters
    nu1, nu2, nu3, m2, m3, T1, T2, f = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nu2, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_admix(phi, f, xx, xx, xx)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=m2, m32=m2, m13=m3, m31=m3)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
admix_origin_sym_mig_adj.__param_names__ = ['nu1', 'nu2', 'nu3', 'm2', 'm3', 'T1', 'T2', 'f']


def admix_origin_uni_mig_adj(params, ns, pts):
    """
    Model with split between pop 1 and 2, gene flow does not occur.
    Population 3 is admixed from pop 1 and 2.
    Gene flow from pop1 to pop3 (unidirectional), and from pop2 to pop3
    (unidirectional).
    nu1: Size of population 1 after split.
    nu2: Size of population 2 after split.
    nu3: Size of population 3 after origin.
    m32: Migration rate from pop 2 to pop3 (2*Na*m)
    m31: Migration rate from pop 1 to pop3
    T1: The scaled time between the split of pops 1 vs 2 and origin of 3
    (in units of 2*Na generations).
    T2: The scaled time between the origin of pop 3  and the present
    (in units of 2*Na generations).
    f: Fraction of pop 3 derived from pop 1
    (with fraction 1-f derived from pop 2).
    """
    # 8 parameters
    nu1, nu2, nu3, m32, m31, T1, T2, f = params

    xx = Numerics.default_grid(pts)
    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)
    phi = Integration.two_pops(phi, xx, T1, nu1=nu1, nu2=nu2, m12=0, m21=0)
    phi = PhiManip.phi_2D_to_3D_admix(phi, f, xx, xx, xx)
    phi = Integration.three_pops(
        phi, xx, T2, nu1=nu1, nu2=nu2, nu3=nu3, m12=0, m21=0, m23=0, m32=m32, m13=0, m31=m31)

    fs = Spectrum.from_phi(phi, ns, (xx, xx, xx))
    return fs
admix_origin_uni_mig_adj.__param_names__ = ['nu1', 'nu2', 'nu3', 'm32', 'm31', 'T1', 'T2', 'f']
