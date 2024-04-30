import argparse, os
from dadi_cli.Models import get_model
from dadi_cli.Pdfs import get_dadi_pdf_params


def positive_int(value: str) -> int:
    """
    Validates if the provided string represents a positive integer.

    Parameters
    ----------
    value : str
        The value to validate.

    Returns
    -------
    int
        The validated positive integer.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a valid integer or positive integer.

    """
    if value is not None:
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid integer")
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def nonnegative_int(value: str) -> int:
    """
    Validates if the provided string represents a nonnegative integer.

    Parameters
    ----------
    value : str
        The value to validate.

    Returns
    -------
    int
        The validated nonnegative integer.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a valid integer or nonnegative integer.

    """
    if value is not None:
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid integer")
        if ivalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is not a nonnegative integer")
    return ivalue


def positive_num(value: str) -> float:
    """
    Validates if the provided string represents a positive number.

    Parameters
    ----------
    value : str
        The value to validate.

    Returns
    -------
    float
        The validated positive number.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a valid number or positive number.

    """
    if value is not None:
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid number")
        if fvalue <= 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive number")
    return fvalue


def nonnegative_num(value: str) -> float:
    """
    Validates if the provided string represents a nonnegative number.

    Parameters
    ----------
    value : str
        The value to validate.

    Returns
    -------
    float
        The validated nonnegative number.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a valid number or nonnegative number.

    """
    if value is not None:
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid number")
        if fvalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is not a nonnegative number")
    return fvalue


def existed_file(value: str) -> str:
    """
    Validates if the provided string is a path to an existing file.

    Parameters
    ----------
    value : str
        The path to validate.

    Returns
    -------
    str
        The validated file path.

    Raises
    ------
    argparse.ArgumentTypeError
        If the file does not exist.

    """
    if value is not None:
        if not os.path.isfile(value):
            raise argparse.ArgumentTypeError(f"{value} is not found")
    return value


# helper functions for reading, parsing, and validating parameters from command line or files
def check_params(params: list[str], model: str, 
                 option: str, misid: bool) -> list[str]:
    """
    Validates the number of demographic parameters against the expected number for a given model.

    Parameters
    ----------
    params : list[str]
        A list containing the demographic parameters to be used with the model.
    model : str
        The name of the demographic model to be validated against the parameters.
    option : str
        Describes the scenario or method using these parameters (for debugging or error messages).
    misid : bool
        A flag indicating whether misidentification of alleles has been considered.
        If True, one parameter is ignored in the count.

    Returns
    -------
    list[str]
        The validated list of parameters.

    Raises
    ------
    Exception
        If the number of input parameters does not match the required number for the specified model.

    """
    input_params_len = len(params)
    _, model_params_len = get_model(model, None)
    model_params_len = len(model_params_len)
    if misid:
        input_params_len = input_params_len - 1
    if input_params_len != model_params_len:
        raise Exception(
            "\nFound "
            + str(input_params_len)
            + " demographic parameters from the option "
            + option
            + "; however, "
            + str(model_params_len)
            + " demographic parameters are required from the "
            + model
            + " model"
            + "\nYou might be using the wrong model or need to add --nomisid if you did not use ancestral allele information to polarize the fs."
        )

    return params


def check_pdf_params(params: list[str], pdf: str, 
                     option: str, misid: bool) -> list[str]:
    """
    Validates the number of PDF (Probability Density Function) parameters against the expected number for a given PDF model.

    Parameters
    ----------
    params : list[str]
        A list of parameters to be used for the PDF.
    pdf : str
        The name of the PDF to be validated against the parameters.
    option : str
        Describes the scenario or method using these parameters (for debugging or error messages).
    misid : bool
        A flag indicating whether misidentification of alleles has been considered.
        If True, one parameter is ignored in the count.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing the validated list of parameters and the list of parameter names from the PDF model.

    Raises
    ------
    Exception
        If the number of input parameters does not match the required number for the specified PDF model.

    """
    input_params_len = len(params)
    if misid:
        input_params_len = input_params_len - 1
    if pdf == "biv_lognormal" or pdf == "biv_ind_gamma":
        if input_params_len in [2, 3]:
            mod = "_sym"
        else:
            mod = "_asym"
        pdf = pdf.replace("biv", "biv" + mod)
    model_params_len = len(get_dadi_pdf_params(pdf))
    param_names = get_dadi_pdf_params(pdf)
    if input_params_len != model_params_len:
        raise Exception(
            "Found "
            + str(input_params_len)
            + " pdf parameters from the option "
            + option
            + "; however, "
            + str(model_params_len)
            + " pdf parameters are required from the "
            + pdf
            + " pdf"
        )

    return params, param_names
