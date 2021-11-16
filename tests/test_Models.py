import dadi
import dadi.DFE as DFE
import pytest
from src.Models import get_dadi_model_func, get_dadi_model_params, print_available_models, print_model_details

def test_get_dadi_model_func():
    #Selection with a gamma shared between populations
    assert get_dadi_model_func('IM', withSelection=True, single_gamma=True) == DFE.DemogSelModels.IM_single_gamma
    assert get_dadi_model_func('IM_pre', withSelection=True, single_gamma=True) == DFE.DemogSelModels.IM_pre_single_gamma
    assert get_dadi_model_func('split_mig', withSelection=True, single_gamma=True) == DFE.DemogSelModels.split_mig_single_gamma
    assert get_dadi_model_func('split_asym_mig', withSelection=True, single_gamma=True) == DFE.DemogSelModels.split_asym_mig_single_gamma
    #Selection with independant gammas
    assert get_dadi_model_func('IM', withSelection=True, single_gamma=False) == DFE.DemogSelModels.IM
    assert get_dadi_model_func('IM_pre', withSelection=True, single_gamma=False) == DFE.DemogSelModels.IM_pre
    assert get_dadi_model_func('split_mig', withSelection=True, single_gamma=False) == DFE.DemogSelModels.split_mig
    assert get_dadi_model_func('split_asym_mig', withSelection=True, single_gamma=False) == DFE.DemogSelModels.split_asym_mig
    assert get_dadi_model_func('equil', withSelection=True, single_gamma=False) == DFE.DemogSelModels.equil
    assert get_dadi_model_func('two_epoch', withSelection=True, single_gamma=False) == DFE.DemogSelModels.two_epoch
    assert get_dadi_model_func('three_epoch', withSelection=True, single_gamma=False) == DFE.DemogSelModels.three_epoch
    #1D demographic models
    assert get_dadi_model_func('bottlegrowth_1d', withSelection=False, single_gamma=False) == dadi.Demographics1D.bottlegrowth
    assert get_dadi_model_func('growth', withSelection=False, single_gamma=False) == dadi.Demographics1D.growth
    assert get_dadi_model_func('snm_1d', withSelection=False, single_gamma=False) == dadi.Demographics1D.snm
    assert get_dadi_model_func('three_epoch', withSelection=False, single_gamma=False) == dadi.Demographics1D.three_epoch
    assert get_dadi_model_func('two_epoch', withSelection=False, single_gamma=False) == dadi.Demographics1D.two_epoch
    #2D demographic models
    assert get_dadi_model_func('bottlegrowth_2d', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth
    assert get_dadi_model_func('bottlegrowth_split', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth_split
    assert get_dadi_model_func('bottlegrowth_split_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.bottlegrowth_split_mig
    assert get_dadi_model_func('IM', withSelection=False, single_gamma=False) == dadi.Demographics2D.IM
    assert get_dadi_model_func('IM_pre', withSelection=False, single_gamma=False) == dadi.Demographics2D.IM_pre
    assert get_dadi_model_func('split_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.split_mig
    assert get_dadi_model_func('split_asym_mig', withSelection=False, single_gamma=False) == dadi.Demographics2D.split_asym_mig
    assert get_dadi_model_func('snm_2d', withSelection=False, single_gamma=False) == dadi.Demographics2D.snm
    #Cover error message
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=False, single_gamma=False)
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=True, single_gamma=False)
    with pytest.raises(Exception) as e_info:
        get_dadi_model_func('haha', withSelection=True, single_gamma=True)

def test_get_dadi_model_params():
    #1D demographic models
    assert get_dadi_model_params('bottlegrowth_1d') == ['nuB', 'nuF', 'T']
    assert get_dadi_model_params('growth') == ['nu', 'T']
    assert get_dadi_model_params('snm_1d') == []
    assert get_dadi_model_params('three_epoch') == ['nuB', 'nuF', 'TB', 'TF']
    assert get_dadi_model_params('two_epoch') == ['nu', 'T']
    #2D demographic models
    assert get_dadi_model_params('bottlegrowth_2d') == ['nuB', 'nuF', 'T']
    assert get_dadi_model_params('bottlegrowth_split') == ['nuB', 'nuF', 'T', 'Ts']
    assert get_dadi_model_params('bottlegrowth_split_mig') == ['nuB', 'nuF', 'm', 'T', 'Ts']
    assert get_dadi_model_params('IM') == ['s', 'nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('IM_pre') == ['nuPre', 'TPre', 's', 'nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('split_mig') == ['nu1', 'nu2', 'T', 'm']
    assert get_dadi_model_params('split_asym_mig') == ['nu1', 'nu2', 'T', 'm12', 'm21']
    assert get_dadi_model_params('snm_2d') == []
    #Cover error message
    with pytest.raises(Exception) as e_info:
        get_dadi_model_params('haha')

def test_print_available_models(capfd):
    print_available_models()
    out, err = capfd.readouterr()
    assert out == 'Available 1D demographic models:\n' + '- bottlegrowth_1d\n' + '- growth\n' + '- snm_1d\n' + '- three_epoch\n' + '- two_epoch\n\n' + 'Available 2D demographic models:\n' + '- bottlegrowth_2d\n' + '- bottlegrowth_split\n' + '- bottlegrowth_split_mig\n' + '- IM\n' + '- IM_pre\n' + '- split_mig\n' + '- split_asym_mig\n' + '- snm_2d\n\n' + 'Available demographic models with selection:\n' + '- equil\n' + '- equil_X\n' + '- IM_sel\n' + '- IM_sel_single_gamma\n' + '- IM_pre_sel\n' + '- IM_pre_sel_single_gamma\n' + '- split_mig_sel\n' + '- split_mig_sel_single_gamma\n' + '- split_asym_mig_sel\n' + '- split_asym_mig_sel_single_gamma\n' + '- two_epoch_sel\n' + '- three_epoch_sel\n'

def test_print_model_details(capfd):
    print_model_details('bottlegrowth_1d')
    out, err = capfd.readouterr()
    exp_out = '- bottlegrowth_1d:\n' + '''
        Instantanous size change followed by exponential growth.
        Only one population in this model.

        params = [nuB,nuF,T]

            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contemporary to ancient population size (in units of Na)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
    ''' + '\n'
    assert out == exp_out

    print_model_details('growth')
    out, err = capfd.readouterr()
    exp_out = '- growth:\n' + '''
        Exponential growth beginning some time ago.
        Only one population in this model.

        params = [nu,T]

            nu: Ratio of contemporary to ancient population size (in units of Na)
             T: Time in the past at which growth began (in units of 2*Na generations) 
    ''' + '\n'
    assert out == exp_out

    print_model_details('snm_1d')
    out, err = capfd.readouterr()
    exp_out = '- snm_1d:\n' + '''
        Standard neutral model.
        Only one population in this model.
    ''' + '\n'
    assert out == exp_out

    print_model_details('three_epoch')
    out, err = capfd.readouterr()
    exp_out = '- three_epoch:\n' + '''
        Two instantaneous size changes some time ago. 
        Only one population in this model.

        params = [nuB,nuF,TB,TF]

            nuB: Ratio of bottleneck population size to ancient pop size (in units of Na)
            nuF: Ratio of contemporary to ancient pop size (in units of Na)
             TB: Length of bottleneck (in units of 2*Na generations) 
             TF: Time since bottleneck recovery (in units of 2*Na generations) 
    ''' + '\n'
    assert out == exp_out

    print_model_details('two_epoch')
    out, err = capfd.readouterr()
    exp_out = '- two_epoch:\n' + '''
        One instantaneous size change some time ago.
        Only one population in this model.

        params = [nu,T]

            nu: Ratio of contemporary to ancient population size (in units of Na)
             T: Time in the past at which size change happened (in units of 2*Na generations) 
    ''' + '\n'
    assert out == exp_out

    print_model_details('bottlegrowth_2d')
    out, err = capfd.readouterr()
    exp_out = '- bottlegrowth_2d:\n' + '''
        Instantanous size change followed by exponential growth with no population
        split.
        Two populations in this model.
    
        params = [nuB,nuF,T]

            nuB: Ratio of population size after instantanous change to ancient
                 population size (in units of Na)
            nuF: Ratio of contempoary to ancient population size (in units of Na)
              T: Time in the past at which instantaneous change happened and growth began
                 (in units of 2*Na generations) 
    ''' + '\n'
    assert out == exp_out

    print_model_details('bottlegrowth_split')
    out, err = capfd.readouterr()
    exp_out = '- bottlegrowth_split:\n' + '''
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
    ''' + '\n'
    assert out == exp_out

    print_model_details('bottlegrowth_split_mig')
    out, err = capfd.readouterr()
    exp_out = '- bottlegrowth_split_mig:\n' + '''
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
    ''' + '\n'
    assert out == exp_out

    print_model_details('IM')
    out, err = capfd.readouterr()
    exp_out = '- IM:\n' + '''
        Isolation-with-migration model with exponential pop growth.
        Two populations in this model.

        params = [s,nu1,nu2,T,m12,m21]
    
              s: Size of pop 1 after split (Pop 2 has size 1-s)
            nu1: Final size of pop 1 (in units of Na)
            nu2: Final size of pop 2 (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('IM_pre')
    out, err = capfd.readouterr()
    exp_out = '- IM_pre:\n' + '''
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
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_mig')
    out, err = capfd.readouterr()
    exp_out = '- split_mig:\n' + '''
        Split into two populations of specifed size, with symmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m]
    
            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
              m: Migration rate between populations (2*Na*m)
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_asym_mig')
    out, err = capfd.readouterr()
    exp_out = '- split_asym_mig:\n' + '''
        Split into two populations of specifed size, with asymmetric migration .
        Two populations in this model.

        params = [nu1,nu2,T,m12,m21]
    
            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
              T: Time in the past of split (in units of 2*Na generations) 
            m12: Migration from pop 2 to pop 1 (2*Na*m12)
            m21: Migration from pop 1 to pop 2 (2*Na*m21)
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('snm_2d')
    out, err = capfd.readouterr()
    exp_out = '- snm_2d:\n' + '''
        Standard neutral model, populations never diverge.
        Two populations in this model.
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('equil')
    out, err = capfd.readouterr()
    exp_out = '- equil:\n' + '''
        Equilibrium demography, plus selection.
        Only one population in this model.

        params: [gamma]

            gamma: Population-scaled selection coefficient
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('equil_X')
    out, err = capfd.readouterr()
    exp_out = '- equil_X:\n' + '''
        Equilibrium demography in chromosome X, plus selection.
        Only one population in this model.

        params: [gamma]

            gamma: Population-scaled selection coefficient
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('IM_sel')
    out, err = capfd.readouterr()
    exp_out = '- IM_sel:\n' + '''
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
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('IM_sel_single_gamma')
    out, err = capfd.readouterr()
    exp_out = '- IM_sel_single_gamma:\n' + '''
        IM model with selection assumed to be equal in all populations.
        Two populations in this model.

        See IM_sel for argument definitions, but only a single gamma in params. 
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('IM_pre_sel')
    out, err = capfd.readouterr()
    exp_out = '- IM_pre_sel:\n' + '''
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
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('IM_pre_sel_single_gamma')
    out, err = capfd.readouterr()
    exp_out = '- IM_pre_sel_single_gamma:\n' + '''
        IM_pre model with selection assumed to be equal in all populations.
        Two populations in this model.

        See IM_pre_sel for argument definitions, but only a single gamma in params.
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_mig_sel')
    out, err = capfd.readouterr()
    exp_out = '- split_mig_sel:\n' + '''
        Instantaneous split into two populations of specified size, with symmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m]

               nu1: Size of population 1 after split (in units of Na)
               nu2: Size of population 2 after split (in units of Na)
                 T: Time in the past of split (in units of 2*Na generations) 
                 m: Migration rate between populations (2*Na*m)
            gamma1: Population-scaled selection coefficient in pop 1 *and* the ancestral population
            gamma2: Population-scaled selection coefficient in pop 2
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_mig_sel_single_gamma')
    out, err = capfd.readouterr()
    exp_out = '- split_mig_sel_single_gamma:\n' + '''
        split_mig model with selection assumed to be equal in all populations.
        Two populations in this model.

        See split_mig_sel for argument definitions, but only a single gamma in params.
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_asym_mig_sel')
    out, err = capfd.readouterr()
    exp_out = '- split_asym_mig_sel:\n' + '''
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
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('split_asym_mig_sel_single_gamma')
    out, err = capfd.readouterr()
    exp_out = '- split_asym_mig_sel_single_gamma:\n' + '''
        split_asym_mig model with selection assumed to be equal in all populations.
        Two populations in this model.

        See split_asym_mig_sel for argument definitions, but only a single gamma in params.
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('two_epoch_sel')
    out, err = capfd.readouterr()
    exp_out = '- two_epoch_sel:\n' + '''
        One instantaneous population size change, plus selection.
        Only one population in this model.

        params: [nu,T,gamma]

            nu: Final population size (in units of Na)
             T: Time of size changei (in units of 2*Na generations)
         gamma: Population-scaled selection coefficient
    ''' + '\n'
    assert out == exp_out
    
    print_model_details('three_epoch_sel')
    out, err = capfd.readouterr()
    exp_out = '- three_epoch_sel:\n' + '''
        Two instantaneous size changes some time ago, plus selection.
        Only one population in this model.
        
        params = [nuB,nuF,TB,TF,gamma]

            nuB: Ratio of bottleneck population size to ancient pop size (in units of Na)
            nuF: Ratio of contemporary to ancient pop size (in units of Na)
             TB: Length of bottleneck (in units of 2*Na generations) 
             TF: Time since bottleneck recovery (in units of 2*Na generations)
          gamma: Population-scaled selection coefficient
    ''' + '\n'
    assert out == exp_out
    
    with pytest.raises(Exception) as e_info:
        print_model_details('mixture')
