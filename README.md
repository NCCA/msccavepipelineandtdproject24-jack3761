# Maya to Unreal Engine 5 USD pipeline for mesh and camera animation

## Project aim

The aim for this project is to produce a pipeline tool that will allow a simplified pipeline for exporting USD assets in Maya and using them in UE5. While there are already simple pipelines to achieve this, in this case the aim is to be able to quickly isolate the animation of mesh and camera objects so they can be accessed individually within a future project to expand this idea into a complete Unreal Engine plugin with more features. 

## Current plan

### This plan is due to change throughout the project as further developments are made

* Write a python script with a GUI to read in the individual animations from a USD stage.
- GUI should be accessible from a button, current idea is to add unreal startup script to add the button to a built in menu, and that button starts the GUI.
- Either that or build it in with C++
* Automate the process of assigning these into level sequences that can be accessed throughout the project.
- Need to look into whether the USD Stage import area is best for this, or for the user to provide USD file path and use that independently.
* Ensure that these USD animation references remain within the project upon restart.

Throughout the development of the Unreal side of the pipeline, I will be using the regular exporter from Maya. In doing this, I hope to learn about any areas in this process that may be made quicker or automated with an additionally script, and from there I will write a script and GUI for the Maya USD export. Currently, I predict that this will be a simplified export menu that has minimal input and only writes the necessary parts of the scene required for the UE import.

The outcome of this project should be scalable, so that it can grow to import more features from the Maya pipeline seemlessly, and to further develop into a full plugin.

---

## Research

Helpful links throughout this project are listed below

- [Unreal Engine USD Description](https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine)
- [Unreal Engine Python Description](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.3)
- [Python for Unreal Engine](https://www.youtube.com/watch?v=OwZxr1SMluY&list=PLA5eKtL_PFiMJwn80t4WWlrAdOn-fE3X6&pp=iAQB)
- [Unreal Engine 5 Python Automation Course](https://www.youtube.com/watch?v=mmiV0qKMTio&list=PLKgYiIAqG99cwlb4Y2Pu-cSb_Vw14-t0c&pp=iAQB)
- [Universal Scene Description](https://openusd.org/release/index.html)
- [Unreal Animation Import Pipeline](https://www.youtube.com/watch?v=XvnLMpvGZ34&ab_channel=TonyBowren)
- [Adding script to UE menu](https://medium.com/@TechArtCorner/executing-python-scripts-from-unreal-engine-5-menus-90b917981020)
- [UE Python sequencer cookbook](https://dev.epicgames.com/community/learning/knowledge-base/0qK6/unreal-engine-ue4-sequencer-python-cookbook)
- [UE4 Knowledgebase for sequencer scripting](https://forums.unrealengine.com/t/knowledge-base-ue4-sequencer-python-cookbook/265097/10)
- [Animated prim attributes forum](https://forums.developer.nvidia.com/t/get-animated-prim-attributes-per-frame-time/222735/4)
- [Add USD Reference](https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/usd/references-payloads/add-reference.html)
- [UE Set up pyside](https://www.petfactory.se/notes/ue5-python-pyside2/)
- [Creating UE menus in python](https://forums.unrealengine.com/t/making-menus-in-py/144498/7)