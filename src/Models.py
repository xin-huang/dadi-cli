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
        elif model_name == 'two_epoch':
            return DFE.DemogSelModels.two_epoch, True
        else:
            raise Exception('Cannot find model ' + model_name) 
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
        elif model_name == '2d_IM_fsc':
            return dadi.Demographics2D.IM_fsc
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
    print('- 2d_IM_fsc')
    print('- 2d_IM_pre')
    print('- 2d_split_mig')
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
    print('- two_epoch')
