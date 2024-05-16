from pathlib import Path
from ue_importer_gui import USDAnimImportDialog, USDStageHandler
import unittest
from pxr import Usd, UsdGeom, Sdf
import unreal
import sys

ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

class TestUSDStageHandler(unittest.TestCase):
    def setUp(self):
        # Directory containing test USD files
        self.test_files_dir = Path(__file__).resolve().parent / "test_files"

    def test_open_stage_valid_file(self):
        file_path = str(self.test_files_dir / "test_shapes.usd")
        USDStageHandler.open_stage(file_path)

        self.assertIsNotNone(USDStageHandler.stage)
        self.assertIsInstance(USDStageHandler.stage, Usd.Stage)

    def test_open_stage_invalid_file_extension(self):
        file_path = str(self.test_files_dir / "invalid.txt")
        with self.assertRaises(ValueError):
            USDStageHandler.open_stage(file_path)


    def test_open_stage_nonexistent_file(self):
        file_path = str(self.test_files_dir / "nonexistent.usd")
        with self.assertRaises(RuntimeError):
            USDStageHandler.open_stage(file_path)


class TestUSDAnimImportDialog(unittest.TestCase):

    def setUp(self):
        self.dialog = USDAnimImportDialog()
        self.file_path = str(Path(__file__).resolve().parent / "test_files" / "test_shapes.usd")

        self.stage = Usd.Stage.Open(self.file_path)
        

    def reload_prims_list(self):
        # set up so they are different
        self.dialog.prim_type_combo.setCurrentIndex(0)
        self.dialog.export_type_combo.setCurrentIndex(1)

        self.dialog.reload_prims_list()

        # assert that they have both been set to the same index

        self.assertEqual(self.dialog.prim_type_combo.currentIndex(), self.dialog.export_type_combo.currentIndex())

    def test_usd_prim_extraction(self):
        mesh_type = "Mesh"

        expected = [Sdf.Path('/pCube1'), Sdf.Path('/pCone1'), Sdf.Path('/pTorus1')]
        expected2 = [Sdf.Path('/pCube1'), Sdf.Path('/pCone1'), Sdf.Path('/pTorus1'), Sdf.Path('/pCylinder1')]
        actual1 = self.dialog.usd_prim_extraction(self.stage, mesh_type, True)
        actual2 = self.dialog.usd_prim_extraction(self.stage, mesh_type, False)


        self.assertEqual(expected, actual1)
        self.assertNotEqual(expected, actual2)
        self.assertEqual(expected2, actual2)

    def test_usd_prim_extraction_2(self):
        stairs_file = Path(__file__).resolve().parent / "test_files" / "stairs_objects.usd"
        stage = Usd.Stage.Open(str(stairs_file))
        mesh_type = "Camera"

        expected = [Sdf.Path('/camera1')]
        actual = self.dialog.usd_prim_extraction(stage, mesh_type, False)

        self.assertEqual(expected, actual)
        

    def test_populate_prims_list(self):
        prims = [Sdf.Path('/pCube1'), Sdf.Path('/pCone1'), Sdf.Path('/pTorus1')]
        
        self.dialog.prim_type_combo.setCurrentText("Mesh")
        self.dialog.is_animated_checkbox.setChecked(True)

        self.dialog.populate_prims_list(self.file_path)

        expected_paths = ['/pCube1', '/pCone1', '/pTorus1']
        for index in range(self.dialog.prim_list_widget.count()):
            item = self.dialog.prim_list_widget.item(index)
            self.assertIsNotNone(item)  
            self.assertIn(str(item.text()), expected_paths) 

        expected_dict = {"/pCube1": Sdf.Path('/pCube1'), "/pCone1": Sdf.Path('/pCone1'), "/pTorus1": Sdf.Path('/pTorus1')}
        self.assertEqual(self.dialog.prim_strings, expected_dict)

        self.assertEqual(self.dialog.prim_list_widget.count(), len(prims))
        self.assertEqual(len(self.dialog.prim_strings), len(prims))

    def test_toggle_export_dir_edit(self):
        self.dialog.use_default_checkbox.setChecked(True)
        self.dialog.toggle_export_dir_edit()

        self.assertFalse(self.dialog.export_dir_edit.isEnabled())
        self.assertFalse(self.dialog.select_export_dir_button.isEnabled())

        self.dialog.use_default_checkbox.setChecked(False)
        self.dialog.toggle_export_dir_edit()

        self.assertTrue(self.dialog.export_dir_edit.isEnabled())
        self.assertTrue(self.dialog.select_export_dir_button.isEnabled())

    def test_toggle_individual_export(self):
        self.dialog.individual_checkbox.setChecked(True)

        self.dialog.toggle_individual_export()

        self.assertFalse(self.dialog.file_name_edit.isEnabled())

        self.dialog.individual_checkbox.setChecked(False)

        self.dialog.toggle_individual_export()

        self.assertTrue(self.dialog.file_name_edit.isEnabled())

    def test_create_temp_stage(self):
        temp_stage = self.dialog.create_temp_stage(self.stage)

        self.assertIsInstance(temp_stage, Usd.Stage)
        self.assertEqual(temp_stage.GetStartTimeCode(), self.stage.GetStartTimeCode())
        self.assertEqual(temp_stage.GetEndTimeCode(), self.stage.GetEndTimeCode())
        self.assertEqual(temp_stage.GetTimeCodesPerSecond(), self.stage.GetTimeCodesPerSecond())
        self.assertEqual(temp_stage.GetFramesPerSecond(), self.stage.GetFramesPerSecond())

    def test_add_prim_to_stage(self):
        temp_stage = self.dialog.create_temp_stage(self.stage)
        export_type = "Mesh"
        prim_path = Sdf.Path('/pCube1')

        temp_stage = self.dialog.add_prim_to_stage(self.stage, temp_stage, self.file_path, export_type, prim_path)

        self.assertIsInstance(temp_stage, Usd.Stage)
        added_prim = temp_stage.GetPrimAtPath(Sdf.Path("/default/pCube1"))
        self.assertIsNotNone(added_prim)
        self.assertTrue(added_prim.IsA(UsdGeom.Mesh))

    def test_export_stage(self):
        temp_stage = self.dialog.create_temp_stage(self.stage)
        export_type = "Mesh"
        prim_path = Sdf.Path('/pCube1')

        file_name = "test_export"

        temp_stage = self.dialog.add_prim_to_stage(self.stage, temp_stage, self.file_path, export_type, prim_path)

        target_directory = Path(__file__).resolve().parent / "test_exports"

        self.dialog.export_stage(temp_stage, target_directory, file_name)

        expected_export_path = target_directory / (file_name + ".usda")
        self.assertTrue(expected_export_path.exists())

    def test_create_usd_stage_actor(self):
        file_path = Path(__file__).resolve().parent / "test_files" / "test_cube.usd"
        prim_name = "pCube1"
        usd_stage_actor = self.dialog.create_usd_stage_actor(str(file_path), prim_name)
        
        self.assertEqual(usd_stage_actor.get_actor_label(), "pCube1_usd")

        existing_actors = ELL.get_all_level_actors()
        usd_actors = [actor for actor in existing_actors if isinstance(actor, unreal.UsdStageActor)]

        self.assertIn(usd_stage_actor, usd_actors)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUSDStageHandler))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUSDAnimImportDialog))

    result = unittest.TextTestRunner(stream=sys.stdout, buffer=True).run(suite)