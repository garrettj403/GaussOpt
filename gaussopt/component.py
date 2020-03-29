""" Optical components.

"""


from copy import deepcopy as copy

import matplotlib.pyplot as plt
import numpy as np
import scipy.constants as sc

import gaussopt
from gaussopt.system import transform_beam


# Optical component base-class ------------------------------------------------

class Component(object):
    """
    Base-class for a general optical component.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    comment : str
        comment to describe component
    radius : float
        aperture radius of component
    
    """

    def __init__(self, matrix=None, **kwargs):
        """
        Construct component.
        
        Parameters
        ----------
        matrix : ndarray
            2x2 beam transformation matrix
        
        Keyword Arguments
        -----------------
        comment : str
            comment used to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture used to analyze edge taper
        verbose : bool
            print info to terminal?
            
        """

        # Set beam transformation matrix
        if matrix is not None:
            self.matrix = matrix
        else:
            self.matrix = np.matrix([[1., 0.], [0., 1.]])

        # Private attributes
        self._units = kwargs.get('units', 'mm')
        self._mult = gaussopt.util.set_d_units(self._units)
        self._verbose = kwargs.get('verbose', True)

        # Unpack keyword arguments
        self.comment = kwargs.get('comment', '')
        self.radius = kwargs.get('radius', None)
        if self.radius is not None:
            self.radius *= self._mult

        # Set default values
        self.d = 0.  # distance
        self.type = 'comp'  # component type

    def __str__(self):

        return 'New Component: {0}\n{1}\n'.format(self.comment, self.matrix)

    def __repr__(self):

        return self.__str__()

    def __mul__(self, next_comp):
        """
        Cascade two optical components (using the multiplication symbol).
        
        Parameters
        ----------
        next_comp : Component
            next component in optical system

        Returns
        -------
        Component
            the product of cascading two components together

        """

        new_matrix = np.dot(next_comp.matrix, self.matrix)
        new_comp = Component(new_matrix, verbose=False,
                             comment='Composite System')

        return new_comp

    def copy(self, **kwargs):
        """
        Copy component to new instance.
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the copied component
        verbose : bool
            print info to terminal?

        Returns
        -------
        class
            new instance of the Component class

        """

        new_comp = copy(self)
        new_comp.comment = kwargs.get('comment', '')
        new_comp._verbose = kwargs.get('verbose', True)
        if new_comp._verbose:
            print(new_comp.__str__())

        return new_comp


# Propagation classes ---------------------------------------------------------

class Freespace(Component):
    """
    Freespace propagation.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    comment : str
        comment to describe component
    d : float
        freespace propagation distance
        
    """

    def __init__(self, distance, **kwargs):
        """
        Build freespace propagation component.
        
        Parameters
        ----------
        distance : float
            freespace propagation distance
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        verbose : bool
            print info to terminal?
            
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'prop'

        # Freespace propagation distance
        self.d = distance * self._mult

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., self.d], [0., 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Freespace: {0}\n\td = {1:.1f} {2}\n"
        d_print = self.d / self._mult
        msg = msg.format(self.comment, d_print, self._units)
        
        return msg


class Dielectric(Component):
    """
    Propagation through a dielectric material.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    comment : str
        comment to describe component
    d : float
        thickness of dielectric slab
    n : float, optional
        index of refraction
            
    """

    def __init__(self, thickness, n, **kwargs):
        """
        Build dielectric propagation component.
        
        Parameters
        ----------
        thickness : float
            thickness of dielectric slab
        n : float
            index of refraction
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'prop'

        # Thickness of dielectric slab
        self.d = thickness * self._mult

        # Index of refraction
        self.n = n

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., self.d * n], [0., 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Dielectric: {0}\n\td = {1:.1f} {2}, n = {3:.1f}\n"
        d_print = self.d / self._mult
        msg = msg.format(self.comment, d_print, self._units, self.n)
        
        return msg


# Transformation classes ------------------------------------------------------

class Mirror(Component):
    """
    Reflection off of a parabolic mirror.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    f : float
        focal length of mirror, in units [m]
    comment : str
        comment to describe mirror
        
    """

    def __init__(self, focal_length, **kwargs):
        """
        Build parabolic mirror component.
        
        Parameters
        ----------
        focal_length : float
            mirror focal length
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture (used to analyze edge taper)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'obj'
        
        # Focal length of mirror
        self.f = focal_length * self._mult

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., 0.], [-1. / self.f, 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Mirror: {0}\n\tf = {1:.1f} {2}\n"
        f_red = self.f / self._mult
        msg = msg.format(self.comment, f_red, self._units)
        
        return msg


class ThinLens(Component):
    """
    Transmission through a thin lens.

    "Thin" meaning that the transmission through the dielectric material is 
    not included in the model. 
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    f : float
        focal length of the thin lens, in units [m]
    comment : str
        comment to describe the thin lens
        
    """

    def __init__(self, focal_length, **kwargs):
        """
        Build thin lens component.
        
        Parameters
        ----------
        focal_length : float
            thin lens focal length
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture (used to analyze edge taper)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'obj'
        
        # Focal length of thin len
        self.f = focal_length * self._mult

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., 0.], [-1. / self.f, 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Thin lens: {0}\n\tf = {1:.1f} {2}\n"
        f_red = self.f / self._mult
        msg = msg.format(self.comment, f_red, self._units)
        
        return msg


class SphericalMirror(Component):
    """
    Reflection off of a spherical mirror
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    f : float
        focal length of the mirror, in units [m]
    R : floag
        radius of curvature of the mirror, in units [m]
    comment : str
        comment to describe the mirror
    radius_curv : float
        radius of curvature, in units [m]
        
    """

    def __init__(self, radius_curv, **kwargs):
        """
        Build spherical mirror component.
        
        Parameters
        ----------
        radius_curv : float
            radius of curvature, in units [m]
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture (used to analyze edge taper)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'obj'
        
        # Focal length of thin len
        self.f = radius_curv * self._mult / 2
        self.radius_curv = radius_curv

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., 0.], [-1. / self.f, 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Spherical mirror: {0}\n\tf = {1:.1f} {2}\n"
        f_red = self.f / self._mult
        msg = msg.format(self.comment, f_red, self._units)
        
        return msg


class EllipsoidalMirror(Component):
    """
    Reflection off of an ellipsoidal mirror
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    f : float
        focal length of the mirror, in units [m]
    d1 : float
        dimension d1
    d2 : float
        dimension d2
    comment : str
        comment to describe the mirror
        
    """

    def __init__(self, d1, d2, **kwargs):
        """
        Build ellipsoidal mirror component.
        
        Parameters
        ----------
        d1 : float
            dimension d1
        d2 : float
            dimension d2
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture (used to analyze edge taper)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        # Private attributes
        self.type = 'obj'
        
        # Focal length of thin len
        self.f = d1 * d2 / (d1 + d2)
        self.d1 = d1
        self.d2 = d2

        # Build beam transformation matrix
        self.matrix = np.matrix([[1., 0.], [-1. / self.f, 1.]])

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        msg = "Ellipsoidal mirror: {0}\n\tf = {1:.1f} {2}\n"
        f_red = self.f / self._mult
        msg = msg.format(self.comment, f_red, self._units)
        
        return msg


class Window(Component):
    """
    Window and/or aperture.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    comment : str
        comment to describe component
    radius : float
        aperture radius of window
        
    """

    def __init__(self, **kwargs):
        """
        Window constructor.
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        radius : float
            radius of aperture (used to analyze edge taper)
        verbose : bool
            print info to terminal?
        
        """

        # Initialize component
        Component.__init__(self, **kwargs)

        self.type = 'obj'
    
    def __str__(self):

        if self.radius is None:
            msg = "Window: {0}\n"
            msg = msg.format(self.comment)
        else:
            msg = "Window: {0}\n\taperture radius = {1:.1f} mm\n"
            msg = msg.format(self.comment, self.radius * 1e3)

        return msg


# Horn ------------------------------------------------------------------------

class Horn(object):
    """
    Waveguide horn antenna.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    comment : str
        comment to describe component
    freq : ndarray/float
        frequency sweep
    w : ndarray/float
        beam waist at aperture of horn
    z : ndarray/float
        z-offset of horn
    q : ndarray/complex
        beam parameter at aperture of horn
    slen : float
        slant length of horn
    arad : float
        aperture radius of horn
    hf : float, optional
        horn factor
        
    """

    def __init__(self, freq, slen, arad, hf, **kwargs):
        """
        Horn constructor.
        
        Parameters
        ----------
        freq : class 'gaussopt.frequency.Frequency'
            frequency class
        slen : float
            slant length
        arad : float
            aperture radius
        hf : float, optional
            horn factor
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the component
        units : str
            units for length (default is mm)
        verbose : bool
            print info to terminal?

        """

        # Private attributes
        self.type = 'horn'
        self._units = kwargs.get('units', 'mm')
        self._verbose = kwargs.get('verbose', True)
        self._mult = gaussopt.util.set_d_units(self._units)

        # Unpack keyword arguments
        self.comment = kwargs.get('comment', '')

        # Horn properties
        self.slen = slen * self._mult  # slant length
        self.arad = arad * self._mult  # aperture radius
        self.hf = hf  # horn factor

        # Frequency sweep
        self.freq = freq

        # Calculate horn parameters
        self.q, self.w, self.z = _horn(self.slen, self.arad, self.hf, freq.w)

        if self._verbose:
            print(self.__str__())

    def __str__(self):

        slen = self.slen / self._mult
        arad = self.arad / self._mult
        units = self._units

        p1 = "\tslen = {0:5.2f} {1}\n".format(slen, units)
        p2 = "\tarad = {0:5.2f} {1}\n".format(arad, units)
        p3 = "\thf   = {0:5.2f}\n".format(self.hf)

        return 'Horn: {0}\n{1}{2}{3}'.format(self.comment, p1, p2, p3)

    def __repr__(self):

        return self.__str__()

    def z_offset(self, units='mm'):
        """
        Calculate distance between horn aperture and beam waist (i.e., the 
        z-offset).
        
        Keyword Arguments
        -----------------
        units : str
            units to use for offset value

        Returns
        -------
        float
            z offset

        """

        # Multiplier for distance units
        mult = gaussopt.util.set_d_units(units)

        return self.z / mult

    def waist(self, units='mm'):
        """
        Calculate beam waist at aperture.
        
        Keyword Arguments
        -----------------
        units : str
            units to use for returned values

        Returns
        -------
        float
            waist at aperture

        """

        # Multiplier for distance units
        mult = gaussopt.util.set_d_units(units)

        return self.w / mult

    def copy(self, **kwargs):
        """
        Copy horn to new instance.
        
        Keyword Arguments
        -----------------
        comment : str
            comment to describe the copied component
        verbose : bool
            print info to terminal?

        Returns
        -------
        class
            new instance of the Horn class

        """

        new_comp = copy(self)
        new_comp.comment = kwargs.get('comment', '')
        new_comp._verbose = kwargs.get('verbose', True)
        if new_comp._verbose:
            print(new_comp.__str__())

        return new_comp

    def plot_properties(self):
        """
        Plot beam waist and z-offset over frequency range.

        """

        freq = self.freq.f

        fig, ax = plt.subplots()
        ax.plot(freq / 1e9, self.w * 1e3, label='Waist at Aperture')
        ax.plot(freq / 1e9, self.z * 1e3, label='Z offset')
        ax.set(xlim=[freq.min() / 1e9, freq.max() / 1e9])
        ax.set(xlabel='Frequency (GHz)')
        ax.set(ylabel='Size (mm)')
        plt.legend()
        plt.show()


def _horn(slen, arad, hf, wlen):
    """
    Calculate the beam parameters for a given horn.
    
    Parameters
    ----------
    slen : float
        slant length
    arad : float
        aperture radius
    hf : float
        horn factor
    wlen : float/ndarray
        wavelength array

    Returns
    -------
    tuple
        beam parameter, beam waist and z-offset

    """

    # wlen can either be an array or a float
    if type(wlen) != np.ndarray:

        # Eqn 7.38a and 7.38b (note there is an error in the textbook)
        w = hf * arad / np.sqrt(1 + (np.pi * (hf * arad) ** 2 /
                                (wlen * slen)) ** 2)
        zoff = slen / (1 + (wlen * slen / (np.pi * (hf * arad) ** 2)) ** 2)
        q_waist = _q_from_waist(w, wlen)

        waist_to_ap = Freespace(zoff, units='m', verbose=False).matrix
        qap = transform_beam(waist_to_ap, q_waist)

        return qap, w, zoff

    # A crappy hack, but this isn't a computer intensive package
    elif type(wlen) == np.ndarray:

        npts = np.alen(wlen)
        qap_arr = np.zeros_like(wlen, dtype=complex)
        w_arr = np.zeros_like(wlen)
        zoff_arr = np.zeros_like(wlen)

        for i in range(npts):

            qap_arr[i], w_arr[i], zoff_arr[i] = _horn(slen, arad, hf, wlen[i])

        return qap_arr, w_arr, zoff_arr


def _q_from_waist(waist, wlen):
    """
    Get the beam parameter (q) from the waist.
    
    Notes
    -----
    This is only valid for the case R=inf (i.e., at the beam waist).
    
    Parameters
    ----------
    waist : float
        beam waist
    wlen : float/ndarray
        wavelength array

    Returns
    -------
    ndarray
        beam parameter (q)

    """

    return 1j * sc.pi * waist ** 2 / wlen
