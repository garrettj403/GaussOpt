""" Classes for optical components.

"""


import numpy as np
import scipy.constants as sc
import matplotlib.pyplot as plt
from copy import deepcopy as copy
from .system import transform_beam
from . import util

component_verbosity = True


# Optical component base-class ------------------------------------------------

class Component(object):
    """
    Base-class for a generic component in a Gaussian optical system.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
    
    """

    def __init__(self, matrix=None, **kwargs):
        """
        Component constructor.
        
        Parameters
        ----------
        matrix : ndarray
            beam transformation matrix, 2x2
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', 'radius' and 
            'verbose'
            
        """

        # Set beam transformation matrix
        if matrix is not None:
            self.matrix = matrix
        else:
            self.matrix = np.matrix([[1., 0.], [0., 1.]])

        # Unpack keyword arguments
        self.comment = kwargs.get('comment', '')
        self._units = kwargs.get('units', 'mm')
        self._mult = util.set_d_units(self._units)
        self.radius = kwargs.get('radius', None)
        self._verbose = kwargs.get('verbose', component_verbosity)

        if self.radius is not None:
            self.radius *= self._mult

        # Set default values
        self.distance = 0.
        self.type = 'comp'

    def __str__(self):

        return 'New Component: {0}\n{1}\n'.format(self.comment, self.matrix)

    def __repr__(self):

        return self.__str__()

    def __mul__(self, next_comp):

        new_matrix = np.dot(next_comp.matrix, self.matrix)
        new_comp = Component(new_matrix, verbose=False,
                             comment='Composite System')

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
        
    """

    def __init__(self, distance, **kwargs):
        """
        Freespace constructor.
        
        Parameters
        ----------
        distance : float
            freespace propagation distance
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', 'radius' and 
            'verbose'
            
        """

        Component.__init__(self, **kwargs)

        self.type = 'prop'
        self.distance = distance * self._mult

        self.matrix = np.matrix([[1., self.distance], [0., 1.]])

        if self._verbose:
            print((self.__str__()))

    def __str__(self):

        string = "Freespace: {0}\n\td = {1:.1f} {2}\n"
        distance_red = self.distance / self._mult
        string = string.format(self.comment, distance_red, self._units)
        
        return string


class Dielectric(Component):
    """
    Propagation through a dielectric slab.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
        
    """

    def __init__(self, thickness, n=1., **kwargs):
        """
        Dielectric constructor.
        
        Parameters
        ----------
        thickness : float
            thickness of dielectric slab
        n : float, optional
            index of refraction
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', 'radius' and 
            'verbose'
        
        """

        Component.__init__(self, **kwargs)

        self.type = 'prop'
        self.distance = thickness * self._mult
        self._n = n

        self.matrix = np.matrix([[1., self.distance * n], [0., 1.]])

        if self._verbose:
            print((self.__str__()))

    def __str__(self):

        string = "Dielectric: {0}\n\td = {1:.1f} {2}, n = {3:.1f}\n"
        d_red = self.distance / self._mult
        string = string.format(self.comment, d_red, self._units, self._n)
        
        return string


# Transformation classes ------------------------------------------------------

class Mirror(Component):
    """
    Reflection off of a parabolic mirror.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
        
    """

    def __init__(self, focal_length, **kwargs):
        """
        Mirror constructor.
        
        Parameters
        ----------
        focal_length : float
            mirror focal length
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', 'radius' and 
            'verbose'
        
        """

        Component.__init__(self, **kwargs)

        self.type = 'obj'
        self._focal_length = focal_length * self._mult

        self.matrix = np.matrix([[1., 0.], [-1. / self._focal_length, 1.]])

        if self._verbose:
            print((self.__str__()))

    def __str__(self):

        string = "Mirror: {0}\n\tf = {1:.1f} {2}\n"
        f_red = self._focal_length / self._mult
        string = string.format(self.comment, f_red, self._units)
        
        return string


class Window(Component):
    """
    A window.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    matrix : ndarray
        beam transformation matrix, 2x2
        
    """

    def __init__(self, **kwargs):
        """
        Window constructor.
        
        Parameters
        ----------
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', 'radius' and 
            'verbose'
        
        """

        Component.__init__(self, **kwargs)

        self.type = 'obj'
    
    def __str__(self):

        if self.radius is None:
            string = "Window: {0}\n"
            string = string.format(self.comment)
        else:
            arad = self.radius * 1e3
            string = "Window: {0}\n\taperture radius = {1:.1f} mm\n"
            string = string.format(self.comment, arad)

        return string


# Horn ------------------------------------------------------------------------

class Horn(object):
    """
    Waveguide horn antenna.
    
    To get initialization information, see :func:`__init__`.
    
    Attributes
    ----------
    f : ndarray/float
        frequency
    w : ndarray/float
        beam waist at aperture
    z : ndarray/float
        z-offset
    q : ndarray/complex
        beam parameter at aperture
        
    """

    def __init__(self, freq, slen, arad, hf=0.59, **kwargs):
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
        \*\*kwargs : 
            key word arguments, such as 'comment', 'units', and 'verbose'
        """

        self.type = 'horn'

        self.comment = kwargs.get('comment', '')
        self._units = kwargs.get('units', 'mm')
        self.radius = kwargs.get('radius', None)
        self._verbose = kwargs.get('verbose', component_verbosity)

        self._mult = util.set_d_units(self._units)

        slen *= self._mult
        arad *= self._mult

        self._slen = slen
        self._arad = arad
        self._hf = hf
        self.f = freq

        self.q, self.w, self.z = _horn(slen, arad, hf, freq.w)

        if self._verbose:
            print((self.__str__()))

    def __str__(self):

        slen = self._slen / self._mult
        arad = self._arad / self._mult
        units = self._units

        p1 = "\tslen = {0:5.2f} {1}\n".format(slen, units)
        p2 = "\tarad = {0:5.2f} {1}\n".format(arad, units)
        p3 = "\thf   = {0:5.2f}\n".format(self._hf)

        return 'Horn: {0}\n{1}{2}{3}'.format(self.comment, p1, p2, p3)

    def __repr__(self):

        return self.__str__()

    def z_offset(self, units='mm'):
        """
        Get distance between horn aperture and beam waist (a.k.a. z-offset).
        
        Parameters
        ----------
        units : str, optional
            units to use for returned value

        Returns
        -------
        float
            z offset

        """

        mult = util.set_d_units(units)

        return self.z / mult

    def waist(self, units='mm'):
        """
        Beam waist at aperture.
        
        Parameters
        ----------
        units : str, optional
            units to use for returned values

        Returns
        -------
        float
            waist at aperture

        """

        mult = util.set_d_units(units)

        return self.w / mult

    def copy(self, **kwargs):
        """
        Copy horn to new instance.
        
        Parameters
        ----------
        \*\*kwargs : 
            keyword arguments to pass to new instance

        Returns
        -------
        class
            new instance of the Horn class

        """

        tmp = copy(self)
        tmp.comment = kwargs.get('comment', '')
        tmp._verbose = kwargs.get('verbose', component_verbosity)
        if tmp._verbose:
            print((tmp.__str__()))

        return tmp

    def plot_properties(self):
        """
        Plots beam waist and z-offset over frequency range.

        """

        f = self.f.f / self.f._mult

        fig, ax = plt.subplots()
        ax.plot(f, self.w / self._mult, label='Waist at Aperture')
        ax.plot(f, self.z / self._mult, label='Z offset')
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f._units))
        ax.set(ylabel='Size ({0})'.format(self._units))
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

      
# Helper functions -----------------------------------------------------------

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
