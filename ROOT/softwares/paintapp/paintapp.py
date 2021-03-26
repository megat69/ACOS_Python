from .. import software_api
import tkinter as tk
from PIL import Image, EpsImagePlugin
from functools import partial
import os
import json

app_icon = "Paintapp_Logo.png"
software_name = "Paintapp"
software_dir = "paintapp"
is_GUI = True
min_size = (600, 400)
max_size = (900, 500)
default_size = None

# Use vars
color = "#000000"
color_var = tk.StringVar()
color_var.set(color)

dot_size = 3
dot_size_var = tk.IntVar()
dot_size_var.set(dot_size)

nbr_imported_images = 0

os.chdir(os.path.dirname(os.path.realpath(__file__)))
# Translations
if software_api.REGISTRY["SYSTEM_LANG"].lower() == "fr":
	translation_file = open("translations_fr.json", "r", encoding="utf-8")
else:
	translation_file = open("translations_en.json", "r")
TRANSLATIONS = json.load(translation_file)
translation_file.close()

os.chdir("../../../")

def on_app_launch(frame:tk.Frame, width:int=100, height:int=100):
	settings_frame_params = {
		"width": width,
		"height": round(height * 0.2),
		"bg": "#e0e0e0"
	}
	canvas_frame_params = {
		"width": width,
		"height": height - settings_frame_params["height"],
		"bg": "#e0e0e0"
	}
	canvas_size = {
		"width": 300,
		"height": 250
	}

	# ! Creating frames
	settings_frame = tk.Frame(
		frame,
		**settings_frame_params
	)
	canvas_frame = tk.Frame(
		frame,
		**canvas_frame_params
	)

	# ! Creating settings
	# Color definition function
	def change_color():
		globals()["color"] = color_var.get()

	# Color definition entry
	color_definition = tk.Entry(
		settings_frame,
		textvariable = color_var
	)
	color_definition.grid(row=0, column=0)
	validate_color_definition = tk.Button(
		settings_frame,
		text = "->",
		command = change_color
	)
	validate_color_definition.grid(row=0, column=1, sticky="w")

	# Creating function for dot size
	def change_dot_size():
		globals()["dot_size"] = dot_size_var.get()

	# Dot size entry
	dot_size = tk.Entry(
		settings_frame,
		textvariable=dot_size_var
	)
	dot_size.grid(row=1, column=0)
	validate_dot_size = tk.Button(
		settings_frame,
		text="->",
		command=change_dot_size
	)
	validate_dot_size.grid(row=1, column=1, sticky="w")

	# Import image
	import_image_path_var = tk.StringVar()
	import_image_path = tk.Entry(
		settings_frame,
		textvariable = import_image_path_var
	)
	import_image_path.grid(
		row = 0,
		column = 2,
		columnspan = 2
	)
	import_image_button = tk.Button(
		settings_frame,
		text = TRANSLATIONS["Import"],
		command = partial(import_image, import_image_path_var)
	)
	import_image_button.grid(
		row = 1,
		column = 3,
		sticky="w"
	)

	# ! Creating drawable zone
	globals()["main_canvas"] = tk.Canvas(
		canvas_frame,
		highlightthickness = 2,
		bg = "white",
		**canvas_size
	)
	globals()["main_canvas"].bind("<B1-Motion>", display)
	globals()["main_canvas"].pack(anchor="center")

	# Canvas size
	canvas_width_var = tk.IntVar()
	canvas_width_var.set(canvas_size["width"])
	canvas_width = tk.Entry(
		settings_frame,
		textvariable=canvas_width_var,
		width = 10
	)
	canvas_width.grid(row=0, column=4)
	canvas_height_var = tk.IntVar()
	canvas_height_var.set(canvas_size["height"])
	canvas_height = tk.Entry(
		settings_frame,
		textvariable=canvas_height_var,
		width = 10
	)
	canvas_height.grid(row=0, column=5)
	canvas_size_apply = tk.Button(
		settings_frame,
		text = TRANSLATIONS["Apply"],
		command = partial(apply_canvas_size, canvas_width_var, canvas_height_var)
	)
	canvas_size_apply.grid(row=1, column=4, columnspan=2)

	# ! Creating save button
	save_button = tk.Button(
		settings_frame,
		text = TRANSLATIONS["Save"],
		command = partial(getter, globals()["main_canvas"], import_image_path_var)
	)
	save_button.grid(row = 1, column = 2, sticky = "e")

	# ! Reset canvas button
	def reset_canvas():
		globals()["main_canvas"].delete("all")

	reset_canvas_button = tk.Button(
		settings_frame,
		text = TRANSLATIONS["Reset"],
		command = reset_canvas
	)
	reset_canvas_button.grid(
		row = 0,
		column = 6,
		rowspan = 2
	)

	# ! Placing the frames
	settings_frame.place(
		x = 0,
		y = 0,
		width = settings_frame_params["width"],
		height = settings_frame_params["height"]
	)
	canvas_frame.place(
		x = 0,
		y = settings_frame_params["height"]
	)

def display(event):
	global color
	global dot_size
	# Coordinates.
	x1, y1, x2, y2 = (event.x - dot_size), (event.y - dot_size), (event.x + dot_size), (event.y + dot_size)

	# specify type of display
	globals()["main_canvas"].create_arc(
		x1,
		y1,
		x2,
		y2,
		fill = color,
		outline = color
	)

def getter(widget, filename):
	"""
	Grabs the image and saves it.
	"""
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	filename = filename.get()  # Because it is a StringVar

	# Setting the ghostscript location
	EpsImagePlugin.gs_windows_binary = r'gs9.53.3/bin/gswin64c.exe'
	EpsImagePlugin.gs_linux_binary = r'gs9.53.3/bin/gs-9533-linux-x86_64.exe'

	# Path to the saving directory
	path = f"../../{software_api.REGISTRY['USERS_FOLDER']}/{software_api.current_user}"\
			     f"/_images/_{software_dir}/"

	# If it doesn't exits, we create all the needed folders
	if not os.path.exists(path):
		try:
			os.mkdir(f"../../{software_api.REGISTRY['USERS_FOLDER']}/{software_api.current_user}/_images")
		except:
			pass
		try:
			os.mkdir(f"../../{software_api.REGISTRY['USERS_FOLDER']}/{software_api.current_user}/_images/_{software_dir}")
		except:
			pass

	# Saving as EPS
	widget.postscript(file = path + filename.replace("../", "") + '.eps')

	# Exporting as PNG
	img = Image.open(path + filename.replace("../", "") + '.eps')
	img.save(path + filename.replace("../", "") + '.png', 'png')

	# Trying to remove the EPS image
	try:
		os.remove(filename + ".eps")
	except:
		pass

	software_api.notify(
		software_name, "Saved image to " \
               + path.replace("../", "").replace(software_api.REGISTRY["USERS_FOLDER"], "", 1)\
		               +filename.replace("../", "")+".png"
	)

	os.chdir("../../../")

def import_image(path):
	global nbr_imported_images
	os.chdir(os.path.dirname(os.path.realpath(__file__)))

	path_content = path.get() if not isinstance(path, str) else path

	# Import the image
	try:
		globals()["imported_image_"+str(nbr_imported_images)] = tk.PhotoImage(
			file=f"../../{software_api.REGISTRY['USERS_FOLDER']}/{software_api.current_user}"
			     f"/_images/_{software_dir}/" + path_content.replace("../", "")
		)
	except Exception as e:
		print(path)
		try:
			path.set(TRANSLATIONS["UnableLoadImage"] + " " + path_content)
		except:
			pass
		software_api.notify(software_name, f"Unable to load the image {path_content}")
		print(e)
		return None

	# Displays the image
	globals()["main_canvas"].create_image(
		0,
		0,
		image=globals()["imported_image_"+str(nbr_imported_images)],
		anchor = "nw"
	)
	globals()["main_canvas"].pack_forget()
	globals()["main_canvas"].pack()

	# Increments the number of imported images
	nbr_imported_images += 1

	software_api.notify(software_name, "Imported image")

	os.chdir("../../../")

def apply_canvas_size(width, height):
	width = width.get()
	height = height.get()
	globals()["main_canvas"].config(
		width = width,
		height = height
	)

def on_file_open(path):
	import_image(path.split("/")[-1])
