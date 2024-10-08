import dadi, importlib, os, sys
import dadi.DFE as DFE
from inspect import getmembers, isfunction

duplicated_models = ["snm", "bottlegrowth"]
# duplicated_sele_models = [
#     "IM",
#     "IM_pre",
#     "IM_pre_single_gamma",
#     "IM_single_gamma",
#     "split_asym_mig",
#     "split_asym_mig_single_gamma",
#     "split_mig",
#     "three_epoch",
#     "two_epoch",
#     "split_mig_single_gamma",
# ]
oned_models = [m[0] for m in getmembers(dadi.Demographics1D, isfunction)]
twod_models = [m[0] for m in getmembers(dadi.Demographics2D, isfunction)]
try:
    threed_models = [m[0] for m in getmembers(dadi.Demographics3D, isfunction)]
except AttributeError:
    threed_models = []
sele_models = [m[0] for m in getmembers(DFE.DemogSelModels, isfunction)]
# portik_models_2d = [m[0] for m in getmembers(dadi_cli.portik_models.portik_models_2d, isfunction)]
# portik_models_3d = [m[0] for m in getmembers(dadi_cli.portik_models.portik_models_3d, isfunction)]
# custom_models = [m[0] for m in getmembers(dadi_cli.custom_models, isfunction)]
for m in duplicated_models:
    oned_models.remove(m)
for m in duplicated_models:
    twod_models.remove(m)
# for m in duplicated_sele_models:
#     sele_models.remove(m)


def get_model(
    model_name: str, 
    model_file: str = None
) -> tuple[callable, list[str]]:
    """
    Obtains a demographic model and its parameters from either a predefined catalog or a specified file.

    Parameters
    ----------
    model_name : str
        Name of the demographic model.
    model_file : str, optional
        Path and name of the file containing customized models. Defaults to None, which uses predefined models.

    Returns
    -------
    tuple
        A tuple containing:
        - function: The demographic model function for modeling.
        - list[str]: List of parameter names required by the model.

    Raises
    ------
    ImportError
        If the specified model file cannot be imported.
    ValueError
        If the demographic model or its parameter names cannot be found or are undefined.

    """
    model_name0 = model_name
    if model_file is not None:
        # If the user has the model folder in their PATH
        #try:
        #    func = getattr(importlib.import_module(model_file), model_name)
        # If the user does not have the model folder in their PATH we add it
        # This currently can mess with the User's PATH while running dadi-cli
        #except:
        #    model_file = os.path.abspath(model_file)
        #    model_path = os.path.dirname(model_file)
        #    model_file = os.path.basename(model_file)
        #    model_file = os.path.splitext(model_file)[0]
        #    sys.path.append(model_path)
        #    func = getattr(importlib.import_module(model_file), model_name)
        try:
            module_name = os.path.splitext(os.path.basename(model_file))[0]
            model_path = os.path.dirname(os.path.abspath(model_file))
            sys.path.append(model_path)
            func = getattr(importlib.import_module(module_name), model_name)
        except ImportError as e:
            raise ImportError(f"Failed to import module: {model_file}") from e
    elif model_name in oned_models:
        func = getattr(dadi.Demographics1D, model_name)
    elif model_name in twod_models:
        func = getattr(dadi.Demographics2D, model_name)
    elif model_name in threed_models:
        func = getattr(dadi.Demographics3D, model_name)
    elif model_name in sele_models:
        func = getattr(DFE.DemogSelModels, model_name)
    else:
        raise ValueError(f"Cannot find model: {model_name}.")

    if not hasattr(func, '__param_names__'):
        raise ValueError(
            f"Demographic model needs a .__param_names__ attribute!\nAdd one by adding the line {model_name0}.__param_name__ = [LIST_OF_PARAMS]\nReplacing LIST_OF_PARAMS with the names of the parameters as strings."
        )

    return func, func.__param_names__


def print_built_in_models() -> None:
    """
    Prints the names of all built-in demographic models available in dadi, categorized by their dimensions
    and whether they incorporate selection.

    The output includes:
    - 1D demographic models
    - 2D demographic models including those from Portik et al. (2017)
    - 3D demographic models including those from Portik et al. (2017)
    - Models that incorporate selection

    Notes
    -----
    3D models are available only in dadi versions >= 2.3.2.

    """
    print("Built-in 1D dadi demographic models:")
    for m in oned_models:
        print(f"- {m}")
    print()

    print("Built-in 2D dadi and Portik et al. (2017) demographic models:")
    for m in twod_models:
        print(f"- {m}")
    print()

    print("Built-in 3D dadi and Portik et al. (2017) demographic models:")
    if threed_models:
        for m in threed_models:
            print(f"- {m}")
    else:
        print("- dadi version is < 2.3.2, please update for simple access to 3D models added to dadi.")
    print()

    print("Built-in demographic models with selection:")
    for m in sele_models:
        print(f"- {m}")


def print_built_in_model_details(model_name: str) -> None:
    """
    Prints detailed documentation for a specified built-in demographic model.

    Parameters
    ----------
    model_name : str
        The name of the built-in model to retrieve details for.

    Raises
    ------
    ValueError
        If the model cannot be found or the model documentation is not accessible.

    """
    try:
        func, params = get_model(model_name)
        model_doc = func.__doc__
        model_doc_new = ""
        for ele in model_doc.split("\n"):
            if "ns:" not in ele and "pts:" not in ele and "n1" not in ele:
                model_doc_new += "\t" + ele.strip() + "\n"
        model_doc_new = model_doc_new.strip()
        print(f"- {model_name}:\n\n\t{model_doc_new}\n")
    except AttributeError:
        raise ValueError(f"Documentation for the model '{model_name}' is not available.")
    except Exception as e:
        raise ValueError(f"Cannot find model: {model_name}.")
