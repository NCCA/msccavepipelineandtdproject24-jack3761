"""
GUI class to detect USDStageActors within Unreal Engine and play their level sequences

"""

import unreal
import PySide2
from pathlib import Path
from pxr import Usd, UsdGeom, Sdf
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *

ELL = unreal.EditorLevelLibrary()
EAL = unreal.EditorAssetLibrary()

class USDSequenceDetectorDialog(QtWidgets.QDialog):
    """
    A dialog to find USDStageActors in a scene and play their animations

    """
    
    def __init__(self, parent=None):
        super().__init__()

        self.usd_stage_actor_list = QListWidget()
        self.usd_stage_actor_dict = {}

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.get_usd_stage_actors)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_button_event)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addWidget(self.play_button)

        layout = QVBoxLayout()
        layout.addWidget(self.usd_stage_actor_list)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)

        self.get_usd_stage_actors()

    def get_usd_stage_actors(self):
        """ Find all of the UsdStageActors within the level """
        actors = ELL.get_all_level_actors()
        usd_actors = [actor for actor in actors if isinstance(actor, unreal.UsdStageActor)]
        for actor in usd_actors:
            label = actor.get_actor_label()
            self.usd_stage_actor_list.addItem(label)

            self.usd_stage_actor_dict[label] = actor

    def play_button_event(self):
        """ Play the selected UsdStageActor's animation"""
        selected_item = self.usd_stage_actor_list.selectedItems()[0].text()
        usd_actor = self.usd_stage_actor_dict[selected_item]

        actor_sequence = usd_actor.get_level_sequence()

        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(actor_sequence)
        unreal.LevelSequenceEditorBlueprintLibrary.play()


if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication([])
dialog = USDSequenceDetectorDialog()
dialog.show()

unreal.parent_external_window_to_slate(dialog.winId())

