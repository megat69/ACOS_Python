from .. import software_api
import tkinter as tk
from tkinter import colorchooser
from functools import partial

app_icon = "Colorpicker_Logo.png"
software_name = "Colorpicker"
software_dir = "colorpicker"
is_GUI = True
min_size = (150, 50)
max_size = (150, 50)

def on_app_launch(frame:tk.Frame, width:int=100, height:int=50):
	frame.config(
		bg = software_api.REGISTRY["MAIN_BG_COLOR"][
			software_api.REGISTRY["CURRENT_THEME"]
		]
	)

	globals()["color_var"] = tk.StringVar()
	globals()["color_var"].set("COLOR")

	globals()["main_button"] = tk.Button(
		frame,
		textvariable = globals()["color_var"],
		borderwidth = 0,
		bg=software_api.REGISTRY["MAIN_BG_COLOR"][
			software_api.REGISTRY["CURRENT_THEME"]
		],
		fg=software_api.REGISTRY["MAIN_FG_COLOR"][
			software_api.REGISTRY["CURRENT_THEME"]
		],
		command = partial(ask_color, frame),
		activebackground = software_api.REGISTRY["MAIN_BG_COLOR"][
			software_api.REGISTRY["CURRENT_THEME"]
		]
	)
	globals()["main_button"].pack()

def ask_color(frame):
	color = colorchooser.askcolor()

	if color[0] is None:
		return

	globals()["color_var"].set(color[1])
	globals()["main_button"].config(bg = color[1], activebackground = color[1])
	frame.config(bg = color[1])
	# Choosing font color
	colors = 0
	for element in color[0]:
		colors += element

	if colors > 382:
		globals()["main_button"].config(fg = "black")
	else:
		globals()["main_button"].config(fg="white")
