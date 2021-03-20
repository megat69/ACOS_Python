from .. import software_api
import tkinter as tk
import requests

app_icon = "ACOS_BrowseApps.png"
software_name = "App Browser"
software_dir = "app_browser"
is_GUI = True
min_size = (700, 350)
max_size = None
default_size = None

def on_app_launch(frame:tk.Frame, width:int=100, height:int=100):
	# -------------------- "WINDOW" CREATION --------------------
	browser_frame = tk.Frame(
		frame,
		width=width,
		height=height
	)
	browser_canvas = tk.Canvas(
		browser_frame,
		width = width - 15,
		height = height
	)
	browser_canvas.place(x=0, y=0)

	scrollbar = tk.Scrollbar(browser_frame, orient=tk.VERTICAL, command=browser_canvas.yview)
	scrollbar.place(height=height, x=width-15, y=0)

	browser_canvas.configure(yscrollcommand=scrollbar.set)
	browser_canvas.bind("<Configure>", lambda e: browser_canvas.configure(scrollregion=browser_canvas.bbox("all")))

	main_browser_frame = tk.Frame(
		browser_frame,
		width=width,
		height=height,
		bg = software_api.REGISTRY["MAIN_BG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]]
	)
	browser_canvas.create_window((0, 0),
	    window=main_browser_frame,
		anchor = "nw",
		width = width,
		height = height
	)
	scrollbar.lift()

	# -------------------- MAIN CODE --------------------
	recurrent_params = {
		"bg": software_api.REGISTRY["MAIN_BG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]],
		"fg": software_api.REGISTRY["MAIN_FG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]]
	}
	title = tk.Label(
		main_browser_frame,
		text="App Browser",
		font = ("Impact", 20),
		**recurrent_params
	)
	title.pack()
	subtitle = tk.Label(
		main_browser_frame,
		text="Find your apps in just a second",
		font = ("Impact", 16),
		**recurrent_params
	)
	subtitle.pack()

	main_frame = tk.Frame(
		main_browser_frame,
		width = width,
		height = height,
		bg = software_api.REGISTRY["MAIN_BG_COLOR"][software_api.REGISTRY["CURRENT_THEME"]]
	)

	# -------------------- APPS PLACEMENT --------------------
	unavailable = tk.Label(main_frame, text="Unavailable at the moment", **recurrent_params).grid(row=0, column=0)


	# -------------------- DISPLAYING --------------------
	main_frame.pack()
	browser_frame.grid(row=4, column=0, columnspan=6)
