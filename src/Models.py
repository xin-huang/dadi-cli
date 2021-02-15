def get_dadi_model_func(model_name, withSelection=False):

    if withSelection:
        import dadi.DFE as DFE
        if model_name == 'IM_sel':
            return DFE.DemogSelModels.IM, False
        elif model_name == 'IM_pre_sel':
            return DFE.DemogSelModels.IM_pre, False
        elif model_name == 'IM_pre_sel_single_gamma':
            return DFE.DemogSelModels.IM_pre_single_gamma, True
        elif model_name == 'IM_sel_single_gamma':
            return DFE.DemogSelModels.IM_single_gamma, True
        elif model_name == 'equil':
            return DFE.DemogSelModels.equil, True
        elif model_name == 'equil_X':
            return DFE.DemogSelModels.equil_X, True
        elif model_name == 'split_mig_sel':
            return DFE.DemogSelModels.split_mig, False
        elif model_name == 'split_mig_sel_single_gamma':
            return DFE.DemogSelModels.split_mig_single_gamma, True
        elif model_name == 'split_asym_mig_sel':
            return DFE.DemogSelModels.split_asym_mig, False
        elif model_name == 'split_asym_mig_sel_single_gamma':
            return DFE.DemogSelModels.split_asym_mig_single_gamma, True
        elif model_name == 'two_epoch_sel':
            return DFE.DemogSelModels.two_epoch, True
        elif model_name == 'three_epoch_sel':
            return DFE.DemogSelModels.three_epoch, True
        elif model_name == 'mixture':
            return DFE.mixture, True
        else:
            raise Exception('Cannot find model: ' + model_name) 
    else:
        import dadi
        if model_name == 'bottlegrowth_1d':
            return dadi.Demographics1D.bottlegrowth
        elif model_name == 'growth_1d':
            return dadi.Demographics1D.growth
        elif model_name == 'snm_1d':
            return dadi.Demographics1D.snm
        elif model_name == 'three_epoch_1d':
            return dadi.Demographics1D.three_epoch
        elif model_name == 'two_epoch_1d':
            return dadi.Demographics1D.two_epoch
        elif model_name == 'bottlegrowth_2d':
            return dadi.Demographics2D.bottlegrowth
        elif model_name == 'bottlegrowth_split':
            return dadi.Demographics2D.bottlegrowth_split
        elif model_name == 'bottlegrowth_split_mig':
            return dadi.Demographics2D.bottlegrowth_split_mig
        elif model_name == 'IM':
            return dadi.Demographics2D.IM
        elif model_name == 'split_asym_mig':
            return dadi.Demographics2D.split_asym_mig
        elif model_name == 'IM_pre':
            return dadi.Demographics2D.IM_pre
        elif model_name == 'split_mig':
            return dadi.Demographics2D.split_mig
        elif model_name == 'snm_2d':
            return dadi.Demographics2D.snm
        else:
            raise Exception('Demographic model ' + model_name + ' is not available!')

def print_available_models():
    
    print('Available 1D demographic models:')
    print('- bottlegrowth_1d')
    print('- growth_1d')
    print('- snm_1d')
    print('- three_epoch_1d')
    print('- two_epoch_1d')
    print()

    print('Available 2D demographic models:')
    print('- bottlegrowth_2d')
    print('- bottlegrowth_split')
    print('- bottlegrowth_split_mig')
    print('- IM')
    print('- IM_pre')
    print('- split_mig')
    print('- split_asym_mig')
    print('- snm_2d')
    print()

    print('Available demographic models with selection:')
    print('- equil')
    print('- equil_X')
    print('- IM_sel')
    print('- IM_sel_single_gamma')
    print('- IM_pre_sel')
    print('- IM_pre_sel_single_gamma')
    print('- split_mig_sel')
    print('- split_mig_sel_single_gamma')
    print('- split_asym_mig_sel')
    print('- split_asym_mig_sel_single_gamma')
    print('- three_epoch_sel')
    print('- two_epoch_sel')
    print('- mixture')

def print_model_details(model_name):

    # 1d demographic models

    bottlegrowth_1d = '''
        Instantanous size change followed by exponential growth.
        Only one population in this model.

        params = [nuB,nuF,T]

            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contemporary to ancient population size (in units of Na)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
    '''
    growth_1d = '''
        Exponential growth beginning some time ago.
        Only one population in this model.

        params = [nu,T]

            nu: Ratio of contemporary to ancient population size (in units of Na)
             T: Time in the past at which growth began (in units of 2*Na generations) 
    '''
    snm_1d = '''
        Standard neutral model.
        Only one population in this model.
    '''
    three_epoch_1d = '''
        Two instantaneous size changes some time ago. 
        Only one population in this model.

        params = [nuB,nuF,TB,TF]

            nuB: Ratio of bottleneck population size to ancient pop size (in units of Na)
            nuF: Ratio of contemporary to ancient pop size (in units of Na)
             TB: Length of bottleneck (in units of 2*Na generations) 
             TF: Time since bottleneck recovery (in units of 2*Na generations) 
    '''
    two_epoch_1d = '''
        One instantaneous size change some time ago.
        Only one population in this model.

        params = [nu,T]

            nu: Ratio of contemporary to ancient population size (in units of Na)
             T: Time in the past at which size change happened (in units of 2*Na generations) 
    '''

    # 2d demographic models

    bottlegrowth_2d = '''
        Instantanous size change followed by exponential growth with no population
        split.
        Two populations in this model.
    
        params = [nuB,nuF,T]

            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contempoary to ancient population size (in units of Na)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
    '''
    bottlegrowth_split = '''
        Instantanous size change followed by exponential growth then split without
        migration.
        Two populations in this model.
        
        params = [nuB,nuF,T,Ts]

            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contempoary to ancient population size (in units of Na)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
             Ts: Time in the past at which the two populations split (in units of 2*Na generations)
    '''
    bottlegrowth_split_mig = '''
        Instantanous size change followed by exponential growth then split with
        symmetric migration.
        Two populations in this model.

        params = [nuB,nuF,m,T,Ts]
    
            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contempoary to ancient population size (in units of Na)
              m: Migration rate between the two populations (2*Na*m)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
             Ts: Time in the past at which the two populations split (in units of 2*Na generations)
    '''
    IM = '''
        Isolation-with-migration model with exponential pop growth.
        Two populations in this model.

        params = [s,nu1,nu2,T,m12,m21]
    
              s: Size of pop 1 after split (Pop 2 has size 1-s)
            nu1: Final size of pop 1 (in units of Na)
            nu2: Final size of pop 2 (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
    '''
    IM_pre = '''
        Isolation-with-migration model with exponential pop growth and a size change
        prior to split.
        Two populations in this model.

        params = [nuPre,TPre,s,nu1,nu2,T,m12,m21]
        
            nuPre: Size after first size change (in units of Na)
             TPre: Time before split of first size change (in units of 2*Na generations)
                s: Fraction of nuPre that goes to pop1 (Pop 2 has size nuPre*(1-s))
              nu1: Final size of pop 1 (in units of Na)
              nu2: Final size of pop 2 (in units of Na)
                T: Time in the past of split (in units of 2*Na generations) 
              m12: Migration from pop 2 to pop 1 (2*Na*m12)
              m21: Migration from pop 1 to pop 2 (2*Na*m21)
    '''
    split_mig = '''
        Split into two populations of specifed size, with symmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m]
    
            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
              m: Migration rate between populations (2*Na*m)
    '''
    split_asym_mig = '''
        Split into two populations of specifed size, with asymmetric migration .
        Two populations in this model.

        params = [nu1,nu2,T,m12,m21]
    
            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
    '''
    snm_2d = '''
        Standard neutral model, populations never diverge.
        Two populations in this model.
    '''

    # demographic models with selection
    equil = '''
        Equilibrium demography, plus selection.
        Only one population in this model.

        params: [gamma]

            gamma: Population-scaled selection coefficient
    '''
    equil_X = '''
        Equilibrium demography in chromosome X, plus selection.
        Only one population in this model.

        params: [gamma]

            gamma: Population-scaled selection coefficient
    '''
    IM_sel = '''
        Isolation-with-migration model with exponential pop growth and selection.
        Two populations in this model.

        params: [s,nu1,nu2,T,m12,m21,gamma1,gamma2]

                 s: Fraction of nuPre that goes to pop1 (Pop 2 has size Na*(1-s))
               nu1: Final size of pop 1 (in units of Na)
               nu2: Final size of pop 2 (in units of Na)
                 T: Time in the past of split (in units of 2*Na generations) 
               m12: Migration from pop 2 to pop 1 (2*Na*m12)
               m21: Migration from pop 1 to pop 2 (2*Na*m21)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    IM_sel_single_gamma = '''
        IM model with selection assumed to be equal in all populations.
        Two populations in this model.

        See IM_sel for argument definitions, but only a single gamma in params. 
    '''
    IM_pre_sel = '''
        Isolation-with-migration model with exponential pop growth, a size change
        prior to split, and selection.
        Two populations in this model.

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
    IM_pre_sel_single_gamma = '''
        IM_pre model with selection assumed to be equal in all populations.
        Two populations in this model.

        See IM_pre_sel for argument definitions, but only a single gamma in params.
    '''
    split_mig_sel = '''
        Instantaneous split into two populations of specified size, with symmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m]

               nu1: Size of population 1 after split (in units of Na)
               nu2: Size of population 2 after split (in units of Na)
                 T: Time in the past of split (in units of 2*Na generations) 
                 m: Migration rate between populations (2*Na*m)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    split_mig_sel_single_gamma = '''
        split_mig model with selection assumed to be equal in all populations.
        Two populations in this model.

        See split_mig_sel for argument definitions, but only a single gamma in params.
    '''
    split_asym_mig_sel = '''
        Instantaneous split into two populations of specified size, with asymmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m12,m21]

               nu1: Size of population 1 after split (in units of Na)
               nu2: Size of population 2 after split (in units of Na)
                 T: Time in the past of split (in units of 2*Na generations)
               m12: Migration rate from population 2 to population 1 (2*Na*m12)
               m21: Migration rate from population 1 to population 2 (2*Na*m21)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    '''
    split_asym_mig_sel_single_gamma = '''
        split_asym_mig model with selection assumed to be equal in all populations.
        Two populations in this model.

        See split_asym_mig_sel for argument definitions, but only a single gamma in params.
    '''
    two_epoch_sel = '''
        One instantaneous population size change, plus selection.
        Only one population in this model.

        params: [nu,T,gamma]

            nu: Final population size (in units of Na)
             T: Time of size changei (in units of 2*Na generations)
         gamma: Population-scaled selection coefficient
    '''
    three_epoch_sel = '''
        Two instantaneous size changes some time ago. 
        Only one population in this model.

        params = [nuB,nuF,TB,TF]

            nuB: Ratio of bottleneck population size to ancient pop size (in units of Na)
            nuF: Ratio of contemporary to ancient pop size (in units of Na)
             TB: Length of bottleneck (in units of 2*Na generations) 
             TF: Time since bottleneck recovery (in units of 2*Na generations)
          gamma: Population-scaled selection coefficient
    '''
    mixture = '''
    '''

    if model_name == 'equil': print('- equil:\n' + equil)
    elif model_name == 'equil_X': print('- equil_X:\n' + equil_X)
    elif model_name == 'IM_sel': print('- IM_sel:\n' + IM_sel)
    elif model_name == 'IM_sel_single_gamma': print('- IM_sel_single_gamma:\n' + IM_sel_single_gamma)
    elif model_name == 'IM_pre_sel': print('- IM_pre_sel:\n' + IM_pre_sel)
    elif model_name == 'IM_pre_sel_single_gamma': print('- IM_pre_sel_single_gamma:\n' + IM_pre_sel_single_gamma)
    elif model_name == 'split_mig_sel': print('- split_mig_sel:\n' + split_mig_sel)
    elif model_name == 'split_mig_sel_single_gamma': print('- split_mig_sel_single_gamma:\n' + split_mig_sel_single_gamma)
    elif model_name == 'split_asym_mig_sel': print('- split_asym_mig_sel:\n' + split_asym_mig_sel)
    elif model_name == 'split_asym_mig_sel_single_gamma': print('- split_asym_mig_sel_single_gamma:\n' + split_asym_mig_sel_single_gamma)
    elif model_name == 'two_epoch_sel': print('- two_epoch_sel:\n' + two_epoch_sel)
    elif model_name == 'three_epoch_sel': print('- three_epoch_sel:\n' + three_epoch_sel)
    elif model_name == 'bottlegrowth_1d': print('- bottlegrowth_1d:\n' + bottlegrowth_1d)
    elif model_name == 'growth_1d': print('- growth_1d:\n' + growth_1d)
    elif model_name == 'snm_1d': print('- snm_1d:\n' + snm_1d)
    elif model_name == 'three_epoch_1d': print('- three_epoch_1d:\n' + three_epoch_1d)
    elif model_name == 'two_epoch_1d': print('- two_epoch_1d:\n' + two_epoch_1d)
    elif model_name == 'bottlegrowth_2d': print('- bottlegrowth_2d:\n' + bottlegrowth_2d)
    elif model_name == 'bottlegrowth_split': print('- bottlegrowth_split:\n' + bottlegrowth_split)
    elif model_name == 'bottlegrowth_split_mig': print('- bottlegrowth_split_mig:\n' + bottlegrowth_split_mig)
    elif model_name == 'IM': print('- IM:\n' + IM)
    elif model_name == 'IM_pre': print('- IM_pre:\n' + IM_pre)
    elif model_name == 'split_mig': print('- split_mig:\n' + split_mig)
    elif model_name == 'split_asym_mig': print('- split_asym_mig:\n' + split_asym_mig)
    elif model_name == 'snm_2d': print('- snm_2d:\n' + snm_2d)
    else: raise Exception('Demographic model ' + model_name + ' is not available!') 
