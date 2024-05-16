import unreal
import sys


def main():
    print("Creating menus")
    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        print("Issue finding main menu")

    import_entry = unreal.ToolMenuEntry(
        name="Importer Gui",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
    )
    import_entry.set_label("USD Prim Importer")
    import_entry.set_tool_tip("Import individual USD prims from a USD file")
    import_entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", string="import ue_importer_gui; import importlib; importlib.reload(ue_importer_gui)")

    sequence_entry = unreal.ToolMenuEntry(
        name="Anim extractor",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
    )
    sequence_entry.set_label("USD Animation Player")
    sequence_entry.set_tool_tip("Find and play USDStageActor animations")
    sequence_entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", string="import ue_usd_sequence; import importlib; importlib.reload(ue_usd_sequence)")

    
    script_menu = main_menu.add_sub_menu("Custom", "Scripts", "Custom Scripts", "USD Animation")

    script_menu.add_menu_entry("Scripts", import_entry)
    script_menu.add_menu_entry("Scripts", sequence_entry)

    menus.refresh_all_widgets()


if __name__ == "__main__":
    main()