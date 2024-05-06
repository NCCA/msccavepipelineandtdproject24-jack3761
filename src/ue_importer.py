
import unreal
from pathlib import Path
from pxr import Usd, UsdGeom, Sdf

ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

directory = "C:/Uni_Work/Bournemouth/PipelineTD/usd_exports/"
file_name = "test_shapes.usd"
file_path = directory + file_name


def usd_anim_extraction(stage) :
    anim_obj_paths = []
    prims = []

    for prim in stage.Traverse():
        prims.append(prim.GetPath())
        for attr in prim.GetAttributes():
            if attr.GetNumTimeSamples() > 0:
                anim_obj_paths.append(prim.GetPath())
                break

    # print(anim_obj_paths)
    return anim_obj_paths

def export_anim_prims(stage, anim_obj_paths, target_directory=""):
    for prim_path in anim_obj_paths :
        temp_stage = Usd.Stage.CreateInMemory()
        default_prim = UsdGeom.Xform.Define(temp_stage, Sdf.Path("/default"))
        temp_stage.SetDefaultPrim(default_prim.GetPrim())
        ref_prim = UsdGeom.Xform.Define(temp_stage, Sdf.Path("/default/ref_prim")).GetPrim()
        add_ext_reference(ref_prim, ref_asset_path=file_path, ref_target_path=prim_path)

        # usda = temp_stage.GetRootLayer().ExportToString()
        # print(usda)

        temp_stage.Export(target_directory + stage.GetPrimAtPath(prim_path).GetName() + ".usda")

def add_ext_reference(prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
    references: Usd.References = prim.GetReferences()
    references.AddReference(
        assetPath=ref_asset_path,
        primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
    )


usd_stage_actor = ELL.spawn_actor_from_class(unreal.UsdStageActor , unreal.Vector())
usd_stage_actor.set_editor_property("root_layer",unreal.FilePath( file_path ))
usd_sequence = usd_stage_actor.get_level_sequence()

# asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
# sequence = asset_tools.create_asset(asset_name="extracted_sequence", package_path="/Game/sequences", asset_class=unreal.LevelSequence, factory=unreal.LevelSequenceFactoryNew())
# mesh_binding = sequence.add_possessable(usd_stage_actor)

print(usd_sequence.get_possessables())
print(usd_sequence.get_tracks())
print(usd_sequence.get_root_folders_in_sequence())
# unreal.LevelSequence.

# instead of exporting lots of individual usd files, we create lightweight stages that just have one prim
# that references what we want. 

# Hopefully then we can spawn a usdstageactor with this reference and fingers crossed it'll have the animation

# then if reference is updated maybe we can still facilitate change, making the USD use not



#TODO
# adjust usd export/import to go into unreal project directory
# add unreal scripting to load in each of the generated usda files as usdstageactors
# fingers crossed they have their own level sequences
# potentially see if the files we generate can just show a reference, rather than create the whole thing
## could just form a string for the file
# Add automated access to the usdstageactor level sequences
# currently doesn't seem like anything on the maya side