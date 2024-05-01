
import unreal
from pathlib import Path

destination_path = "/Game/Enviro"
source_path = "C:\Uni_Work\Bournemouth\PipelineTD\usd_exports"
assets_to_import = list(Path(source_path).glob("*.usd"))
unreal.UsdStageAssetImportFactory
tasks: list[unreal.AssetImportTask] = []


options = unreal.UsdAssetImportData
unreal.UsdStageOptions
unreal.UsdStageActor.
unreal.UsdStageImportFactory
unreal.UsdStageImportOptions

for input_file_path in assets_to_import :
    task = unreal.AssetImportTask()
    task.automated = True
    task.destination_path = destination_path
    task.destination_name = input_file_path.stem
    task.filename = str(input_file_path)
    task.replace_existing = True
    task.save = True




    tasks.append(task)


actorsList = unreal.EditorLevelLibrary.get_all_level_actors()

unreal.UsdStageActor.get