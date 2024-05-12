
import sys
# change to suitable path or change environment variables
# sys.path.append('c:\\users\\jack3\\appdata\\local\\programs\\python\\python39\\lib\\site-packages')

import unreal
import PySide2
from pathlib import Path
from pxr import Usd, UsdGeom, Sdf
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *


ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

class USDStageHandler:
    stage = None

    @classmethod
    def open_stage(cls, file_path):
        valid_extensions = [".usd", ".usda", ".usdc", ".usdz"]

        if not any(file_path.endswith(ext) for ext in valid_extensions):
            raise ValueError("Invalid USD file path")

        cls.stage = Usd.Stage.Open(file_path)
        if not cls.stage:
            raise RuntimeError("Failed to open USD stage")



class USDAnimImportDialog(QtWidgets.QDialog):    

    def __init__(self, parent=None):
        super().__init__()

        # input file section
        self.file_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        file_input_layout = QHBoxLayout()
        file_input_layout.addWidget(self.file_path_edit)
        file_input_layout.addWidget(self.browse_button)

        # list widget for prims
        self.prim_list_widget = QListWidget()
        self.prim_list_widget.setSelectionMode(QListWidget.MultiSelection)

        # create dictionary for path strings and Sdf.Path()
        self.prim_strings = {}

        # checkbox for default export directory
        self.use_default_checkbox = QCheckBox("Use Default Export Directory")
        self.use_default_checkbox.setChecked(True)
        self.use_default_checkbox.stateChanged.connect(self.toggle_export_dir_edit)

        # create export directory selection section
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setEnabled(False)  # disabled by default
        self.select_export_dir_button = QPushButton("Select export directory")
        self.select_export_dir_button.clicked.connect(self.select_export_directory)

        self.export_dir_layout = QHBoxLayout()
        self.export_dir_layout.addWidget(self.export_dir_edit)
        self.export_dir_layout.addWidget(self.select_export_dir_button)

        self.export_button = QPushButton("Export Selected Prims")
        self.export_button.clicked.connect(self.export_options())

        # set layout
        layout = QVBoxLayout()
        layout.addLayout(file_input_layout)
        layout.addWidget(self.prim_list_widget)
        layout.addWidget(self.use_default_checkbox)
        layout.addWidget(self.export_dir_edit)
        layout.addLayout(self.export_dir_layout)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "USD Files (*.usd*)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self.populate_prims_list(file_path)

    def populate_prims_list(self, file_path: str):
        self.prim_list_widget.clear()

        try:
            USDStageHandler.open_stage(file_path)
        except Exception as e:
            print("Error:", e)
            return
        
        stage = USDStageHandler.stage
        anim_prims = self.usd_anim_extraction(stage)
        
        for prim_path in anim_prims:
            self.prim_list_widget.addItem(str(prim_path))
            self.prim_strings[str(prim_path)] = prim_path

        print(self.prim_strings)


    def usd_anim_extraction(self, stage: Usd.Stage) -> list[Sdf.Path]:
        anim_obj_paths = []
        prims = []

        for prim in stage.Traverse():
            prims.append(prim.GetPath())
            for attr in prim.GetAttributes():
                if attr.GetNumTimeSamples() > 0:
                    anim_obj_paths.append(prim.GetPath())
                    break

        return anim_obj_paths
    
    def toggle_export_dir_edit(self):
        state = self.use_default_checkbox.isChecked()
        if state == 0:  
            self.export_dir_edit.setEnabled(True)
        else: 
            self.export_dir_edit.setEnabled(False)

    def select_export_directory(self):
        export_dir = QFileDialog.getExistingDirectory(self, "Select export Directory")
        if export_dir:
            self.export_dir_edit.setText(export_dir)

    def export_options(self):
        # file path used to add reference
        file_path = self.file_path_edit.text()


        prims = []
        selected_paths = self.prim_list_widget.selectedItems()
        print(type(selected_paths))
        print(selected_paths)
        

        if not self.use_default_checkbox.isChecked():
            target_directory = self.export_dir_edit.text()
        else:
            target_directory = ""
        

    def export_anim_prims(self, file_path: str, stage: Usd.Stage, anim_obj_paths: list[Sdf.Path], target_directory:str ="") -> None:
        for prim_path in anim_obj_paths :
            # create temporary stage with anim prim path as default
            temp_stage = Usd.Stage.CreateInMemory()
            default_prim = UsdGeom.Xform.Define(temp_stage, Sdf.Path("/default"))
            temp_stage.SetDefaultPrim(default_prim.GetPrim())

            # set basic stage metadata

            temp_stage.SetStartTimeCode(stage.GetStartTimeCode())
            temp_stage.SetEndTimeCode(stage.GetEndTimeCode())
            temp_stage.SetTimeCodesPerSecond(stage.GetTimeCodesPerSecond())
            temp_stage.SetFramesPerSecond(stage.GetFramesPerSecond())
            # temp_stage.SetMetersPerUnit(stage.GetMetersPerUnit()) - these functions don't exist but might be important to find and add
            # temp_stage.SetUpAxis(stage.GetUpAxis())

            ref_prim = UsdGeom.Mesh.Define(temp_stage, Sdf.Path("/default/ref_prim")).GetPrim()
            add_ext_reference(ref_prim, ref_asset_path=file_path, ref_target_path=prim_path)

            # usda = temp_stage.GetRootLayer().ExportToString()
            # print(usda)

            
            if target_directory == "":
                project_path = Path(unreal.Paths.get_project_file_path()).parent
                target_directory = project_path / "Content" / "usd_exports" / stage.GetPrimAtPath(prim_path).GetName()
                target_directory = target_directory.with_suffix(".usda")


                temp_stage.Export(str(target_directory))
                print("Creating .usda at: " + str(target_directory))

                create_usd_stage_actor(file_path=str(target_directory))

            else :
                temp_stage.Export(str(target_directory) + stage.GetPrimAtPath(prim_path).GetName() + ".usda")

            target_directory = ""

        def add_ext_reference(self, prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
            references: Usd.References = prim.GetReferences()
            references.AddReference(
                assetPath=ref_asset_path,
                primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
            )

        def create_usd_stage_actor(self, file_path: str) -> None:
            usd_stage_actor = ELL.spawn_actor_from_class(unreal.UsdStageActor , unreal.Vector())
            usd_stage_actor.set_editor_property("root_layer",unreal.FilePath( file_path ))
            
            return usd_stage_actor




if __name__ == "__main__":

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication([])
    dialog = USDAnimImportDialog()
    dialog.show()
    sys.exit(dialog.exec_())





#TODO
# potentially see if the files we generate can just show a reference, rather than create the whole thing
## could just form a string for the file
# Add automated access to the usdstageactor level sequences
# currently doesn't seem like anything on the maya side
# Add all GUI functionality
# improve usd authoring to detect correct prim types, explore the different layers of prims 
#       and use correct names in the authored file


# add comments, doc strings and type hints (should do while working)
# write tests - also should do while working
# figure out and write up deployment, go through the process on a new machine