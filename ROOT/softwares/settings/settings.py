"""
Settings for ACOS.
"""
from .. import software_api
import tkinter as tk
import json
from copy import deepcopy
import requests
import urllib.request
from packaging import version
import zipfile
import os
import importlib
import ROOT.softwares as all_softwares
from PIL import Image, ImageTk
from main import setup_navbar

app_icon = "ACOS_Settings.png"
software_name = "Settings"
software_dir = "settings"
is_GUI = True
min_size = (700, 350)
max_size = None
default_size = None

def on_app_launch(frame:tk.Frame, width:int=100, height:int=100):
	background = "#f0f0f0"
	foreground = software_api.REGISTRY["MAIN_FG_COLOR"]["light"]

	frame.config(
		bg = background
	)

	# Theme dropdown
	theme_label = tk.Label(frame, text="Theme : ", bg=background, fg=foreground)
	theme_label.grid(row=0, column=0, sticky="e")

	theme_value = tk.StringVar()
	theme_value.set(software_api.REGISTRY["CURRENT_THEME"])

	theme_dropdown = tk.OptionMenu(frame, theme_value, "dark", "light")
	theme_dropdown.grid(row=0, column=1, sticky="w")

	def apply_theme():
		change_registry_value("CURRENT_THEME", theme_value)

	theme_button = tk.Button(frame, text="SAVE", command=apply_theme)
	theme_button.grid(row=0, column=2, sticky="w")

	# Status bar position dropdown
	status_bar_position_label = tk.Label(frame, text="Status bar position : ", bg=background, fg=foreground)
	status_bar_position_label.grid(row=4, column=0, sticky="e")

	status_bar_position_value = tk.StringVar()
	status_bar_position_value.set("Top" if software_api.REGISTRY["TOPBAR_POSITION_ON_TOP"] else "Bottom")

	status_bar_position_dropdown = tk.OptionMenu(frame, status_bar_position_value, "Top", "Bottom")
	status_bar_position_dropdown.grid(row=4, column=1, sticky="w")

	def apply_status_bar_position():
		change_registry_value("TOPBAR_POSITION_ON_TOP",
            True if status_bar_position_value.get() == "Top" else False,
            is_string=True
        )

	status_bar_position_button = tk.Button(frame, text="SAVE", command=apply_status_bar_position)
	status_bar_position_button.grid(row=4, column=2, sticky="w")

	# Lang dropdown
	lang_label = tk.Label(frame, text="Lang : ", bg=background, fg=foreground)
	lang_label.grid(row=1, column=0, sticky="e")

	lang_value = tk.StringVar()
	lang_value.set(software_api.REGISTRY["SYSTEM_LANG"])

	lang_dropdown = tk.OptionMenu(frame, lang_value, "fr", "en")
	lang_dropdown.grid(row=1, column=1, sticky="w")

	def apply_lang():
		change_registry_value("SYSTEM_LANG", lang_value)

	lang_button = tk.Button(frame, text="SAVE", command=apply_lang)
	lang_button.grid(row=1, column=2, sticky="w")

	# Icons sizes entry
	icons_sizes_label = tk.Label(frame, text="Icons sizes : ", bg=background, fg=foreground)
	icons_sizes_label.grid(row=2, column=0, sticky="e")

	icons_sizes_value = tk.StringVar()
	icons_sizes_value.set(software_api.REGISTRY["ICONS_SIZES"])

	icons_sizes_entry = tk.Entry(frame, textvariable=icons_sizes_value)
	icons_sizes_entry.grid(row=2, column=1, sticky="w")

	def apply_icons_sizes():
		change_registry_value("ICONS_SIZES", icons_sizes_value, to_int=True)

	icons_sizes_button = tk.Button(frame, text="SAVE", command=apply_icons_sizes)
	icons_sizes_button.grid(row=2, column=2, sticky="w")

	# Navbar size entry
	navbar_size_label = tk.Label(frame, text="Navbar size : ", bg=background, fg=foreground)
	navbar_size_label.grid(row=3, column=0, sticky="e")

	navbar_size_value = tk.StringVar()
	navbar_size_value.set(software_api.REGISTRY["NAVBAR_SIZE"])

	navbar_size_entry = tk.Entry(frame, textvariable=navbar_size_value)
	navbar_size_entry.grid(row=3, column=1, sticky="w")

	def apply_navbar_size():
		change_registry_value("NAVBAR_SIZE", navbar_size_value, to_int=True)

	navbar_size_button = tk.Button(frame, text="SAVE", command=apply_navbar_size)
	navbar_size_button.grid(row=3, column=2, sticky="w")

	# Notification duration entry
	notification_duration_label = tk.Label(frame, text="Notification duration : ", bg=background, fg=foreground)
	notification_duration_label.grid(row=3, column=0, sticky="e")

	notification_duration_value = tk.StringVar()
	notification_duration_value.set(software_api.REGISTRY["NOTIFICATION_STAYING_TIME"])

	notification_duration_entry = tk.Entry(frame, textvariable=notification_duration_value)
	notification_duration_entry.grid(row=3, column=1, sticky="w")

	def apply_notification_duration():
		change_registry_value("NOTIFICATION_STAYING_TIME", notification_duration_value, to_int=True)

	notification_duration_button = tk.Button(frame, text="SAVE", command=apply_notification_duration)
	notification_duration_button.grid(row=3, column=2, sticky="w")

	# ! Taskbar elements
	taskbar_frame = tk.Frame(
		frame,
		width = width,
		height = round(height * 0.3)
	)
	taskbar_canvas = tk.Canvas(
		taskbar_frame
	)
	taskbar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

	scrollbar = tk.Scrollbar(taskbar_frame, orient=tk.VERTICAL, command=taskbar_canvas.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

	taskbar_canvas.configure(yscrollcommand=scrollbar.set)
	taskbar_canvas.bind("<Configure>", lambda e: taskbar_canvas.configure(scrollregion=taskbar_canvas.bbox("all")))

	main_taskbar_frame = tk.Frame(taskbar_frame)
	taskbar_canvas.create_window((0, 0), window = main_taskbar_frame, anchor = "nw")

	userdata = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"]\
					+ "/" + software_api.current_user + "/" + ".userdata.json", "r")
	user_taskbar = json.load(userdata)["taskbar"]
	userdata.close()

	done_apps = []
	iterations = 0
	for software in os.listdir("ROOT/" + software_api.REGISTRY["SOFTWARES_FOLDER"]):
		# Imports the software file
		try:
			importlib.import_module(f"ROOT.{software_api.REGISTRY['SOFTWARES_FOLDER']}.{software}.{software}")
		except ModuleNotFoundError:
			continue
		# Fetches its modules
		for i in dir(all_softwares):
			if i.startswith("__"):  # If it is built-in, we just ignore it
				continue
			# We get the attributes of the folder module
			item = getattr(all_softwares, i)
			# We get the real code file
			try:
				app = getattr(item, i)
			except AttributeError:
				continue

			# Launching MASSIVE try block, if error, it just gets entirely ignored
			try:
				# If we already did the app OR it is not in the user's taskbar
				if app.software_dir in done_apps:
					continue

				# App icon
				globals()[app.software_dir + "_tkimage"] = ImageTk.PhotoImage(
					Image.open(
						f"ROOT/{software_api.REGISTRY['SOFTWARES_FOLDER']}/{app.software_dir}/{app.app_icon}"
					).resize((32, 32))
				)

				globals()[app.software_dir + "_is_checkbox_checked"] = tk.IntVar()
				globals()[app.software_dir + "_is_checkbox_checked"].set(
					0 if app.software_dir not in user_taskbar else 1
				)

				globals()[app.software_dir + "_checkbox"] = tk.Checkbutton(
					main_taskbar_frame,
					variable = globals()[app.software_dir + "_is_checkbox_checked"],
					text = app.software_name
				)
				globals()[app.software_dir + "_checkbox"].grid(
					row = iterations // 2,
					column = 0 if iterations % 2 == 0 else 2
				)

				# Icon
				globals()[app.software_dir + "_icon"] = tk.Label(
					main_taskbar_frame,
					image = globals()[app.software_dir + "_tkimage"]
				)
				globals()[app.software_dir + "_icon"].grid(
					row=iterations // 2,
					column = 1 if iterations % 2 == 0 else 3
				)

				done_apps.append(app.software_dir)

				iterations += 1
			except Exception as e:
				try:
					del globals()["MENU_app_tkimages_" + str(iterations)]
					del globals()["MENU_app_buttons_" + str(iterations) + "_NAME"]
				except:
					pass
				print(e)

	def save_taskbar():
		taskbar_elements = []
		for variable in globals():
			if variable.endswith("_is_checkbox_checked"):
				if globals()[variable].get() == 1:
					taskbar_elements.append(variable.replace("_is_checkbox_checked", "", 1))

		# Dumping it
		userdata = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] \
		                + "/" + software_api.current_user + "/" + ".userdata.json", "r")
		userdata_contents = json.load(userdata)
		userdata.close()
		userdata_contents["taskbar"] = taskbar_elements
		userdata = open("ROOT/" + software_api.REGISTRY["USERS_FOLDER"] \
		                + "/" + software_api.current_user + "/" + ".userdata.json", "w")
		json.dump(userdata_contents, userdata, indent=4)
		userdata.close()

		software_api.notify(software_name, "Taskbar saved !")
		setup_navbar(software_api.__window, software_api.REGISTRY, software_api.current_user, open_startup_apps=False)



	taskbar_save_button = tk.Button(
		main_taskbar_frame,
		text = "SAVE",
		command = save_taskbar
	)
	taskbar_save_button.grid(
		row = iterations,
		column = 0,
		columnspan = 4
	)

	taskbar_frame.grid(row=5, column=0, columnspan=6)

	# Update checker
	def check_updates_launch():
		check_updates()

	update_checker_btn = tk.Button(
		frame,
		text = "Check for updates",
		command = check_updates_launch
	)
	update_checker_btn.grid(row=frame.grid_size()[1], column=0, columnspan=2)

	def install_update_launch():
		install_update()

	globals()["finalize_update_btn"] = tk.Button(
		frame,
		text = "Install update.",
		command = install_update_launch
	)
	globals()["shutdown_text"] = tk.Label(
		frame,
		text = "Please shutdown the system and manually start the 'updater.py' script."
	)

def change_registry_value(key:str, var:(tk.StringVar, str), is_string:bool=False, to_int:bool=False):
	REGISTRY = deepcopy(software_api.REGISTRY)
	if is_string is False:
		try:
			REGISTRY[key] = var.get() if to_int is False else int(var.get())
		except Exception as e:
			print(e)
			return
	else:
		REGISTRY[key] = var

	registry_file = open("registry.json", "w")
	json.dump(REGISTRY, registry_file, indent=4)
	registry_file.close()

	software_api.refresh_registry()

def check_updates():
	# If wifi disabled
	try:
		urllib.request.urlopen('http://google.com')
	except:
		software_api.notify("Settings", "Cannot check updates ; WiFi is disabled.")
		return

	# Check GitHub version
	response = requests.get("https://api.github.com/repos/megat69/ACOS/releases/latest")
	zip_link = response.json()['assets'][0]["browser_download_url"]
	github_version = response.json()["tag_name"]

	# Decide if an update is available on GitHub
	do_update = version.parse(github_version) > version.parse(software_api.os_version)

	if do_update is False:
		software_api.notify("Settings", "No update found.")
		return

	# Notify the user that a new update is available
	software_api.notify("Update available", f"Your version : {software_api.os_version}\n"
	                                        f"GitHub version : {github_version}")
	globals()["finalize_update_btn"].grid(row=5, column=0, columnspan=2)
	globals()["zip_link"] = zip_link

def install_update():
	globals()["finalize_update_btn"].grid_forget()
	zip_link = globals()["zip_link"]
	# Download the update as zip file
	r = requests.get(zip_link)
	existing = r.status_code == 200
	if not existing:
		software_api.notify("Settings", "Update download failed.")
		return

	# Writing the zip
	with open("update.zip", "wb") as code:
		code.write(r.content)
		code.close()

	# Creating a folder for the zip content
	if not os.path.exists("update"):
		os.mkdir("update")
	# Extracting the zip
	with zipfile.ZipFile("update.zip", "r") as zip_ref:
		zip_ref.extractall("update")

	software_api.notify("Update", "System needs to shutdown. Please shutdown "
	                              "the system and manually launch the 'updater.py' script.")
	globals()["shutdown_text"].grid(row=5, column=0, columnspan=2)

def on_file_open(path):
	pass
