GaussOpt
========

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/garrettj403/GaussOpt/issues)

*Analyze quasioptical systems using Gaussian beam analysis*

This package assumes Gaussian beam propagation to analyze quasioptical systems. Quasioptical analysis is important whenever the size of the optical components is comparable to the wavelength. Gaussian beam analysis of quasioptical systems then assumes that the transverse amplitude profile of the beam is close to a Gaussian function, which is approximately true for beams originating from waveguide horn antennas.

**Webpage:** https://garrettj403.github.io/GaussOpt/

Description
-----------

At millimeter and submillimeter wavelengths, traditional transmission lines (e.g., microstrips and waveguides) have very high attenuation constants. To avoid this loss, an alternative is to use freespace propagation. However, since the dimensions of the optical components are often only a few times the wavelength, the beams cannot be effectively collimated and then a series of lenses or parabolic mirrors are required to continually refocus the beam. This type of system is often called a quasioptical system ("quasi" because standard geometric optics do not apply).

Beams in quasioptical systems typically originate/terminate in waveguide feed horns. The transverse amplitude profile of these beams is very close to a Gaussian distribution, which can be used to simplify the description of the beam as it propagates through a quasioptical system. In short, Gaussian beam analysis is a simplified formulation of physical optics; however, it is sufficient for most applications and at least provides a starting point for more rigorous analysis.

The GaussOpt package allows the user to define feed horns and various optical components, build a quasioptical system, and then simulate the beam as it propagates through the system. This can be used to calculate coupling factors, beam waists, edge tapers, etc.

Installation
------------

GaussOpt can be installed via [``pip``](https://pypi.python.org/pypi/GaussOpt):

```bash
pip install GaussOpt
```

Examples
--------

An example of a quasioptical system is provided in the [``gaussopt_example.ipynb`` notebook.](https://github.com/garrettj403/GaussOpt/blob/master/gaussopt_example.ipynb)

Licence
-------

GaussOpt is released under an [MIT open-source licence](https://github.com/garrettj403/GaussOpt/blob/master/LICENSE).

References
----------

P. F. Goldsmith, *Quasioptical Systems*. New York, NY: IEEE, 1998.

P. F. Goldsmith, “Quasi-optical techniques,” *Proc. IEEE*, vol. 80, no. 11, pp. 1729–1747, 1992.
