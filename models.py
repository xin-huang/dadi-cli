def get_dadi_model(model_name, withSelection=False):
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
            raise Exception('Cannot find model ' + model_name + ' in dadi.DFE') 
    else:
        import dadi 
