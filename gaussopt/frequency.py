""" Frequency sweep.

"""


import numpy as np
import scipy.constants as sc

import gaussopt


class Frequency(object):
    """
    Frequency sweep.
    
    Attributes
    ----------
    f : float/ndarray
        frequency array (in Hz)
    w : float/ndarray
        wavelength array (in m)
    idx_center : int
        index of center value
    
    """

    def __init__(self, start=None, stop=None, npts=301, units='GHz', **kwargs):
        """
        Build frequency sweep.
        
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
        units : str
            frequency units (e.g., 'GHz', 'MHz')
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
        self._units = units
        self._mult = gaussopt.util.set_f_units(units)

        if single is not None:
            start = single
            stop = single
            npts = 1
        elif center is not None and span is not None:
            start = center - span / 2
            stop = center + span / 2
        elif start is None and stop is None:
            start = 200
            stop = 300
        
        self.f = np.linspace(start, stop, npts) * self._mult
        self.w = sc.c / self.f
        self.idx_center = npts // 2

        if verbose:
            print(self.__str__())

    def __str__(self):

        start = self.f[0] / self._mult
        stop = self.f[-1] / self._mult
        npts = np.alen(self.f)
        if self.comment is None:
            s = "Frequency sweep:\n\tf = {0:.1f} to {1:.1f} {2}, {3} pts\n"
            s = s.format(start, stop, self._units, npts)
        else:
            s = "Frequency sweep: {0}\n\tf = {1:.1f} to {2:.1f} {3}, {4} pts\n"
            s = s.format(self.comment, start, stop, self._units, npts)

        return s

    def __repr__(self):

        return self.__str__()

    def __len__(self):
        
        return np.alen(self.f)

    def __eq__(self, other):

        return np.array_equal(self.f, other.f)

    def idx(self, freq, units='GHz'):
        """
        Get index of value closest to specified frequency.
        
        Parameters
        ----------
        freq : float
            target frequency
        units : str 
            units for the frequency

        Returns
        -------
        int
            index of value closest to given frequency

        """

        # Multiplier for distance units
        mult = gaussopt.util.set_f_units(units)

        return np.abs(freq * mult - self.f).argmin()
