#!/usr/bin/env/python
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

from .Interface_Identifiers import Group_StandardMaterials_Label


def isLocalCoordinatesObserver(fobj):
    tmp = 'lcclass' in fobj.PropertiesList
    return tmp


def isOpticalSystemObserver(fobj):
    tmp = 'wavelengths' in fobj.PropertiesList
    return tmp


def isFunctionsObject(fobj):
    tmp = 'functions' in fobj.PropertiesList
    return tmp


def isGroup(fobj):
    return 'Group' in fobj.PropertiesList


def isMaterialCatalogue(fobj):
    result = False
    if isGroup(fobj):
        result = any(['NameMaterialsCatalogue' in o.PropertiesList
                      for o in fobj.Group])
    return result


def isMaterial(fobj):
    return 'matclass' in fobj.PropertiesList


def existsStandardMaterialsCatalogue(doc):
    return any([obj.Label == Group_StandardMaterials_Label
                for obj in doc.Objects if isMaterialCatalogue(obj)])

def getStandardMaterialsCatalogue(doc):
    group_candidates = list([obj for obj in doc.Objects
                             if isMaterialCatalogue(obj) and
                                 obj.Label == Group_StandardMaterials_Label])
    if len(group_candidates) > 0:
        return group_candidates[0]
    else:
        return None


