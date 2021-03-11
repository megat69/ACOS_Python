from .. import software_api
import tkinter as tk

app_icon = "ACOS_Folder.png"
software_name = "Filesystem"
software_dir = "SYSTEM_Filesystem"
is_GUI = True
min_size = None
max_size = None

def on_app_launch(frame:tk.Frame, width:int, height:int):
	""""
	Function called on app launch.
	"""
	disclaimer = tk.Label(frame, text=f"{software_name} is not done yet...").pack()

