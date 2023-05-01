# Models

## Built-in models

## User-defined models

Users can also import their own models into dadi-cli. In the `examples/data` folder, there is a file `split_mig_fix_T_models.py` which has a custom demographic model and demographic models with selection. The file imports various functions from dadi that are used to build demographic models.

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

dadi-cli checks models for the names and number of parameters, so after defining the demographic model we add an attribute for a list of the parameter names:

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
dadi-cli InferDM --model split_mig_fix_T --model-file examples/data/split_mig_fix_T_models --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --p0 2 0.5 1.2 .02 --ubounds 3 1 2 0.03 --lbounds 1 1e-1 1e-1 1e-3 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params --optimizations 20 --maxeval 300 --check-convergence

dadi-cli GenerateCache --model split_mig_fix_T_one_s --model-file examples/data/split_mig_fix_T_models --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_one_s_psudo_new_model.spectra.bpkl --cpus 4

dadi-cli GenerateCache --model split_mig_fix_T_sel --model-file examples/data/split_mig_fix_T_models --dimensionality 2 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_psudo_new_model.spectra.bpkl --cpus 4
```
