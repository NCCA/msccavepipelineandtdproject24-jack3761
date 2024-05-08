
import unreal
from pathlib import Path
from pxr import Usd, UsdGeom, Sdf

ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

def usd_anim_extraction(stage: Usd.Stage) -> list[Sdf.Path]:
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

def export_anim_prims(stage: Usd.Stage, anim_obj_paths: list[Sdf.Path], target_directory:str ="") -> None:
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

        # else :
        #     temp_stage.Export(str(target_directory) + stage.GetPrimAtPath(prim_path).GetName() + ".usda")

        target_directory = ""

def add_ext_reference(prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
    references: Usd.References = prim.GetReferences()
    references.AddReference(
        assetPath=ref_asset_path,
        primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
    )

def create_usd_stage_actor(file_path: str) -> None:
    usd_stage_actor = ELL.spawn_actor_from_class(unreal.UsdStageActor , unreal.Vector())
    usd_stage_actor.set_editor_property("root_layer",unreal.FilePath( file_path ))
    
    return usd_stage_actor




if __name__ == "__main__":
    directory = "C:/Uni_Work/Bournemouth/PipelineTD/usd_exports/"
    file_name = "test_shapes.usd"
    file_path = directory + file_name

    main_usd_stage = Usd.Stage.Open(file_path)
    prim_paths = usd_anim_extraction(main_usd_stage)
    print(prim_paths)

    export_anim_prims(main_usd_stage, prim_paths)

    # main_usd_stage_actor = create_usd_stage_actor(file_path)

    # asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    # sequence = asset_tools.create_asset(asset_name="extracted_sequence", package_path="/Game/sequences", asset_class=unreal.LevelSequence, factory=unreal.LevelSequenceFactoryNew())
    # mesh_binding = sequence.add_possessable(usd_stage_actor)





#TODO
# add material to generated USD's, currently nothing shows
# adjust usd export/import to go into unreal project directory
# add unreal scripting to load in each of the generated usda files as usdstageactors
# fingers crossed they have their own level sequences
# potentially see if the files we generate can just show a reference, rather than create the whole thing
## could just form a string for the file
# Add automated access to the usdstageactor level sequences
# currently doesn't seem like anything on the maya side
# Add all GUI functionality

# add comments, doc strings and type hints (should do while working)
# write tests - also should do while working