#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyrate - Optical raytracing based on Python

Copyright (C) 2014-2020
               by     Moritz Esslinger moritz.esslinger@web.de
               and    Johannes Hartung j.hartung@gmx.net
               and    Uwe Lippmann  uwe.lippmann@web.de
               and    Thomas Heinze t.heinze@uni-jena.de
               and    others

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import logging

import numpy as np


from pyrateoptics.sampling2d import raster
from pyrateoptics.raytracer.material.material_anisotropic import\
    AnisotropicMaterial
from pyrateoptics.raytracer.surface_shape import Conic
from pyrateoptics.raytracer.optical_element import OpticalElement
from pyrateoptics.raytracer.surface import Surface
from pyrateoptics.raytracer.optical_system import OpticalSystem

from pyrateoptics.raytracer.aperture import CircularAperture
from pyrateoptics.raytracer.localcoordinates import LocalCoordinates

from pyrateoptics.raytracer.analysis.optical_system_analysis import\
    OpticalSystemAnalysis

from pyrateoptics import draw

logging.basicConfig(level=logging.DEBUG)


wavelength = 0.5876e-3

# definition of optical system
s = OpticalSystem.p(name='os')

lc0 = s.addLocalCoordinateSystem(LocalCoordinates.p(name="stop", decz=0.0),
                                 refname=s.rootcoordinatesystem.name)
lc1 = s.addLocalCoordinateSystem(LocalCoordinates.p(name="surf1", decz=-1.048),
                                 refname=lc0.name)  # objectDist
lc2 = s.addLocalCoordinateSystem(LocalCoordinates.p(name="surf2", decz=4.0),
                                 refname=lc1.name)
lc3 = s.addLocalCoordinateSystem(LocalCoordinates.p(name="surf3", decz=2.5),
                                 refname=lc2.name)
lc4 = s.addLocalCoordinateSystem(LocalCoordinates.p(name="image", decz=97.2),
                                 refname=lc3.name)

stopsurf = Surface.p(lc0, name="stopsurf")
frontsurf = Surface.p(lc1, name="frontsurf",
                      shape=Conic.p(lc1, curv=1./62.8, name='conic1'),
                      aperture=CircularAperture.p(lc1, maxradius=12.7))
cementsurf = Surface.p(lc2, name="cementsurf",
                       shape=Conic.p(lc2, curv=-1./45.7, name='conic2'),
                       aperture=CircularAperture.p(lc2, maxradius=12.7))
rearsurf = Surface.p(lc3, name="rearsurf",
                     shape=Conic.p(lc3, curv=-1./128.2, name='conic3'),
                     aperture=CircularAperture.p(lc3, maxradius=12.7))
image = Surface.p(lc4, name="imagesurf")

elem = OpticalElement.p(lc0, name="thorlabs_AC_254-100-A")

rnd_data1 = np.random.random((3, 3))  # np.eye(3)
rnd_data2 = np.random.random((3, 3))  # np.zeros((3, 3))#
rnd_data3 = np.random.random((3, 3))  # np.eye(3)
rnd_data4 = np.random.random((3, 3))  # np.zeros((3, 3))#

# isotropic tests

# bk7 = material.ConstantIndexGlass(lc1, n=1.5168)
# sf5 = material.ConstantIndexGlass(lc2, n=1.6727)

myeps1 = 1.5168**2*np.eye(3)
myeps2 = 1.6727**2*np.eye(3)

# anisotropic materials

# myeps1 = rnd_data1 + complex(0, 1)*rnd_data2
# myeps2 = rnd_data3 + complex(0, 1)*rnd_data4

crystal1 = AnisotropicMaterial.p(lc1, myeps1, name="crystal1")
crystal2 = AnisotropicMaterial.p(lc2, myeps2, name="crystal2")


elem.addMaterial("crystal1", crystal1)
elem.addMaterial("crystal2", crystal2)

elem.addSurface("stop", stopsurf, (None, None))
elem.addSurface("front", frontsurf, (None, "crystal1"))
elem.addSurface("cement", cementsurf, ("crystal1", "crystal2"))
elem.addSurface("rear", rearsurf, ("crystal2", None))
elem.addSurface("image", image, (None, None))

s.addElement("AC254-100", elem)

sysseq = [("AC254-100", [("stop", {}), ("front", {}), ("cement", {}),
                         ("rear", {}), ("image", {})])]

osa = OpticalSystemAnalysis(s, sysseq, name="Analysis")
osa.aim(11, {"radius": 11.43, "startz": -5., "raster": raster.MeridionalFan()},
        bundletype="collimated", wave=wavelength)
r2 = osa.trace(splitup=True)[0]
draw(s, [(r2[0], "blue"), (r2[1], "green")],
     interactive=True,
     show_box=False,
     figsize=None,
     export=None)
