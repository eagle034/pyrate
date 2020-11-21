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

from PySide import QtGui

import FreeCAD
import FreeCADGui


import PyrateInterface
from .Interface_Identifiers import *


class LoadSystemCommand:
    "Load optical system file"

    def GetResources(self):
        return {"MenuText": "Load Optical System from pickle ...",
                "Accel": "",
                "ToolTip": "Loads an optical system from pickles file",
                "Pixmap": ":/icons/pyrate_load_sys_icon.svg"
                }

    def IsActive(self):
        return True

    def Activated(self):
        if FreeCAD.ActiveDocument == None:
            FreeCAD.newDocument()


        fname, _ = QtGui.QFileDialog.getOpenFileName(None, 'Open file', '')

        if fname == "":
            return 1
        else:
            pass
            # Loading functionality not supported, yet


        for i in FreeCAD.ActiveDocument.Objects:
            i.touch()

        FreeCAD.ActiveDocument.recompute()

class SaveSystemCommand:
    "Save optical system file"

    def GetResources(self):
        return {"MenuText": "Save Optical System as pickle ...",
                "Accel": "",
                "ToolTip": "Saves an optical system to pickles file",
                "Pixmap": ":/icons/pyrate_save_sys_icon.svg"
                }

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):
        savedlg = QtGui.QFileDialog(None, 'Save file', '')
        savedlg.setFileMode(QtGui.QFileDialog.AnyFile)
        fname, _ = savedlg.getSaveFileName()

        if fname == "":
            return 1
        else:
            pass
            # Saving functionality not supported, yet
            # QtGui.QMessageBox.warning(None, Title_MessageBoxes, "Dumped!\n" + "Warning, pickle format may change over time!")


FreeCADGui.addCommand('LoadSystemCommand',LoadSystemCommand())
FreeCADGui.addCommand('SaveSystemCommand',SaveSystemCommand())
