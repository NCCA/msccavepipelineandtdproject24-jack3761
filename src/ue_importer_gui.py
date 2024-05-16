"""
GUI class to detect USD prims with animation and individually import them to Unreal Engine 5 as USDStageActors

"""

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
    """ Handler class to store the current USD Stage object"""
    stage = None

    @classmethod
    def open_stage(cls, file_path):
        """class method to open and store current USD Stage

        Parameters
        -----------
        file_path : str

            string address for the location of the USD file to be loaded


        """

        valid_extensions = [".usd", ".usda", ".usdc", ".usdz"]

        if not any(file_path.endswith(ext) for ext in valid_extensions):
            raise ValueError("Invalid USD file path")

        cls.stage = Usd.Stage.Open(file_path)
        if not cls.stage:
            raise RuntimeError("Failed to open USD stage")



class USDAnimImportDialog(QtWidgets.QDialog):    
    """
    A dialog for importing USD animations

    Attributes:
        file_path_edit (QLineEdit): Input field for file path.
        prim_list_widget (QListWidget): List widget for displaying prims.
        prim_strings (dict): Dictionary to store path strings and Sdf.Path().
        use_default_checkbox (QCheckBox): Checkbox for default export directory.
        export_dir_edit (QLineEdit): Input field for export directory.
        export_button (QPushButton): Button for exporting selected prims.
    """
    def __init__(self, parent=None):

        """ Initialise the USDAnimImportDialog """
        
        super().__init__()

        # input file section
        self.file_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        self.file_input_layout = QHBoxLayout()
        self.file_input_layout.addWidget(QLabel("File Path:"))
        self.file_input_layout.addWidget(self.file_path_edit)
        self.file_input_layout.addWidget(self.browse_button)

        self.prim_type_combo = QComboBox()
        self.prim_type_combo.addItem("Mesh")
        self.prim_type_combo.addItem("Camera")
        self.prim_type_combo.addItem("XForm")

        self.is_animated_checkbox = QCheckBox("Animated")
        self.is_animated_checkbox.setChecked(False)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload_prims_list)

        self.prim_type_layout = QHBoxLayout()
        self.prim_type_layout.addWidget(self.prim_type_combo)
        self.prim_type_layout.addWidget(self.is_animated_checkbox)
        self.prim_type_layout.addWidget(self.reload_button)

        # list widget for prims
        self.prim_list_widget = QListWidget()
        self.prim_list_widget.setSelectionMode(QListWidget.MultiSelection)

        # create dictionary for path strings and Sdf.Path()
        self.prim_strings = {}

        # checkbox for default export directory
        self.use_default_checkbox = QCheckBox("Use Default Export Directory")
        self.use_default_checkbox.setChecked(True)
        self.use_default_checkbox.stateChanged.connect(self.toggle_export_dir_edit)

        self.individual_checkbox = QCheckBox("Export individually")
        self.individual_checkbox.setChecked(True)
        self.individual_checkbox.stateChanged.connect(self.toggle_individual_export)


        self.file_name_edit = QLineEdit()
        self.file_name_edit.setEnabled(False)

        self.export_checkboxes = QHBoxLayout()
        self.export_checkboxes.addWidget(self.use_default_checkbox)
        self.export_checkboxes.addWidget(self.individual_checkbox)
        self.export_checkboxes.addWidget(QLabel("File Name:"))
        self.export_checkboxes.addWidget(self.file_name_edit)

        # create export directory selection section
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItem("Mesh")
        self.export_type_combo.addItem("Camera")
        self.export_type_combo.addItem("XForm")
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setEnabled(False)  # disabled by default
        self.select_export_dir_button = QPushButton("Select export directory")
        self.select_export_dir_button.setEnabled(False)
        self.select_export_dir_button.clicked.connect(self.select_export_directory)

        self.export_dir_layout = QHBoxLayout()
        self.export_dir_layout.addWidget(QLabel("Export Type:"))
        self.export_dir_layout.addWidget(self.export_type_combo)
        self.export_dir_layout.addWidget(QLabel("Export Directory:"))
        self.export_dir_layout.addWidget(self.export_dir_edit)
        self.export_dir_layout.addWidget(self.select_export_dir_button)

        self.export_button = QPushButton("Export Selected Prims")
        self.export_button.clicked.connect(self.export_options)

        # set layout
        layout = QVBoxLayout()        
        layout.addLayout(self.file_input_layout)
        layout.addWidget(QLabel("Prim Type:"))
        layout.addLayout(self.prim_type_layout)
        layout.addWidget(QLabel("Select imported prims:"))        
        layout.addWidget(self.prim_list_widget)
        layout.addLayout(self.export_checkboxes)
        layout.addLayout(self.export_dir_layout)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

    def browse_file(self) -> None:
        """
        Open a file dialog to browse and select a USD file

        The selected file path is displayed in the file path edit field,
        and the prims list is populated based on the selected file.

        Returns:
            None
        """

        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "USD Files (*.usd*)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self.populate_prims_list(file_path)
    
    def reload_prims_list(self):
        """ Calls populate_prims_list on button press"""
        file_path = self.file_path_edit.text()
        self.populate_prims_list(file_path)
        self.export_type_combo.setCurrentIndex(self.prim_type_combo.currentIndex())

    def populate_prims_list(self, file_path: str) -> None:
        """
        Populate the prims list widget with animation prims from the specified USD file.

        Parameters
        ----------
            file_path : str             
                The path to the USD file.

        Returns
        -------
            None
        """
        self.prim_list_widget.clear()

        try:
            USDStageHandler.open_stage(file_path)
        except Exception as e:
            print("Error:", e)
            return
        
        stage = USDStageHandler.stage

        mesh_type = self.prim_type_combo.currentText()
        is_animated = self.is_animated_checkbox.isChecked()

        prims = self.usd_prim_extraction(stage, mesh_type, is_animated)
        
        for prim_path in prims:
            self.prim_list_widget.addItem(str(prim_path))
            self.prim_strings[str(prim_path)] = prim_path


    def usd_prim_extraction(self, stage: Usd.Stage, mesh_type: str, is_animated: bool) -> list[Sdf.Path]:
        """
        Extract the USD Prim paths that contain time samples within any of their attributes

        Parameters
        ----------

        stage : Usd.Stage
            the USD stage to extract from

        Returns
        -------

        list
            prim paths of animated objects
        
        """
        prim_paths = []

        if mesh_type == "Mesh":
            prims = self.find_prims_by_type(stage, UsdGeom.Mesh)
        elif mesh_type == "Camera":
            prims = self.find_prims_by_type(stage, UsdGeom.Camera)
        else:
            prims = self.find_prims_by_type(stage, UsdGeom.Xform)

        for prim in prims:
            if is_animated:
                for attr in prim.GetAttributes():
                    if attr.GetNumTimeSamples() > 0:
                        prim_paths.append(prim.GetPath())
                        break
            else:
                prim_paths.append(prim.GetPath())

        return prim_paths
    
    def toggle_export_dir_edit(self):
        """ Toggle whether to use default export directory or chosen"""

        state = self.use_default_checkbox.isChecked()
        if state == 0:  
            self.export_dir_edit.setEnabled(True)
            self.select_export_dir_button.setEnabled(True)
        else: 
            self.export_dir_edit.setEnabled(False)
            self.select_export_dir_button.setEnabled(False)
        
        self.toggle_individual_export()

    def toggle_individual_export(self):
        """ Toggle whether to export individual prims or together"""
        state = self.individual_checkbox.isChecked()
        if state == 0:  
            self.file_name_edit.setEnabled(True)
        else: 
            self.file_name_edit.setEnabled(False)



    def select_export_directory(self):
        """ Opens a file dialog to browse and select directory to export animated prim files to"""

        export_dir = QFileDialog.getExistingDirectory(self, "Select export Directory")
        if export_dir:
            self.export_dir_edit.setText(export_dir)

    def export_options(self):
        """
        Called from the button click event to set up export of selected animated prims
        """
        file_path = self.file_path_edit.text()

        stage = USDStageHandler.stage        

        selected_paths = self.prim_list_widget.selectedItems()

        anim_obj_paths = []

        for path in selected_paths:
            anim_obj_paths.append(self.prim_strings[path.text()])

        export_type = self.export_type_combo.currentText()

        export_individual = self.individual_checkbox.isChecked()

        if not self.use_default_checkbox.isChecked():
            target_directory = self.export_dir_edit.text()
        else:
            target_directory = ""

        if export_individual:
            self.export_anim_prims(file_path, stage, anim_obj_paths, export_type, export_individual, target_directory)
        else:
            file_name = self.file_name_edit.text()
            self.export_anim_prims(file_path, stage, anim_obj_paths, export_type, export_individual, target_directory, file_name)
        
    # TODO refactor to remove repeated code
    def export_anim_prims(self, file_path: str, stage: Usd.Stage, anim_obj_paths: list[Sdf.Path], export_type: str, export_individual: bool, target_directory:str ="", file_name: str="untitled") -> None:
        """
        Export animation prims to USD files

        Parameters
        ----------
            file_path : str 
                The original USD file path.
            stage : Usd.Stage
                The USD stage containing animation prims
            anim_obj_paths : list[Sdf.Path]
                List of Sdf.Path objects representing animation prims
            target_directory : str, optional
                The target directory for exporting USD files. Defaults to ""

        Returns
        -------
            None
        """
        if export_individual:
            for prim_path in anim_obj_paths :
                temp_stage = self.create_temp_stage(stage)
                temp_stage = self.add_prim_to_stage(stage, temp_stage, file_path, export_type, prim_path)
                file_name = stage.GetPrimAtPath(prim_path).GetName()

                self.export(temp_stage, target_directory, file_name)

                target_directory = ""
        else:
            temp_stage = self.create_temp_stage(stage)
            for prim_path in anim_obj_paths:
                temp_stage = self.add_prim_to_stage(stage, temp_stage, file_path, export_type, prim_path)

            self.export(temp_stage, target_directory, file_name)

            target_directory = ""

    def create_temp_stage(self, stage: Usd.Stage):
        # create temporary stage with anim prim path as default

        temp_stage = Usd.Stage.CreateInMemory()
        default_prim = UsdGeom.Xform.Define(temp_stage, Sdf.Path("/default"))
        temp_stage.SetDefaultPrim(default_prim.GetPrim())
        
        # set basic stage metadata

        temp_stage.SetStartTimeCode(stage.GetStartTimeCode())
        temp_stage.SetEndTimeCode(stage.GetEndTimeCode())
        temp_stage.SetTimeCodesPerSecond(stage.GetTimeCodesPerSecond())
        temp_stage.SetFramesPerSecond(stage.GetFramesPerSecond())

        return temp_stage

    def add_prim_to_stage(self, stage: Usd.Stage, temp_stage: Usd.Stage, file_path: str, export_type: str, prim_path: Sdf.Path):
        prim_name = stage.GetPrimAtPath(prim_path).GetName()

        new_path = "/default/" + prim_name

        if export_type == "Mesh":
            ref_prim = UsdGeom.Mesh.Define(temp_stage, Sdf.Path(new_path)).GetPrim()
        elif export_type == "Camera":
            ref_prim = UsdGeom.Camera.Define(temp_stage, Sdf.Path(new_path)).GetPrim()
        else:
            ref_prim = UsdGeom.Xform.Define(temp_stage, Sdf.Path(new_path)).GetPrim()

        self.add_ext_reference(ref_prim, ref_asset_path=file_path, ref_target_path=prim_path)

        return temp_stage

    def export(self, temp_stage, target_directory, file_name):
        if target_directory == "":
            project_path = Path(unreal.Paths.get_project_file_path()).parent
            target_directory = project_path / "Content" / "usd_exports" / file_name
        else :
            target_directory = Path(target_directory) / file_name

        target_directory = target_directory.with_suffix(".usda")

        temp_stage.Export(str(target_directory))
        print("Creating .usda at: " + str(target_directory))

        self.create_usd_stage_actor(str(target_directory ), file_name)

    
    def add_ext_reference(self, prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
            """
            Code from NVidia Omniverse dev guide to add USD reference prim to a stage

            https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/usd/references-payloads/add-reference.html
            """
            references: Usd.References = prim.GetReferences()
            references.AddReference(
                assetPath=ref_asset_path,
                primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
            )

    def find_prims_by_type(self, stage: Usd.Stage, prim_type: type[Usd.Typed]) -> list[Usd.Prim]:
        """
            Code from NVidia Omniverse dev guide to find prims of a given type

            https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/usd/hierarchy-traversal/find-prims-by-type.html
        """
        found_prims = [x for x in stage.Traverse() if x.IsA(prim_type)]
        return found_prims
        
    def create_usd_stage_actor(self, file_path: str, prim_name: str) -> None:
        usd_stage_actor = ELL.spawn_actor_from_class(unreal.UsdStageActor , unreal.Vector())
        usd_stage_actor.set_editor_property("root_layer",unreal.FilePath( file_path ))
        usd_stage_actor.set_actor_label(prim_name + "_usd")
        
        return usd_stage_actor


# if __name__ == "__ue_importer_gui__":

if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication([])
dialog = USDAnimImportDialog()
dialog.show()

unreal.parent_external_window_to_slate(dialog.winId())