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

app_icon = "ACOS_Settings.png"
software_name = "Settings"
software_dir = "settings"
is_GUI = True
min_size = None
max_size = None

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

	# Update checker
	def check_updates_launch():
		check_updates()

	update_checker_btn = tk.Button(
		frame,
		text = "Check for updates",
		command = check_updates_launch
	)
	update_checker_btn.grid(row=4, column=0, columnspan=2)

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

def change_registry_value(key:str, var:tk.StringVar, is_string:bool=False, to_int:bool=False):
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
