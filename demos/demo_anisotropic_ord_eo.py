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
from pyrateoptics.raytracer.globalconstants import degree

from pyrateoptics import draw, raytrace

logging.basicConfig(level=logging.DEBUG)

wavelength = 0.5876e-3

# definition of optical system
s = OpticalSystem.p()

lc0 = s.addLocalCoordinateSystem(
        LocalCoordinates.p(name="stop", decz=1.0),
        refname=s.rootcoordinatesystem.name)
lc1 = s.addLocalCoordinateSystem(
        LocalCoordinates.p(name="surf1", decz=10.0),
        refname=lc0.name)  # objectDist
lc2 = s.addLocalCoordinateSystem(
        LocalCoordinates.p(name="surf2", decz=5.0),
        refname=lc1.name)
lc3 = s.addLocalCoordinateSystem(
        LocalCoordinates.p(name="image", decz=10.0),
        refname=lc2.name)


stopsurf = Surface.p(lc0)
frontsurf = Surface.p(lc1, shape=Conic.p(lc1, curv=0),
                      aperture=CircularAperture.p(lc1, maxradius=10.0))
rearsurf = Surface.p(lc2, shape=Conic.p(lc2, curv=0),
                     aperture=CircularAperture.p(lc3, maxradius=10.0))
image = Surface.p(lc3)


elem = OpticalElement.p(lc0, name="crystalelem")

no = 1.5
neo = 1.8

myeps = np.array([[no, 0, 0], [0, no, 0], [0, 0, neo]])

crystal = AnisotropicMaterial.p(lc1, myeps)


elem.addMaterial("crystal", crystal)

elem.addSurface("stop", stopsurf, (None, None))
elem.addSurface("front", frontsurf, (None, "crystal"))
elem.addSurface("rear", rearsurf, ("crystal", None))
elem.addSurface("image", image, (None, None))

s.addElement("crystalelem", elem)

sysseq = [("crystalelem",
           [("stop", {"is_stop": True}),
            ("front", {}),
            ("rear", {}),
            ("image", {})])]


raysdict = {"opticalsystem": s, "startz": -5., "radius": 20*degree,
            "raster": raster.MeridionalFan()}
splitup = True
r2 = raytrace(s, sysseq, 10, raysdict, bundletype="divergent",
              traceoptions={"splitup": splitup}, wave=wavelength)[0]


if splitup:
    draw(s, [(r2[0], "blue"), (r2[1], "green")])
    logging.info("contains splitted? %s" % (r2[0].containsSplitted(),))
else:
    draw(s, (r2[0], "blue"))
    logging.info(r2[0].raybundles[-1].rayID)
    logging.info("contains splitted? %s" % (r2[0].containsSplitted(),))
