"""
Build optical system and analyze.

"""


import numpy as np 
from . import util 
import matplotlib.pyplot as plt

system_verbosity = True


class System(object):
    """
    Entire optical system.
    
    Attributes
    ----------
    matrix : ndarray
        cascaded beam transformation matrix
    f : ndarray/float
        frequency
    wout : ndarray/float
        output beam waist
    qout : ndarray/complex
        output beam parameter
    rout : ndarray/float
        output beam radius
    
    """

    def __init__(self, horn_tx, component_list, horn_rx=None, **kwargs):
        """
        System constructor.
        
        Parameters
        ----------
        horn_tx : class
            transmitting horn
        component_list : tuple/list
            list of optical components
        horn_rx : class
            receiving horn
        \*\*kwargs : 
            keyword arguments (comment, verbose)
        
        """

        if horn_rx is None:
            horn_rx = horn_tx.copy(comment='copy', verbose=False)

        assert horn_rx.f == horn_tx.f, "Horn frequencies must match."
        self.f = horn_rx.f

        self.comment = kwargs.get('comment', '')
        self._verbose = kwargs.get('verbose', system_verbosity)

        self._horn_tx = horn_tx
        self._horn_rx = horn_rx
        self._comp_list = component_list

        self._system = component_list[0]
        for comp in component_list[1:]:
            self._system *= comp 
        self.matrix = self._system.matrix

        self.qout = transform_beam(self.matrix, self._horn_tx.q)
        self.wout = _waist_from_q(self._horn_tx.q, self.f.w)
        self.rout = _radius_from_q(self._horn_tx.q)

        if self._verbose:
            print((self.__str__()))

    def __str__(self):

        return "System: {0}\n{1}".format(self.comment, self.matrix)

    def coupling(self):
        """
        Get coupling between the horns.
        
        Returns
        -------
        ndarray 
            coupling between the antennas
            
        """

        return _coupling(self.qout, self._horn_rx, self.f.w)

    def best_coupling_frequency(self):
        """
        Get best coupling frequency.
        
        Returns
        -------
        float
            frequency where best coupling is found
        
        """

        idx_best = self.coupling().argmax()

        return self.f.f[idx_best]

    def best_coupling(self):
        """
        Get best coupling.
        
        Returns
        -------
        float
            best coupling 
            
        """

        return self.coupling().max()

    def print_best_coupling(self, units='GHz'):
        """
        Print best coupling and frequency where it is found.
        
        Parameters
        ----------
        units : str, optional
            units for frequency

        """

        mult = util.set_f_units(units)
        best = self.best_coupling() * 100.
        f_best = self.best_coupling_frequency() / mult

        s = "Best coupling: {0:.1f} % at {1:.1f} {2}"
        print((s.format(best, f_best, units)))

    def plot_coupling(self, ax=None):
        """
        Plot coupling (in percentage) versus frequency.
        
        """

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(f, self.coupling() * 100.)
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Coupling (\%)')
        plt.autoscale(enable=True, axis='y', tight=True)
        plt.grid(True)
        plt.minorticks_on()
        if ax is None:
            plt.show()

    def plot_coupling_mag(self, ax=None):
        """
        Plot coupling versus frequency. 

        """

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(f, self.coupling())
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Coupling (1)')
        if ax is None:
            plt.show()

    def plot_coupling_db(self, ax=None):
        """
        Plot coupling (in dB) versus frequency.

        """

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(f, 10*np.log10(self.coupling()))
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Coupling (dB)')
        if ax is None:
            plt.show()

    def plot_edge_taper_db(self, ax=None):

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        sys = self._comp_list[0]
        for comp in self._comp_list[1:]:
            sys *= comp
            if comp.type == 'obj':
                q = transform_beam(sys.matrix, self._horn_tx.q)
                w = _waist_from_q(q, self.f.w)
                et = _edge_taper(w, comp.radius, output='dB')
                ax.plot(f, et, label=comp.comment)
        ax.legend()
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Edge Taper (dB)')
        plt.tight_layout()
        if ax is None:
            plt.show()

    def plot_waists(self, ax=None):

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        sys = self._comp_list[0]
        for comp in self._comp_list[1:]:
            sys *= comp
            if comp.type == 'obj':
                q = transform_beam(sys.matrix, self._horn_tx.q)
                w = _waist_from_q(q, self.f.w) * 1e3
                ax.plot(f, w, label=comp.comment)
        ax.legend()
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Beam Waist (mm)')
        if ax is None:
            plt.show()

    def plot_aperture_30db(self, ax=None):

        f = self.f.f / self.f.mult

        if ax is None:
            fig, ax = plt.subplots()
        sys = self._comp_list[0]
        for comp in self._comp_list[1:]:
            sys *= comp
            if comp.type == 'obj':
                q = transform_beam(sys.matrix, self._horn_tx.q)
                w = _waist_from_q(q, self.f.w) * 1e3
                ax.plot(f, w*np.sqrt(30/8.686), label=comp.comment)
        ax.legend()
        ax.set(xlim=[f.min(), f.max()])
        ax.set(xlabel='Frequency ({0})'.format(self.f.units))
        ax.set(ylabel='Required Aperture Radius (mm)')
        plt.tight_layout()
        if ax is None:
            plt.show()

    def plot_system(self, freq=None, ax=None, figname=None):

        # Frequency to plot waists for
        if freq is None:
            idx = self.f.idx_center
        else:
            idx = self.f.idx(freq)

        qin = self._horn_tx.q
        wlen = self.f.w

        if ax is None:
            fig, ax = plt.subplots()

        # Plot waist as a function of distance
        d_last_comp = 0.
        distance = []
        waist = []
        sys = np.matrix([[1., 0], [0., 1.]])
        for comp in self._comp_list:
            if comp.type == 'prop':
                d_tmp = np.arange(comp.distance, step=1e-3)
                for d in d_tmp:
                    m_tmp = _freespace_matrix(d)
                    s_tmp = np.dot(m_tmp, sys)
                    q = transform_beam(s_tmp, qin)
                    w = _waist_from_q(q, wlen)
                    waist.append(w[idx])
                    distance.append(d + d_last_comp)
            d_last_comp += comp.distance
            sys = np.dot(comp.matrix, sys)
        distance = np.array(distance)
        waist = np.array(waist)
        ax.plot(distance*1e3, waist*1e3, label='Beam waist')
        ax.plot(distance*1e3, waist*np.sqrt(30/8.686)*1e3, 'r--',
                label='Aperture radius required\n'+ r'for $<$30 dB edge taper')

        # Add component radii and positions
        distance = self._comp_list[0].distance
        sys = self._comp_list[0]
        for comp in self._comp_list[1:]:
            sys *= comp
            distance += comp.distance
            if comp.type == 'obj':
                q = transform_beam(sys.matrix, self._horn_tx.q)
                w = _waist_from_q(q, self.f.w)

                ax.axvline(distance * 1e3, ls=':', lw=0.5, c='k')

                ax.plot(distance * 1e3, comp.radius * 1e3, 'kx', lw=1, markersize=3)
                label = "A.R.".format(comp.comment)
                ax.text(distance * 1e3, comp.radius * 1e3 + 4, label,
                        rotation=90, ha='center', va='bottom',
                        multialignment='left',
                        bbox=dict(boxstyle='round', facecolor='wheat',
                                  alpha=1),
                        fontsize=8)

                label = "{0}".format(comp.comment)
                ax.text(distance * 1e3, w[idx] * 1e3 + 10, label,
                        rotation=90, ha='center', va='bottom',
                        multialignment='left',
                        bbox=dict(boxstyle='round', facecolor='wheat',
                                  alpha=1),
                        fontsize=8)

        ax.set(ylim=[0, 100], ylabel='Size (mm)')
        plt.autoscale(enable=True, axis='x', tight=True)
        ax.set(xlabel='Distance from Horn Aperture (mm)')
        ax.minorticks_on()

        leg = ax.legend(loc=8, fontsize=8)
        leg.get_frame().set_alpha(1.)

        if figname is not None:
            plt.savefig(figname, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()


def transform_beam(sys_matrix, q_in):
    """
    Transform a beam using the beam transformation matrix.
    
    Parameters
    ----------
    sys_matrix : ndarray
        beam transformation matrix
    q_in : complex/ndarray
        input beam parameter (q)

    Returns
    -------
    complex/ndarray
        output beam parameter (q)

    """

    q_out = (sys_matrix[0, 0] * q_in + sys_matrix[0, 1]) / \
            (sys_matrix[1, 0] * q_in + sys_matrix[1, 1])

    return q_out


# Helper functions -----------------------------------------------------------

def _waist_from_q(q, wavelength):

    return np.sqrt(wavelength / (np.pi * np.imag(-1 / q)))


def _radius_from_q(q):

    return 1 / (np.real(1 / q))


def _freespace_matrix(distance):

    return np.matrix([[1., distance], [0., 1.]])


def _coupling(qin, horn_rx, wavelength):
    """Determine the coupling to a horn.

    Given the systems output beam parameter q, this function will determine
    the coupling to a given horn.

    Args:
        qin (complex): Input beam parameter
        horn_rx: Receiving horn
        wavelength (ndarray/float): Wavelength

    Returns:
        ndarray/float: Coupling (some value 0-1)

    """

    whorn = horn_rx.w
    zoff = horn_rx.z

    if isinstance(wavelength, np.ndarray):
        qout = np.zeros(np.alen(wavelength), dtype=complex)
        for i in range(np.alen(wavelength)):
            qout[i] = transform_beam(_freespace_matrix(zoff[i]), qin[i])
    else:
        qout = transform_beam(_freespace_matrix(zoff), qin)

    w = np.sqrt(wavelength / (np.pi * np.imag(-1 / qout)))

    r = 1 / (np.real(1 / qout))

    coupling = 4 / ((((w / whorn) + (whorn / w))**2 +
                     ((np.pi * whorn * w / wavelength)**2) *
                     (((1 / r) - (1 / 1e50))**2)))

    return coupling


def _edge_taper(beam_waist, aperture_radius, output='dB'):
    """Determine the edge taper due to some aperture.

    Args:
        beam_waist (ndarray): beam waist
        aperture_radius (float): aperture radius
        output (string): Return edge taper in 'dB' or 'linear' units

    Returns:
        ndarray: edge taper

    """

    taper = np.exp(-2 * aperture_radius ** 2 / beam_waist ** 2)

    if output == 'linear':
        return taper

    elif output == 'dB':
        return -10 * np.log10(taper)
