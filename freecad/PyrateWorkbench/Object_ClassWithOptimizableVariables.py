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

from pyrateoptics.core.base_ui import UIInterfaceClassWithOptimizableVariables

from FreeCAD import newDocument


class ClassWithOptimizableVariablesObject:
    """
    FreeCAD interface object for class with optimizable variables.
    First of all, it should be very general. Save and Load mechanisms
    should be treated via the dump and read mechanism of yaml or json.
    (TODO: how to solve the interaction with a FreeCAD document?)
    """

    def __init__(self, myclasswithoptimizablevariables,
                 doc=None, super_group=None):
        if doc is None:
            self.Document = newDocument()
        else:
            self.Document = doc

        if super_group is None:
            self.SuperGroup = None
        else:
            self.SuperGroup = super_group
        # create subgroup in super_group or if None create group in doc
        # every class with optimizable variables should get one group

        self.Group = self.Document.addObject("App::DocumentObjectGroup",
                                             myclasswithoptimizablevariables.name)
        if self.SuperGroup is not None:
            self.SuperGroup.addObject(self.Group)
