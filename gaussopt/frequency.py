""" Frequency sweep.

"""


import numpy as np
import scipy.constants as sc

import gaussopt


class Frequency(object):
    """ Frequency sweep.
    
    Attributes
    ----------
    f : float/ndarray
        frequency, in units [Hz]
    w : float/ndarray
        wavelength, in units [m]
    idx_center : int
        index of center value
    
    """

    def __init__(self, start=None, stop=None, npts=None, freq=None, units='GHz', **kwargs):
        """ Build frequency sweep.
        
        Keyword Arguments
        -----------------
        start : float
            start frequency
        stop : float
            stop frequency
        center : float
            center frequency
        span : float
            span of frequency sweep
        npts : int
            number of points
        freq : float
            frequeny array
        units : str
            frequency units (e.g., 'GHz', 'MHz')
        single : float
            single frequency value
        verbose : bool
            print info to terminal?
        comment : str
            comment to describe frequency sweep
        
        """

        center = kwargs.pop('center', None)
        span = kwargs.pop('span', None)
        single = kwargs.pop('single', None)
        verbose = kwargs.pop('verbose', True)

        self.comment = kwargs.pop('comment', None)
        self.units = units
        self.unit_mult = gaussopt.util.set_f_units(units)

        if single is not None:
            start = single
            stop = single
            npts = 1
        elif center is not None and span is not None:
            start = center - span / 2
            stop = center + span / 2
        
        self._f = None

        if start is not None and stop is not None and npts is not None:
            self.f = np.linspace(start, stop, npts) * self.unit_mult
        elif freq is not None:
            self.f = np.array(freq) * self.unit_mult
        else:
            print("Must specify start+stop+npts, center+span+npts or single")
            raise ValueError

        if verbose:
            print(self.__str__())

    def __str__(self):

        start = self.f[0] / self.unit_mult
        stop = self.f[-1] / self.unit_mult
        npts = len(self.f)
        if self.comment is None:
            s = "Frequency sweep:\n\tf = {0:.1f} to {1:.1f} {2}, {3} pts\n"
            s = s.format(start, stop, self.units, npts)
        else:
            s = "Frequency sweep: {0}\n\tf = {1:.1f} to {2:.1f} {3}, {4} pts\n"
            s = s.format(self.comment, start, stop, self.units, npts)

        return s

    def __repr__(self):

        return self.__str__()

    def __len__(self):
        
        return len(self.f)

    def __eq__(self, other):

        return np.array_equal(self.f, other.f)

    @property
    def f(self):
        """Get frequency in Hz."""
        return self._f

    @f.setter
    def f(self, value):
        """Set frequency and wavelength."""
        self._f = value
        if value is not None:
            self.w = sc.c / value
            self.idx_center = len(value) // 2
        else:
            self.w = None
            self.idx_center = None
    
    def idx(self, freq, units='GHz'):
        """
        Get index of value closest to specified frequency.
        
        Parameters
        ----------
        freq : float
            target frequency
        units : str 
            units for frequency

        Returns
        -------
        int
            index of value closest to given frequency

        """

        # Multiplier for distance units
        mult = gaussopt.util.set_f_units(units)

        return np.abs(freq * mult - self.f).argmin()
