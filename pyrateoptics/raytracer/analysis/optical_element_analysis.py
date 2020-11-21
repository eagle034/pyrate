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

import numpy as np

from ...core.log import BaseLogger


class OpticalElementAnalysis(BaseLogger):
    """
    Class for optical element analysis.
    """

    def __init__(self, oe, elemseq, name=""):
        super(OpticalElementAnalysis, self).__init__(name=name)
        self.opticalelement = oe
        self.elementsequence = elemseq

    def setKind(self):
        self.kind = "opticalelementanalysis"

    def calc_xyuv(self, parthitlist, pilotbundle, fullsequence,
                  background_medium):
        """
        Calculate XYUV matrices.
        """

        # FIXME: to many parameters in call
        # maybe set pilotbundle and background medium in advance

        (_, matrices) = self.opticalelement.\
            calculateXYUV(pilotbundle, fullsequence, background_medium)

        tmp = np.eye(4)

        for hit in parthitlist:
            tmp = np.dot(matrices[hit], tmp)

        return tmp
