# Models

## Built-in models

### Available demographic models

`dadi-cli` provides a subcommand `Model` to help users finding available demographic models in `dadi`. To find out available demographic models, users can use:

```         
dadi-cli Model --names
```

Then the available demographic models (version: 0.9.5) will be displayed in the screen:

```
Built-in 1D dadi demographic models:
- bottlegrowth_1d
- growth
- snm_1d
- three_epoch
- three_epoch_inbreeding
- two_epoch

Built-in 2D dadi and Portik et al. (2017) demographic models:
- IM
- IM_mscore
- IM_pre
- IM_pre_mscore
- anc_asym_mig
- anc_asym_mig_size
- anc_sym_mig
- anc_sym_mig_size
- asym_mig
- asym_mig_size
- asym_mig_twoepoch
- bottlegrowth_2d
- bottlegrowth_split
- bottlegrowth_split_mig
- founder_asym
- founder_nomig
- founder_nomig_admix_early
- founder_nomig_admix_late
- founder_nomig_admix_two_epoch
- founder_sym
- no_mig
- no_mig_size
- sec_contact_asym_mig
- sec_contact_asym_mig_size
- sec_contact_asym_mig_size_three_epoch
- sec_contact_asym_mig_three_epoch
- sec_contact_sym_mig
- sec_contact_sym_mig_size
- sec_contact_sym_mig_size_three_epoch
- sec_contact_sym_mig_three_epoch
- snm_2d
- split_asym_mig
- split_delay_mig
- split_mig
- split_mig_mscore
- sym_mig
- sym_mig_size
- sym_mig_twoepoch
- vic_anc_asym_mig
- vic_anc_sym_mig
- vic_no_mig
- vic_no_mig_admix_early
- vic_no_mig_admix_late
- vic_sec_contact_asym_mig
- vic_sec_contact_sym_mig
- vic_two_epoch_admix

Built-in 3D dadi and Portik et al. (2017) demographic models:
- admix_origin_no_mig
- admix_origin_sym_mig_adj
- admix_origin_uni_mig_adj
- ancmig_2_size
- ancmig_adj_1
- ancmig_adj_2
- ancmig_adj_3
- out_of_africa
- refugia_adj_1
- refugia_adj_2
- refugia_adj_2_var_sym
- refugia_adj_2_var_uni
- refugia_adj_3
- refugia_adj_3_var_sym
- refugia_adj_3_var_uni
- sim_split_no_mig
- sim_split_no_mig_size
- sim_split_refugia_sym_mig_adjacent
- sim_split_refugia_sym_mig_adjacent_size
- sim_split_refugia_sym_mig_adjacent_var
- sim_split_refugia_sym_mig_all
- sim_split_refugia_uni_mig_adjacent_var
- sim_split_sym_mig_adjacent
- sim_split_sym_mig_adjacent_var
- sim_split_sym_mig_all
- sim_split_uni_mig_adjacent_var
- split_nomig
- split_nomig_size
- split_sym_mig_adjacent_var1
- split_sym_mig_adjacent_var2
- split_symmig_adjacent
- split_symmig_all
- split_uni_mig_adjacent_var1
- split_uni_mig_adjacent_var2

Built-in demographic models with selection:
- IM_pre_sel
- IM_pre_sel_single_gamma
- IM_sel
- IM_sel_single_gamma
- bottlegrowth_1d_sel
- bottlegrowth_2d_sel
- bottlegrowth_2d_sel_single_gamma
- bottlegrowth_split_mig_sel
- bottlegrowth_split_mig_sel_single_gamma
- bottlegrowth_split_sel
- bottlegrowth_split_sel_single_gamma
- equil
- growth_sel
- split_asym_mig_sel
- split_asym_mig_sel_single_gamma
- split_delay_mig_sel
- split_delay_mig_sel_single_gamma
- split_mig_sel
- split_mig_sel_single_gamma
- three_epoch_sel
- two_epoch_sel
```

To find out the parameters and detail of a specific model, users can use the name of the demograpic model as the parameter after `--names`. For example,

```         
dadi-cli Model --names split_mig
```

Then the detail of the model will be displayed in the screen:

```         
- split_mig:

        params = (nu1,nu2,T,m)
        
        Split into two populations of specifed size, with migration.
        
        nu1: Size of population 1 after split.
        nu2: Size of population 2 after split.
        T: Time in the past of split (in units of 2*Na generations)
        m: Migration rate between populations (2*Na*m)
```

### Available DFE distributions

`dadi-cli` provides a subcommand `Pdf` to help users finding available probability density functions for DFE inference in `dadi`.

To find out available probability density functions, users can use

```         
dadi-cli Pdf --names
```

Then the availalbe functions will be displayed in the screen:

```         
Available probability density functions:
- beta
- biv_ind_gamma
- biv_lognormal
- exponential
- gamma
- lognormal
- normal
- mixture
```

To find out the parameters and the detail of a specific function, users can use the name of the function as the parameter after `--names`. For example,

```         
dadi-cli Pdf --names lognormal
```

Then the detail of the function will be displayed in the screen:

```         
- lognormal:

        Lognormal probability density function.

        params = [log_mu, log_sigma]
```

## User-defined models

Users can also import their own models into `dadi-cli`. In the `examples/data` folder, there is a file `split_mig_fix_T_models.py` which has a custom demographic model and demographic models with selection. The file imports various functions from dadi that are used to build demographic models.

```         
from dadi import Numerics, Integration, PhiManip, Spectrum
```

Then defines a demographic model:

```         
def split_mig_fix_T(params, ns, pts):
    """
    Instantaneous split into two populations of specified size, with symmetric migration and a fixed time point.
    """
    nu1,nu2,m = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, 0.3, nu1, nu2, m12=m, m21=m)

    fs = Spectrum.from_phi(phi, ns, (xx,xx))
    return fs
```

`dadi-cli` checks models for the names and number of parameters, so after defining the demographic model we add an attribute for a list of the parameter names:

```         
split_mig_fix_T.__param_names__ = ['nu1', 'nu2', 'm']
```

If you want to preform a DFE inference, you will need to add `gamma` parameters for `gamma` arguments when initializing $\phi$, ex:

```         
dadi.PhiManip.phi_1D(xx, gamma=gamma_Pop1)
```

And for integration steps, ex:

```         
dadi.Integration.two_pops(phi, xx, T, nu1, nu2, m12=m, m21=m, gamma1=gamma_Pop1, gamma2=gamma_Pop2)
```

When making demographic models with selection and setting the inital $\phi$, users should consider which population will share the selection coefficientwith the ancestral population for the gamma argument in `dadi.PhiManip.phi_1D`.

Because custom model files can have multiple models in them, users will still want to use `--model` to pass in the model for demographic inference and cache generation. Here are some quick examples for users to run:

```         
dadi-cli InferDM --model split_mig_fix_T --model-file examples/data/split_mig_fix_T_models --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --p0 2 0.5 1.2 .02 --ubounds 3 1 2 0.03 --lbounds 1 1e-1 1e-1 1e-3 --grids 60 80 100 --output ./examples/results/demog/1KG.YRI.CEU.20.split_mig_fix_T.demog.params --optimizations 20 --maxeval 300 --check-convergence 10

dadi-cli GenerateCache --model split_mig_fix_T_one_s --model-file examples/data/split_mig_fix_T_models --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig_fix_T.demog.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_one_s_psudo_new_model.spectra.bpkl --cpus 4

dadi-cli GenerateCache --model split_mig_fix_T_sel --model-file examples/data/split_mig_fix_T_models --dimensionality 2 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig_fix_T.demog.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_psudo_new_model.spectra.bpkl --cpus 4
```
