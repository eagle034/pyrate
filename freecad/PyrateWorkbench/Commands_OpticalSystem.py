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

import FreeCAD
import FreeCADGui

from PySide.QtGui import QLineEdit, QInputDialog


from .Observer_OpticalSystem import OpticalSystemObserver
from .Object_MaterialCatalogue import MaterialCatalogueObject

from .Interface_Identifiers import (Title_MessageBoxes,
                                    Group_StandardMaterials_Label)
from .Interface_Checks import (existsStandardMaterialsCatalogue,
                               isOpticalSystemObserver)
from .Interface_Helpers import (getStandardMaterialsCatalogue,
                                getStandardMaterialsCatalogueObject,
                                getMaterialCatalogueObject,
                                getAllMaterialsFromMaterialCatalogue)

from .TaskPanel_SurfaceList_Edit import SurfaceListTaskPanelEdit

class CreateSystemTool:
    "Tool for creating optical system"

    def GetResources(self):
        return {"Pixmap"  : ":/icons/pyrate_logo_icon.svg", # resource qrc file needed, and precompile with python-rcc
                "MenuText": "Create optical system ...",
                "Accel": "",
                "ToolTip": "Opens dialog for system creation"
                }

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            return True

    def Activated(self):

        doc = FreeCAD.ActiveDocument
        (text, ok) = QInputDialog.getText(None, Title_MessageBoxes, "Name for optical system?", QLineEdit.Normal)
        osobs = None
        if text and ok:
            osobs = OpticalSystemObserver(doc, text)

        if not existsStandardMaterialsCatalogue(doc):
            # No question for adding the standard material catalogue anymore
            # result = QMessageBox.question(None, Title_MessageBoxes,
            #                               "No Standard Materials Catalogue defined. Create one?",
            #                               QMessageBox.Yes | QMessageBox.No)
            # if result == QMessageBox.Yes:
            # create standard materials catalogue
            stdmatcatalogue = MaterialCatalogueObject(
                doc, Group_StandardMaterials_Label)
        else:
            # get standard materials catalogue
            stdmatcatalogue = getStandardMaterialsCatalogueObject(doc)

        if stdmatcatalogue is not None:
            # TODO: put initialization procedure elsewhere

            # check whether the materials are already in the catalogue
            # if yes, do nothing
            stdmatcatalogue_group = getStandardMaterialsCatalogue(doc)
            all_materials_in_stdmatcatalogue =\
                getAllMaterialsFromMaterialCatalogue(stdmatcatalogue_group)
            if not any([material.Name in ("PMMA",
                                          "Vacuum",
                                          "mydefaultmodelglass")
                        for material in all_materials_in_stdmatcatalogue]):
                # checked for .Name since .Label may change afterwards, Name
                # not
                stdmatcatalogue.addMaterial("ConstantIndexGlass", "PMMA",
                                            index=1.5)
                stdmatcatalogue.addMaterial("ConstantIndexGlass", "Vacuum")
                stdmatcatalogue.addMaterial("ModelGlass", "mydefaultmodelglass")

        if osobs != None:
            osobs.initFromGivenOpticalSystem(osobs.initDemoSystem())

        # TODO: 1 OSinterface per doc, but several optical systems
        # TODO: call wizard for creation of new system

        # old code

        # doc.OSinterface.dummycreate4() # substitute by system creation dialog
        # dummycreate() -> lens system
        # dummycreate2() -> mirror system
        # dummycreate3() -> lens system with incorrect curvature in surface7
        # dummycreate4() -> GRIN medium
        # doc.OSinterface.createSurfaceViews(doc)
        # doc.OSinterface.showAimFiniteSurfaceStopDialog()
        # doc.OSinterface.showFieldWaveLengthDialog()
        # doc.OSinterface.createRayViews(doc, 50)
        #PyrateInterface.OSinterface.showSpotDiagrams(100)


class ShowRaybundlesTool:
    "Tool for showing raybundles"

    def GetResources(self):
        return {"Pixmap"  : ":/icons/pyrate_rays_icon.svg", # resource qrc file needed, and precompile with python-rcc
                "MenuText": "Actualize rays ...",
                "Accel": "",
                "ToolTip": "Actualize rays"
                }

    def IsActive(self):
        if FreeCAD.ActiveDocument == None:
            return False
        else:
            selection = FreeCADGui.Selection.getSelection()
            if len(selection) == 1 and isOpticalSystemObserver(selection[0]): #('wavelengths' in selection[0].PropertiesList):
                # TODO: comparison with CheckObjects function?
                return True
            else:
                return False

    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        if isOpticalSystemObserver(selection[0]):
            doc = FreeCAD.ActiveDocument
            # preliminary deletion of former Ray objects
            # TODO: subgroup in OS group
            raysobjectslabel = [o.Label for o in doc.Objects if o.Label.find("Ray") != -1]
            for r in raysobjectslabel:
                doc.removeObject(r)

            obj = selection[0]
            aimys = obj.Proxy.calculateAimys()
            rays = obj.Proxy.calculateRaypaths(aimys)
            obj.Proxy.drawRaypaths(rays)


class ShowSurfaceListTool:
    def GetResources(self):
        return {"Pixmap"  : ":/icons/pyrate_shape_icon.svg",
                "MenuText": "Edit Surface List ...",
                "Accel": "",
                "ToolTip": "Manage Surface List"
                }

    def IsActive(self):

        if FreeCAD.ActiveDocument == None:
            return False
        else:
            selection = FreeCADGui.Selection.getSelection()
            if len(selection) == 1 and isOpticalSystemObserver(selection[0]): #('wavelengths' in selection[0].PropertiesList):
                # TODO: comparison with CheckObjects function?
                return True
            else:
                return False

    def Activated(self):
        osselection = FreeCADGui.Selection.getSelection()[0] # only active if len = 1 and obj is appropriate


        # TODO: In menu: Add, Del Surf001, Delf Surf002, ..., Del Surf00N
        # TODO: Enums must have actualized with Labels of defined surfaces
        # TODO: every time something is changed the list in the core opticalsystem has to be actualized
        # TODO: initial Surfaces list from pyrateoptics opticalsystem
        # TODO: initial enumeration list from pyrateoptics opticalsystem

        panel = SurfaceListTaskPanelEdit(osselection)
        FreeCADGui.Control.showDialog(panel)



FreeCADGui.addCommand('CreateSystemCommand', CreateSystemTool())
FreeCADGui.addCommand('ShowSurfaceDialogCommand', ShowSurfaceListTool())
FreeCADGui.addCommand('ShowRaybundlesCommand', ShowRaybundlesTool())

