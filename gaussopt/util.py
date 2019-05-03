""" General utilities.

"""


import scipy.constants as sc


def set_d_units(units):
    """
    Read distance units.

    Parameters
    ----------
    units : str 
        distance units: 'um', 'mm', 'cm', 'dm', 'm' or 'km'

    Returns
    -------
    float
        multiplier

    """

    unit_dict = {
        'km': sc.kilo,
        'm': 1,
        'dm': sc.deci,
        'cm': sc.centi,
        'mm': sc.milli,
        'um': sc.micro,
    }

    try:
        mult = unit_dict[units.lower()]
    except:
        raise ValueError("Distance units not recognized.")

    return mult


def set_f_units(units):
    """
    Read frequency units.

    Parameters
    ----------
    units : str 
        frequency units: 'Hz', 'kHz', 'MHz', 'GHz' or 'THz' 

    Returns
    -------
    float
        multiplier

    """

    unit_dict = {
        'thz': sc.tera,
        'ghz': sc.giga,
        'mhz': sc.mega,
        'khz': sc.kilo,
        'hz': 1,
    }

    try:
        mult = unit_dict[units.lower()]
    except:
        raise ValueError("Frequency units not recognized.")

    return mult
