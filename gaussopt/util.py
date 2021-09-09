"""General utilities."""


import scipy.constants as sc


# Useful equations -----------------------------------------------------------

def get_beam_radius(z, w0, wavelength):
    """Get beam radius (w).

    Requires distance (z) and beam waist (w0).

    Note
    ----
    All parameters should be defined in the same units, including the output!
    
    Parameters
    ----------
    z : float
        distance from beam waist
    w0 : float
        beam waist
    wavelength : float
        wavelength

    Returns
    -------
    float 
        beam radius, i.e., the radial distance at which the E-field drops off 
        to 1/e of its on-axis value

    """

    return w0 * (1 + ((wavelength * z) / (sc.pi * w0 ** 2)) ** 2) ** 0.5


def get_radius_of_curvature(z, w0, wavelength):
    """Get radius of curvature (R) at a given distance (z).

    Requires distance (z) and beamwaist (w0).

    Note
    ----
    All parameters should be defined in the same units, including the output!
    
    Parameters
    ----------
    z : float
        distance from beam waist
    w0 : float
        beam waist
    wavelength : float
        wavelength

    Returns
    -------
    float 
        radius of curvature (R)

    """

    return z * (1 + ((sc.pi * w0**2) / (wavelength * z)) ** 2)


def get_confocal_distance(w0, wavelength):
    """Get confocal distance (z_c).

    Requires beam waist and wavelength.

    This value generally defines the separation between near- and far-field.

    Note
    ----
    Beam waist and wavelength should be defined in the same units!
    
    Parameters
    ----------
    w0 : float
        beam waist
    wavelength : float
        wavelength

    Returns
    -------
    float 
        confocal distance (z_c)

    """

    return sc.pi * w0 ** 2 / wavelength


def get_far_field_angle(w0, wavelength):
    """Get far-field divergence angle (theta_0).

    Requires beam waist and wavelength.

    Note
    ----
    Beam waist and wavelength should be defined in the same units!
    
    Parameters
    ----------
    w0 : float
        beam waist
    wavelength : float
        wavelength

    Returns
    -------
    float 
        far-field divergence angle (theta_0), i.e., the angle at which the 
        beam waist grows in the far-field

    """

    return wavelength / sc.pi / w0


def get_fwhm(w0, wavelength):
    """Get full width of half-maximum angle (theta_FWHM).

    Requires beam waist and wavelength.

    Note
    ----
    Beam waist and wavelength should be defined in the same units!

    Parameters
    ----------
    w0 : float
        beam waist
    wavelength : float
        wavelength

    Returns
    -------
    float 
        full width of half-maximum angle (theta_FWHM)

    """

    return 1.18 * get_far_field_angle(w0, wavelength)


# Set units ------------------------------------------------------------------

def set_d_units(units):
    """Read distance units.

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
        multiplier = unit_dict[units.lower()]
    except KeyError:
        raise ValueError("Distance units not recognized.")

    return multiplier


def set_f_units(units):
    """Read frequency units.

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
        multiplier = unit_dict[units.lower()]
    except KeyError:
        raise ValueError("Frequency units not recognized.")

    return multiplier
