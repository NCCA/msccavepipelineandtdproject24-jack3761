import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import tempfile

class USDExporter () :

    def get_selection_clicked(self) :
        current_view = cmds.getPanel( withFocus = True)
        objects = cmds.ls(sl=True)
        if len(objects) == 0 :
            cmds.warning("No objects selected")
        dir="home/s5603002/usd_tests/"
        cmds.hide(all = True)

        for obj in objects :
            cmds.group(empty=True, world=True, name="exportGRP")
            cmds.showHidden("exportGRP")
            for item in cmds.listRelatives(obj, f=True):
                dup_name = cmds.duplicate(item, rr=True)
                cmds.parent(dup_name, "exportGRP")

        cmds.select("exportGRP")
        cmds.CenterPivot()
        cmds.move(0,0,0, "exportGRP", rotatePivotRelative=True)
        cmds.file(dir+"test1", pr=1, type="USD Export",exportSelected=1, 
                op="defaultUSDFormat=usda;mergeTransformAndShape=1;exportDisplayColor=1;exportDisplayColor=1;exportDisplayOpacity=1;exportUVs=1;exportNormals=1;exportMaterialAssignments=1;exportVisibility=1;exportCameras=1;exportLights=1;shadingMode=useRegistry")
        cmds.delete("exportGRP")
        cmds.showHidden( all=True )

            

