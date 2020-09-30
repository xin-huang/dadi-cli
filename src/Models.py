def get_dadi_model_func(model_name, withSelection=False):

    if withSelection:
        import dadi.DFE as DFE
        if model_name == 'IM':
            return DFE.DemogSelModels.IM, False
        elif model_name == 'IM_pre':
            return DFE.DemogSelModels.IM_pre, False
        elif model_name == 'IM_pre_single_gamma':
            return DFE.DemogSelModels.IM_pre_single_gamma, True
        elif model_name == 'IM_single_gamma':
            return DFE.DemogSelModels.IM_single_gamma, True
        elif model_name == 'equil':
            return DFE.DemogSelModels.equil, True
        elif model_name == 'split_mig':
            return DFE.DemogSelModels.split_mig, False
        elif model_name == 'split_mig_single_gamma':
            return DFE.DemogSelModels.split_mig_single_gamma, True
        elif model_name == 'split_asym_mig':
            return DFE.DemogSelModels.split_asym_mig, False
        elif model_name == 'split_asym_mig_single_gamma':
            return DFE.DemogSelModels.split_asym_mig_single_gamma, True
        elif model_name == 'two_epoch':
            return DFE.DemogSelModels.two_epoch, True
        elif model_name == 'mixture':
            return DFE.mixture, True
        else:
            raise Exception('Cannot find model: ' + model_name) 
    else:
        import dadi
        if model_name == '1d_bottlegrowth':
            return dadi.Demographics1D.bottlegrowth
        elif model_name == '1d_growth':
            return dadi.Demographics1D.growth
        elif model_name == '1d_snm':
            return dadi.Demographics1D.snm
        elif model_name == '1d_three_epoch':
            return dadi.Demographics1D.three_epoch
        elif model_name == '1d_two_epoch':
            return dadi.Demographics1D.two_epoch
        elif model_name == '2d_bottlegrowth':
            return dadi.Demographics2D.bottlegrowth
        elif model_name == '2d_bottlegrowth_split':
            return dadi.Demographics2D.bottlegrowth_split
        elif model_name == '2d_bottlegrowth_split_mig':
            return dadi.Demographics2D.bottlegrowth_split_mig
        elif model_name == '2d_IM':
            return dadi.Demographics2D.IM
        elif model_name == '2d_split_asym_mig':
            return dadi.Demographics2D.split_asym_mig
        elif model_name == '2d_IM_pre':
            return dadi.Demographics2D.IM_pre
        elif model_name == '2d_split_mig':
            return dadi.Demographics2D.split_mig
        elif model_name == '2d_snm':
            return dadi.Demographics2D.snm
        else:
            raise Exception('Cannot find model ' + model_name)

def print_available_models():
    
    print('1D demographic models:')
    print('- 1d_bottlegrowth')
    print('- 1d_growth')
    print('- 1d_snm')
    print('- 1d_three_epoch')
    print('- 1d_two_epoch')
    print()

    print('2D demographic models:')
    print('- 2d_bottlegrowth')
    print('- 2d_bottlegrowth_split')
    print('- 2d_bottlegrowth_split_mig')
    print('- 2d_IM')
    print('- 2d_IM_pre')
    print('- 2d_split_mig')
    print('- 2d_split_asym_mig')
    print('- 2d_snm')
    print()

    print('Demographic models with selection:')
    print('- equil')
    print('- IM')
    print('- IM_single_gamma')
    print('- IM_pre')
    print('- IM_pre_single_gamma')
    print('- split_mig')
    print('- split_mig_single_gamma')
    print('- split_asym_mig')
    print('- split_asym_mig_single_gamma')
    print('- two_epoch')
    print('- mixture')

def print_model_details(model_name):

    equil = '''
        Equilibrium demography, plus selection.

        params: [gamma]

            gamma: Population-scaled selection coefficient
    '''
    IM = '''
        Isolation-with-migration model with exponential pop growth and selection.

        params: [s,nu1,nu2,T,m12,m21,gamma1,gamma2]

            s: Fraction of nuPre that goes to pop1. (Pop 2 has size Na*(1-s).)
            nu1: Final size of pop 1 (in units of Na)
            nu2: Final size of pop 2 (in units of Na)
            T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    IM_single_gamma = '''
        IM model with selection assumed to be equal in all populations.

        See IM for argument definitions, but only a single gamma in params. 

    '''
    IM_pre = '''
        Isolation-with-migration model with exponential pop growth, a size change
        prior to split, and selection.

        params: [nuPre,TPre,s,nu1,nu2,T,m12,m21,gamma1,gamma2]

            nuPre: Size after first size change (in units of Na)
            TPre: Time before split of first size change (in units of 2*Na generations)
            s: Fraction of nuPre that goes to pop1 (Pop 2 has size nuPre*(1-s))
            nu1: Final size of pop 1 (in units of Na)
            nu2: Final size of pop 2 (in units of Na)
            T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    IM_pre_single_gamma = '''
        IM_pre model with selection assumed to be equal in all populations.

        See IM_pre for argument definitions, but only a single gamma in params.
    '''
    split_mig = '''
        Instantaneous split into two populations of specified size, with symmetric migration.

        params = [nu1,nu2,T,m]

            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
            T: Time in the past of split (in units of 2*Na generations) 
            m: Migration rate between populations (2*Na*m)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    split_mig_single_gamma = '''
        split_mig model with selection assumed to be equal in all populations.

        See split_mig for argument definitions, but only a single gamma in params.
    '''
    split_asym_mig = '''
        Instantaneous split into two populations of specified size, with asymmetric migration.

        params = [nu1,nu2,T,m12,m21]

            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
            T: Time in the past of split (in units of 2*Na generations)
            m12: Migration rate from population 2 to population 1 (2*Na*m12)
            m21: Migration rate from population 1 to population 2 (2*Na*m21)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    split_asym_mig_single_gamma = '''
        split_asym_mig model with selection assumed to be equal in all populations.

        See split_asym_mig for argument definitions, but only a single gamma in params.
    '''
    two_epoch = '''
        Instantaneous population size change, plus selection.

        params: [nu,T,gamma]

            nu: Final population size (in units of Na)
            T: Time of size changei (in units of 2*Na generations)
    '''
    mixture = '''
    '''

    if model_name == 'equil': print('- equil:\n' + equil)
    elif model_name == 'IM': print('- IM:\n' + IM)
    elif model_name == 'IM_single_gamma': print('- IM_single_gamma:\n' + IM_single_gamma)
    elif model_name == 'IM_pre': print('- IM_pre:\n' + IM_pre)
    elif model_name == 'IM_pre_single_gamma': print('- IM_pre_single_gamma:\n' + IM_pre_single_gamma)
    elif model_name == 'split_mig': print('- split_mig:\n' + split_mig)
    elif model_name == 'split_mig_single_gamma': print('- split_mig_single_gamma:\n' + split_mig_single_gamma)
    elif model_name == 'split_asym_mig': print('- split_asym_mig:\n' + split_asym_mig)
    elif model_name == 'split_asym_mig_single_gamma': print('- split_asym_mig_single_gamma:\n' + split_asym_mig_single_gamma)
    elif model_name == 'two_epoch': print('- two_epoch:\n' + two_epoch)
