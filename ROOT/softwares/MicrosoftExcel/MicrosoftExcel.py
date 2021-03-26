from .. import software_api
from .. import webapp_generator
from cefpython3 import cefpython as cef

try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
import platform
import logging as _logging

app_icon = "Excel.png"
software_name = "Microsoft Excel"
software_dir = "MicrosoftExcel"
is_GUI = True
min_size = (800, 440)
max_size = None
default_size = (900, 640)

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# Globals
logger = _logging.getLogger("tkinter_.py")

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

def on_app_launch(frame: tk.Frame, width: int = 900, height: int = 640):
	# Testing if connection
	if software_api.test_connection() is True:
		if "no_connection_title" in globals():
			globals()["no_connection_title"].pack_forget()
			globals()["no_connection_title"].destroy()
			globals()["no_connection_subtitle"].pack_forget()
			globals()["no_connection_subtitle"].destroy()

		# Launching webapp
		webapp_generator.launch(frame, "https://www.office.com/launch/excel")

	else:
		if not "no_connection_title" in globals():
			globals()["no_connection_title"] = tk.Label(
				frame,
				text="Oh No !",
				font=("Impact", 22)
			)
			globals()["no_connection_title"].pack()
			globals()["no_connection_subtitle"] = tk.Label(
				frame,
				text="Sounds like no connection is available...",
				font=("Impact", 14)
			)
			globals()["no_connection_subtitle"].pack()
		# Testing again
		frame.after(5000, on_app_launch, frame, width, height)