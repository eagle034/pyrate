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

from ..core.base import ClassWithOptimizableVariables


class LocalCoordinatesTreeBase(ClassWithOptimizableVariables):
    """
    Optical element base class for optical system and optical element, whereas
    an optical system consists of many optical elements.
    Implements functionality for local coordinate system tree and connection
    checks.

    :param rootcoordinatesystem (LocalCoordinates object)
    :param name (string)
    :param **kwargs (key word arguments)
    """
    @classmethod
    def p(cls, rootcoordinatesystem, name=""):
        return cls({}, {"rootcoordinatesystem": rootcoordinatesystem},
                   name=name)

    def setKind(self):
        self.kind = "localcoordinatestreebase"

    def checkForRootConnection(self, lc):
        """
        Checks whether given local coordinate system is child of rootcoordinatesystem.

        :param lc (LocalCoordinates object)

        :return bool
        """
        allconnectedchildren = self.rootcoordinatesystem.returnConnectedChildren()
        return (lc in allconnectedchildren)

    def addLocalCoordinateSystem(self, lc, refname):
        """
        Adds local coordinate system as child to given reference.

        :param lc (LocalCoordinates object)
        :param refname (string)

        :return lc
        """
        self.debug(lc.pprint())
        allnames = self.rootcoordinatesystem.returnConnectedNames()
        self.debug("root coordinate system connected names: " + str(allnames))

        if lc.name in allnames:
            # choose new name if name already in allnames
            lc.name = ''

        if refname not in allnames:
            # if refname is not in allnames, set it to this root
            refname = self.rootcoordinatesystem.name

        self.debug("adding child '" + lc.name + "' to reference '" +
                   refname + "'")
        self.rootcoordinatesystem.addChildToReference(refname, lc)
        self.rootcoordinatesystem.update()

        return lc



