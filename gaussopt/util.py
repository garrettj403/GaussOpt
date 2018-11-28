"""
General utilities.

"""

import scipy.constants as sc
from . import component
from . import frequency
from . import system


def set_d_units(units):
    """
    Read distance units.

    Parameters
    ----------
    units : str 
        distance units (e.g., 'mm', 'um', 'cm')

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
        raise ValueError("Units not recognized.")

    return mult


def set_f_units(units):
    """
    Read frequency units.

    Parameters
    ----------
    units : str 
        frequency units (e.g., 'THz', 'GHz', 'MHz')

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
        raise ValueError("Units not recognized.")

    return mult


def set_verbosity(verbosity):

    component.component_verbosity = verbosity
    frequency.frequency_verbosity = verbosity
    system.system_verbosity = verbosity
