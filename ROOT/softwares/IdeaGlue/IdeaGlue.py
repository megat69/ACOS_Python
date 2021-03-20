from .. import software_api
import tkinter as tk
import os

app_icon = "ACOS_IdeaGlue.png"
software_name = "Idea glue"
software_dir = "IdeaGlue"
is_GUI = True
min_size = None
max_size = None
default_size = (200, 200)

def on_app_launch(frame:tk.Frame, width:int=200, height:int=200):
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

	# Placing the textarea
	globals()["main_textarea"].place(
		x = 0,
		y = 0,
		width = width,
		height = height
	)

	frame.after(5000, save_content, frame)
	

def save_content(frame:tk.Tk):
	"""
	Function to save the textarea content
	"""

	textarea_file = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] + "/" \
	                     + software_api.current_user + "/.ideaglue_content", "w")
	textarea_file.write(globals()["main_textarea"].get(1.0, tk.END))
	textarea_file.close()

	frame.after(3000, save_content, frame)
	
