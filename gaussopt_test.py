""" Test the GaussOpt module.

"""


import gaussopt


def test_gaussian_telescope():
    """ A Gaussian telescope is generated in this test. Ensure that perfect
    coupling is found. The focal length of all mirrors = 160mm. """

    # Frequency sweep
    freq = gaussopt.Frequency(center=250, span=100, npts=101)
    idx_center = freq.idx(250)

    # Horns
    slen = 22.64  # slant length (in mm)
    arad = 3.6  # aperture radius (in mm)
    hfac = 0.59  # horn factor
    horn_tx = gaussopt.Horn(freq, slen, arad, hfac, comment='Trasmitting')
    horn_rx = horn_tx.copy(comment='Receiving')

    # Optical components
    air = gaussopt.Freespace(160)
    mirror = gaussopt.Mirror(16, units='cm')
    z_offset = horn_tx.z_offset(units='mm')[idx_center]
    air_red = gaussopt.Freespace(160 - z_offset, comment='reduced')

    # Build system
    component_list = (air_red, mirror, air, air, mirror, air_red)
    system = gaussopt.System(horn_tx, component_list, horn_rx)

    # Test coupling
    # Should be perfect for center frequency
    coupling = system.coupling()

    # Should not be perfect for other frequencies
    # (beam waist offset changes in the horns)
    for i in range(len(freq)):
        if i == idx_center:
            assert coupling[i] == 1.
        else:
            assert coupling[i] < 1.


def test_dielectric():
    """Make sure that adding an x amount of dielectric is equivalent to
    adding x*n amount of air."""

    # Dielectric slab
    distance = 100.  # mm
    index_of_refraction = 3.
    diel = gaussopt.Dielectric(distance, index_of_refraction)

    # Freespace
    air = gaussopt.Freespace(distance)

    assert air.matrix[0, 1] * index_of_refraction == diel.matrix[0, 1]
    assert air.matrix[0, 0] == diel.matrix[0, 0]
    assert air.matrix[1, 0] == diel.matrix[1, 0]
    assert air.matrix[1, 1] == diel.matrix[1, 1]


# def test_edge_taper():
#
#     beam_waist = 30
#     aperture_rad = beam_waist * 1.2
#
#     # Check edge taper against table 2.1 in Goldsmith
#     assert round(gaussopt.edge_taper(beam_waist, aperture_rad), 1) == 12.5
#
#
# def test_gaussian_telescope_1_freq():
#     """For this test, a Gaussian telescope is created. I ensure that perfect
#     coupling is found (as expected). The system is roughly based on my own
#     system. Focal length of all mirrors = 160mm."""
#
#     frequency = 230e9
#     wavelength = gaussopt.freq_to_wavelength(frequency)
#
#     # Input horn
#     q_in, waist_in, z_offset_in = gaussopt.horn(22.64, 3.6, 0.59, wavelength)
#
#     # Distance between horn and mirror
#     # Reduced to take into account the offset between the beam waist and the
#     # horn's aperture
#     reduced_distance = 160 - z_offset_in
#
#     # Optical components
#     air_160_reduced = gaussopt.freespace(reduced_distance)
#     air_160         = gaussopt.freespace(160)
#     mirror_f160     = gaussopt.mirror(160)
#
#     # Build system
#     system = gaussopt.cascade_system(air_160_reduced,
#                                mirror_f160,
#                                air_160,
#                                air_160,
#                                mirror_f160,
#                                air_160_reduced)
#
#     # Output beam
#     q_out, waist_out, R_out = gaussopt.beam_output(system, q_in, wavelength)
#
#     # Coupling to a 'Gubbins' horn
#     coupling = gaussopt.coupling(q_out, 22.64, 3.6, 0.59, wavelength)
#
#     # Test coupling
#     # Should be perfect for center frequency
#     assert coupling == 1.
#
#     return frequency, coupling
