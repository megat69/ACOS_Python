from .. import software_api
import tkinter as tk
from functools import partial
import os

app_icon = "ACOS_Textrock.png"
software_name = "Textrock - Text Editor"
software_dir = "textrock"
is_GUI = True
min_size = None
max_size = None

def on_app_launch(frame:tk.Frame, width:int=100, height:int=100):
	# Menus
	menus_frame = tk.Frame(frame, width=width, height=round(height * 0.1))

	# Name entry
	globals()["name_entry"] = tk.Entry(menus_frame)
	globals()["name_entry"].grid(row=0, column=0)

	# 'Save' button
	save_button = tk.Button(
		menus_frame,
		text = "SAVE",
		command = save_file
	)
	save_button.grid(row=0, column=1)

	# 'Open' button
	open_button = tk.Button(
		menus_frame,
		text = "OPEN",
		command = open_file
	)
	open_button.grid(row=0, column=2)

	menus_frame.pack()

	# Creating the main textbox
	globals()["main_textbox"] = tk.Text(
		frame
	)
	globals()["main_textbox"].pack(
		expand = True,
		fill = tk.BOTH
	)

def on_file_open(path):
	open_file(path)

def save_file():
	"""
	Saves the current text to a file.
	"""
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	file_to_save_in = globals()["name_entry"].get()

	if file_to_save_in.endswith(".textrock"):
		file_to_save_in = file_to_save_in[:-len(".textrock")]

	temp_name = ""
	for letter in file_to_save_in:
		if letter not in tuple("\\/:?*\"<>|"):
			temp_name += letter
	file_to_save_in = temp_name

	# Test of path existence
	if not os.path.exists("../../" + software_api.REGISTRY["USERS_FOLDER"] + "/" + software_api.current_user + "/_documents/"):
		os.mkdir("../../" + software_api.REGISTRY["USERS_FOLDER"] + "/" + software_api.current_user + "/_documents/")

	# Opening of the file
	file_to_save_in = open("../../" + software_api.REGISTRY["USERS_FOLDER"]\
	    + "/" + software_api.current_user + "/_documents/" + file_to_save_in + ".textrock", "w")

	# Saving of the contents
	file_to_save_in.write(
		globals()["main_textbox"].get(1.0, tk.END)
	)

	# Closing the file
	file_to_save_in.close()

	software_api.notify(software_name, "Saved to " \
	        +"/" + software_api.current_user + "/_documents/" + temp_name + ".textrock")

	os.chdir("../../../")

def open_file(path:str=None):
	"""
	Opens a textrock file and inserts its in the textarea.
	"""
	os.chdir(os.path.dirname(os.path.realpath(__file__)))

	if path is None:
		filename = "../../" + software_api.REGISTRY["USERS_FOLDER"]\
	        + "/" + software_api.current_user + "/_documents/" + globals()["name_entry"].get()
	else:
		filename = path
	if not filename.endswith(".textrock") and path is None:
		filename += ".textrock"

	# Test if path exists
	if not os.path.exists(filename) and path is None:
		globals()["name_entry"].config(text="File does not exist")
		return

	# Opening of the file
	file = open("../"*3 +filename, "r")
	file_contents = file.read()
	file.close()

	# Inserting the contents in the textbox
	globals()["main_textbox"].delete(1.0, tk.END)
	globals()["main_textbox"].insert(1.0, file_contents)


	software_api.notify(software_name, "Opened " \
	        +"/" + software_api.current_user + "/_documents/" + filename)

	os.chdir("../../../")
