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

import FreeCAD
import FreeCADGui


from pyrateoptics.optimize import optimize

from .Observer_OpticalSystem import OpticalSystemObserver
from .Dialog_Optimization import OptimizationDialog

class StartOptimizationCommand:
    "Starts optimization"

    def GetResources(self):
        return {"MenuText": "Start Optimization",
                "Accel": "",
                "ToolTip": "Starts Optimization",
                "Pixmap": ":/icons/pyrate_del_sys_icon.svg"
                }

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):

        # TODO: obsolete

        # non-well defined interface to internal variables of optical system
        OSinterface.os.surfaces[2].setStatus("curvature", True)
        OSinterface.os.surfaces[3].setStatus("curvature", True)
        OSinterface.os.surfaces[4].setStatus("curvature", True)
        OSinterface.os.surfaces[5].setStatus("curvature", True)
        OSinterface.os.surfaces[7].setStatus("curvature", True)

        # input

        #numsteps_t = QtGui.QLineEdit("bla", None) # 1
        #dx_t = QtGui.QLineEdit("bla", None) # 1e-6

        #FreeCAD.Console.PrintMessage(str(numsteps_t))

        optdlg = OptimizationDialog(1, 1e-6)
        optdlg.exec_()
        numsteps = optdlg.iterations
        delta = optdlg.dx

        # optimization

        #OSinterface.os = \
        #optimize.optimizeNewton1D(OSinterface.os,
        #                          merit.mySimpleDumpRMSSpotSizeMeritFunction, iterations=numsteps, dx=delta
        #                          )
        # update
        # TODO: organize in PyrateInterface class

        doc = FreeCAD.ActiveDocument

        OSinterface.deleteSurfaces(doc)
        OSinterface.deleteRays(doc)
        # abfrage!
        OSinterface.createSurfaceViews(doc)
        OSinterface.createRayViews(doc, OSinterface.shownumrays)


        for i in doc.Objects:
            i.touch()

        doc.recompute()




FreeCADGui.addCommand('StartOptimizationCommand',StartOptimizationCommand())
