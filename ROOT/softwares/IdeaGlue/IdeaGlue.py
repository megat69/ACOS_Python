from .. import software_api
import tkinter as tk
import os
from functools import partial
from PIL import Image, ImageTk

app_icon = "ACOS_IdeaGlue.png"
software_name = "Idea glue"
software_dir = "IdeaGlue"
is_GUI = True
default_size = (250, 270)
min_size = None
max_size = None

def on_app_launch(frame:tk.Frame, width:int=default_size[0], height:int=default_size[1]):
	# Opening the textarea
	globals()["main_textarea"] = tk.Text(
		frame,
		bg = "#d8ad02"
	)

	# If the file exists, pasting its text
	try:
		textarea_file = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] + "/"\
		                     + software_api.current_user + "/.ideaglue_content", "r")
	except FileNotFoundError:
		textarea_file = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] + "/" \
		     + software_api.current_user + "/.ideaglue_content", "w")
		textarea_content = ""
	else:
		textarea_content = textarea_file.read()
	finally:
		textarea_file.close()

	# Inserting the content
	globals()["main_textarea"].insert(1.0, textarea_content)
	globals()["main_textarea"].bind("<KeyPress>", partial(display_status_icon, frame, False))

	# Placing the textarea
	globals()["main_textarea"].place(
		x = 0,
		y = 0,
		width = width + 2,
		height = height + 2
	)

	frame.after(5000, save_content, frame)

	frame.bind("<Configure>", partial(on_resize, frame))
	
def on_resize(frame, event):
	globals()["main_textarea"].place(
		x = 0,
		y = 0,
		width = frame.winfo_width(),
		height = frame.winfo_height()
	)

def display_status_icon(frame, saved:bool=True, event=None):
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	icon_size = 16

	globals()["status_icon_TkImage"] = ImageTk.PhotoImage(
		Image.open(
			("Not" if saved is False else "") + "Saved.png"
		).resize((icon_size, icon_size))
	)
	globals()["status_icon"] = tk.Label(
		frame,
		image = globals()["status_icon_TkImage"],
		bg = "#d8ad02"
	)
	globals()["status_icon"].place(
		x = frame.winfo_width() - icon_size,
		y = frame.winfo_height() - icon_size
	)
	globals()["status_icon"].bind("<Button-1>", partial(save_content, frame))

	os.chdir("../../../")


def save_content(frame:tk.Tk, event=None):
	"""
	Function to save the textarea content
	"""

	textarea_file = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] + "/" \
	                     + software_api.current_user + "/.ideaglue_content", "w")
	textarea_file.write(globals()["main_textarea"].get(1.0, tk.END)[:-1])
	textarea_file.close()

	display_status_icon(frame, True)

	frame.after(3000, save_content, frame)
	
