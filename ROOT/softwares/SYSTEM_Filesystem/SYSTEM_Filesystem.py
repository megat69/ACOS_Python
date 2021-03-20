from .. import software_api
import tkinter as tk
import json
import os
from PIL import Image, ImageTk
import importlib
import ROOT.softwares as all_softwares
from functools import partial
import shutil

app_icon = "ACOS_Folder.png"
software_name = "Filesystem"
software_dir = "SYSTEM_Filesystem"
is_GUI = True
min_size = None
max_size = None
default_size = None

is_admin = False
userdata = {}
path = "ROOT/" + software_api.REGISTRY["USERS_FOLDER"] + "/" + software_api.current_user + "/"

def get_userdata():
	global is_admin
	global userdata
	os.chdir(os.path.dirname(os.path.realpath(__file__)))

	try:
		userdata_file = open("../../" + software_api.REGISTRY["USERS_FOLDER"] \
		                     + "/" + software_api.current_user + "/" + software_api.REGISTRY["USERDATA_NAME"] \
		                     + "/" + "filesystem.json", "r")
	except FileNotFoundError:
		userdata_file = open("../../" + software_api.REGISTRY["USERS_FOLDER"] \
		                     + "/" + software_api.current_user + "/" + software_api.REGISTRY["USERDATA_NAME"] \
		                     + "/" + "filesystem.json", "w")
		userdata = {"style": "details"}
		json.dump(userdata, userdata_file)
		userdata_file.close()
	else:
		userdata = json.load(userdata_file)
		userdata_file.close()

	userdata_file = open("../../" + software_api.REGISTRY["USERS_FOLDER"] \
	        + "/" + software_api.current_user + "/" + software_api.REGISTRY["USERDATA_NAME"] + ".json", "r")
	is_admin = json.load(userdata_file)["is_admin"]
	userdata_file.close()

	os.chdir("../../../")

def on_app_launch(frame: tk.Frame, width: int, height: int):
	""""
	Function called on app launch.
	"""
	global path
	get_userdata()
	global userdata

	def change_path(new_path, event=None):
		global path
		nonlocal frame
		if new_path != "" or new_path != "/":
			path = new_path
			software_api.destroy_all_widgets(frame)
			on_app_launch(frame, width, height)

	frame.config(bg=software_api.REGISTRY["MAIN_BG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]])
	elements = []
	general_params = {
		"bg": software_api.REGISTRY["MAIN_BG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]],
		"fg": software_api.REGISTRY["MAIN_FG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]]
	}

	# Columns names
	font = ("Impact", 12)
	new_folder_name = tk.StringVar()
	def new_folder():
		try:
			os.mkdir(path + "/" + new_folder_name.get())
		except:
			software_api.notify(software_name, f"Folder '{new_folder_name.get()}' couldn't be created.")
		# Refresh
		change_path(path)
	elements.append(
		(
			tk.Label(frame, text="<-", **general_params),
			tk.Label(frame, text="Name", font=font, **general_params),
			tk.Label(frame, text="File type", font=font, **general_params),
			tk.Label(frame, text="File size", font=font, **general_params),
			tk.Entry(frame, textvariable=new_folder_name, width=10),
			tk.Button(frame, text="Create New Folder", font=font, **general_params, command=new_folder)
		)
	)
	elements[0][0].bind("<Button-1>", partial(change_path,
	                                          software_api.recreate_string(software_api.remove_suffix(path,
	                                                                                                  path.endswith("/")).split("/")[:-1], "/")))
	for i in range(len(elements[0])):
		elements[0][i].grid(row=0, column=i)
	del font

	# Fetching all files
	try:
		os.listdir(path)
	except FileNotFoundError:
		path = "ROOT/"

	for filesystem_element in os.listdir(path):

		# Skipping hidden files
		if filesystem_element.startswith("."):
			continue

		# Icons
		if os.path.isdir(path + "/" + filesystem_element):
			extension_formatted = "Folder"
			name = filesystem_element
			file_size = ""

			# Icon
			os.chdir(os.path.dirname(os.path.realpath(__file__)))
			globals()[filesystem_element + "_icon"] = ImageTk.PhotoImage(
				Image.open(app_icon).resize((16, 16))
			)
			os.chdir("../../../")
		else:
			extension_raw = filesystem_element.split(".")[1]
			if extension_raw in ("png", "eps"):
				extension_raw = "paintapp"
			elif extension_raw == "py":
				extension_raw = "settings"

			extension_formatted = extension_raw.upper() + " file"
			name = filesystem_element.split(".")[0]
			file_size = os.path.getsize(path + "/" + filesystem_element)
			size_units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
			size_unit = 0
			while len(str(file_size).split(".")[0]) > 3:
				file_size = float(file_size) / 1024
				size_unit += 1
			file_size = str(round(file_size, 1)) + " " + size_units[size_unit]
			del size_units
			del size_unit

			# Importing the program
			try:
				importlib.import_module("ROOT." + software_api.REGISTRY["SOFTWARES_FOLDER"] + "."
				                        + extension_raw + "." + extension_raw)
			except ModuleNotFoundError:
				extension_raw = "settings"
				importlib.import_module("ROOT." + software_api.REGISTRY["SOFTWARES_FOLDER"] + "."
				                        + extension_raw + "." + extension_raw)

			for i in dir(all_softwares):
				if i.startswith("__"):  # If it is built-in, we just ignore it
					continue
				# We get the attributes of the folder module
				item = getattr(all_softwares, i)
				# We get the real code file
				try:
					app = getattr(item, i)

					os.chdir("ROOT/" + software_api.REGISTRY["SOFTWARES_FOLDER"] + "/"
					         + extension_raw + "/")
					if app.software_dir == extension_raw:
						globals()[filesystem_element + "_icon"] = ImageTk.PhotoImage(
							Image.open(app.app_icon).resize((16, 16))
						)
						os.chdir("../../../")
						break
					os.chdir("../../../")
				except AttributeError:
					continue

		def delete_file(file):
			if os.path.isdir(file):
				shutil.rmtree(file)
			else:
				os.remove(file)
			software_api.notify(software_name, file + " deleted.")
			# Refresh
			change_path(path)

		def rename_file(file, new_name):
			new_name = new_name.get()
			new_name = software_api.remove_prefix(new_name, new_name.startswith(".")\
			                                      or new_name.startswith("_"))
			os.rename(file, software_api.recreate_string(file.split("/")[:-1], "/") + new_name\
			          + "." + extension_raw)
			# Refresh
			change_path(path)

		elements.append(
			(
				tk.Label(frame, image=globals()[filesystem_element + "_icon"], **general_params),
				tk.Label(frame, text=software_api.remove_prefix(name, name.startswith("_")), **general_params),
				tk.Label(frame, text=extension_formatted, **general_params),
				tk.Label(frame, text=file_size, **general_params)
			)
		)
		if not filesystem_element.startswith("_") and path != "ROOT/":
			if "ROOT/"+software_api.REGISTRY["SOFTWARES_FOLDER"] in path or \
				software_api.remove_suffix(path, path.endswith("/")) == "ROOT/"\
					+ software_api.REGISTRY["USERS_FOLDER"]:
				if is_admin is True:
					elements[-1] = list(elements[-1])
					# Delete button
					elements[-1].append(
						tk.Button(frame, text="Delete", command=partial(delete_file, path + "/" + \
							filesystem_element), **general_params)
					)
					# Rename entry
					elements[-1].append(
						tk.Entry(frame, width=10)
					)
					# Rename button
					elements[-1].append(
						tk.Button(frame, text="Rename", command=partial(rename_file, path + "/" + \
						                                                filesystem_element, elements[-1][-1]), **general_params)
					)
					elements[-1] = tuple(elements[-1])
			else:
				elements[-1] = list(elements[-1])
				# Delete button
				elements[-1].append(
					tk.Button(frame, text="Delete", command=partial(delete_file, path + "/" + \
					                                                filesystem_element), **general_params)
				)
				# Rename entry
				elements[-1].append(
					tk.Entry(frame, width=10)
				)
				# Rename button
				elements[-1].append(
					tk.Button(frame, text="Rename", command=partial(rename_file, path + "/" + \
					                                                filesystem_element, elements[-1][-1]), **general_params)
				)
				elements[-1] = tuple(elements[-1])

		def open_app(app, path, event):
			from main import launched_app
			launched_app(app, app.min_size, app.max_size, event)
			app.on_file_open(path)

		if os.path.isdir(path + "/" + filesystem_element):
			elements[-1][1].bind("<Button-1>", partial(change_path,
					software_api.remove_suffix(path, path.endswith("/")) + "/" + name))
		else:
			elements[-1][1].bind("<Button-1>", partial(open_app, app,
			        software_api.remove_suffix(path, path.endswith("/")) + "/" + filesystem_element))

		# Displaying them
		for i in range(len(elements[len(elements) - 1])):
			elements[len(elements) - 1][i].grid(row=len(elements), column=i)
