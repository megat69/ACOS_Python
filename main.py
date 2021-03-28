import importlib
import json
import os
import platform
import shutil
import sys
import tkinter as tk
from functools import partial
from math import isclose
from random import randint
from tkinter import filedialog
import psutil
import datetime

from PIL import Image, ImageTk

import ROOT.softwares as all_softwares
import blend_tools
import hash_utility

# Init of lang
lang = "en"
language_file = open("SYSTEM_LANG_EN.json")
TRANSLATIONS = json.load(language_file)
language_file.close()
root = None
opened_apps_amount = 0

usage_file = open("general_data.json", "r", encoding="utf-8")
GENERAL_DATA = json.load(usage_file)
usage_file.close()

def set_locale(locale: str):
	"""
	Sets the system language.
	"""
	global lang
	global TRANSLATIONS
	lang = locale.upper()
	language_file = open(f"SYSTEM_LANG_{lang}.json", "r", encoding="utf-8")
	TRANSLATIONS = json.load(language_file)
	language_file.close()

def ThrowBSOD(window: tk.Tk, message=""):
	"""
	Throws the BSOD and exits.
	"""
	# ------------------ WIDGET DESTRUCTION ------------------
	destroy_all_widgets(window)

	# ------------------ BSOD DISPLAYING ------------------
	BSOD_COLOR = "#0071FF"
	window["bg"] = BSOD_COLOR
	window.geometry("1024x512")
	main_label = tk.Label(
		window,
		text=TRANSLATIONS["BSOD"]["SysError"],
		font=("Impact", 36),
		bg=BSOD_COLOR,
		fg="white"
	)
	main_label.place(
		x=40,
		y=40
	)
	message_label = tk.Label(
		window,
		text=TRANSLATIONS["BSOD"][message] if message in TRANSLATIONS.keys() else message,
		font=("Impact", 18),
		bg=BSOD_COLOR,
		fg="white"
	)
	message_label.place(
		x=40,
		y=180
	)
	reboot_label = tk.Label(
		window,
		text=TRANSLATIONS["BSOD"]["RebootMsg"],
		font=("Impact", 24),
		bg=BSOD_COLOR,
		fg="white"
	)
	reboot_label.place(
		x=40,
		y=300
	)

	def exit_fx():
		sys.exit(1)

	window.title("BSOD")
	window.protocol("WM_DELETE_WINDOW", exit_fx)
	window.mainloop()

def get_all_widgets(window):
	_list = window.winfo_children()

	for item in _list:
		if item.winfo_children():
			_list.extend(item.winfo_children())

	return _list

def destroy_all_widgets(window: tk.Tk):
	"""
	Destroys all widgets in given window.
	"""
	widget_list = get_all_widgets(window)
	for item in widget_list:
		try:
			item.place_forget()
		except:
			try:
				item.grid_forget()
			except:
				item.pack_forget()
		item.destroy()

def corrupted_key(key, general_data: bool = False):
	return TRANSLATIONS["BSOD"]["CorruptedKey"].format(key=key) + \
	       ("\n" + TRANSLATIONS["BSOD"]["GeneralDataKey"] if general_data is True else "")

def start_OS(window: tk.Tk, REGISTRY: dict):
	"""
	Starts the OS.
	"""
	globals()["REGISTRY"] = REGISTRY
	# ------------------ DEFINING THEME ------------------
	try:
		globals()["current_theme"] = REGISTRY["CURRENT_THEME"]
	except:
		ThrowBSOD(window, corrupted_key("CURRENT_THEME"))

	if globals()["current_theme"] not in ("light", "dark"):
		globals()["current_theme"] = "light"

	# ------------------ SETTING BACKGROUND ------------------
	try:
		window["bg"] = REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]]
	except:
		ThrowBSOD(window, corrupted_key("MAIN_BG_COLOR"))

	# ------------------ USER LOGIN ------------------
	users_list = []
	# Displaying the users
	i = 0
	for user in os.listdir(f"ROOT/{REGISTRY['USERS_FOLDER']}/"):
		users_list.append(
			tk.Button(
				window,
				text=user,
				borderwidth=0,
				command=partial(select_user, user, window, REGISTRY),
				bg=REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]],
				fg=REGISTRY["MAIN_FG_COLOR"][globals()["current_theme"]],
				font=("Calibri Light", 20)
			)
		)
		users_list[-1].place(
			x=2,
			y=window.winfo_height() - (32 * (i + 1)),
			height=32
		)
		i += 1
	del i

	# Displaying the latest connected user at the middle of the screen
	try:
		last_connected_user = GENERAL_DATA["last_connected_user"]
	except:
		ThrowBSOD(window, corrupted_key("last_connected_user", general_data=True))
	globals()["user"] = last_connected_user

	globals()["username_label"] = tk.Label(
		window,
		text=last_connected_user,
		font=("Calibri Light", 26),
		fg=REGISTRY["MAIN_FG_COLOR"][globals()["current_theme"]],
		bg=REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]]
	)
	globals()["username_label"].place(
		x=window.winfo_width() // 2 - (len(last_connected_user) // 2 * 12),
		y=window.winfo_height() // 2 - 26
	)

	# Displaying the ACOS logo on top of it
	globals()["user_logo_canvas"] = tk.Canvas(
		window,
		width=128,
		height=128,
		bg=REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]],
		bd=0,
		highlightthickness=0,
		relief='ridge'
	)
	globals()["user_logo_canvas"].place(
		x=window.winfo_width() // 2 - 32 * 1.5,
		y=window.winfo_height() // 2 - 128 * 1.5
	)

	userdata = get_userdata(window, last_connected_user, REGISTRY)

	if "USERS_FOLDER" not in REGISTRY.keys():
		ThrowBSOD(window, corrupted_key("USERS_FOLDER"))
	elif "USERDATA_NAME" not in REGISTRY.keys():
		ThrowBSOD(window, corrupted_key("USERDATA_NAME"))
	elif "ProfileImage" not in userdata.keys():
		globals()["user_logo"] = ImageTk.PhotoImage(
			Image.open(
				REGISTRY["LOGO_PATH"]
			).resize((128, 128))
		)
	else:
		globals()["user_logo"] = ImageTk.PhotoImage(
			Image.open(
				f"ROOT/"
				f"{REGISTRY['USERS_FOLDER']}/"
				f"{last_connected_user}/"
				f"{REGISTRY['USERDATA_NAME']}/"
				f"{userdata['ProfileImage']}"
			).resize((128, 128), Image.NEAREST)
		)

	globals()["user_logo_canvas"].create_image(
		0,
		0,
		image=globals()["user_logo"],
		anchor="nw"
	)

	# Password field
	globals()["password_field"] = tk.Entry(
		window,
		show="*"  # TODO : ECOLEDIRECTE APP -> USES ECOLEDIRECTE API
	)

	if globals()["current_theme"] == "dark":  # Dark theme modifiers
		globals()["password_field"].config(
			bg="#404040",
			fg="white",
			insertbackground="white"
		)

	globals()["password_field"].place(
		x=window.winfo_width() // 2 - 32 * 1.4,
		y=window.winfo_height() // 2 + 32,
		width=128,
		height=24
	)
	# And send button
	globals()["password_send_button"] = tk.Button(
		window,
		text="->",
		font=("JetBrains Mono", 16),
		command=partial(compute_password, "password_field", window),
		borderwidth=0
	)

	if globals()["current_theme"] == "dark":  # Dark theme modifiers
		globals()["password_send_button"].config(
			bg="#404040",
			fg="white"
		)

	globals()["password_send_button"].place(
		x=window.winfo_width() // 2 - 32 * 1.4 + 128,
		y=window.winfo_height() // 2 + 32,
		height=24
	)

	import ROOT.softwares.software_api
	ROOT.softwares.software_api.__set_window(window)

def compute_password(entry_name: str, window: tk.Tk):
	"""
	Computes the password in the given entry.
	"""
	# Gets the given pass
	given_pass = globals()[entry_name].get()
	user = globals()["user"]

	# Checks the password
	if hash_utility.check_password(
			given_pass,
			"json",
			file=f"ROOT/"
			     f"{globals()['REGISTRY']['USERS_FOLDER']}/"
			     f"{user}/"
			     f".userdata.json",
			key="PASSWORD"
	):
		# Destroying all widgets
		destroy_all_widgets(window)
		# ------------------ MODIFYING LAST CONNECTED USER ------------------
		general_data_file = open("general_data.json", "r")
		general_data = json.load(general_data_file)
		general_data_file.close()
		general_data["last_connected_user"] = user
		general_data_file = open("general_data.json", "w")
		json.dump(general_data, general_data_file, indent=4)
		general_data_file.close()

		# ------------------ SETUP NAVBAR ------------------
		setup_topbar(window, globals()["REGISTRY"])
		setup_navbar(window, globals()["REGISTRY"], user)
		setup_desktop(window, globals()["REGISTRY"], user)
	else:
		incorrect_password_label = tk.Label(
			window,
			text=globals()["TRANSLATIONS"]["LOGIN"]["IncorrectPassword"],
			fg="red",
			bg=globals()["REGISTRY"]["MAIN_BG_COLOR"][globals()["current_theme"]]
		)
		incorrect_password_label.place(
			x=window.winfo_width() // 2 \
			  - len(globals()["TRANSLATIONS"]["LOGIN"]["IncorrectPassword"]),
			y=window.winfo_height() // 2 + 96
		)

def get_userdata(window, user, REGISTRY):
	try:
		userdata_file = open(
			f"ROOT/{REGISTRY['USERS_FOLDER']}/{globals()['user']}/{REGISTRY['USERDATA_NAME']}.json",
			"r",
			encoding="utf-8"
		)
		userdata = json.load(userdata_file)
		userdata_file.close()
		return userdata
	except Exception as e:
		ThrowBSOD(window, f"Unknown exception : {e}")

def select_user(user, window, REGISTRY):
	"""
	Selects an user.
	"""
	# Username
	globals()["username_label"].config(text=user)
	globals()["username_label"].place_forget()
	globals()["username_label"].place(
		x=window.winfo_width() // 2 - (len(user) // 2 * 11),
		y=window.winfo_height() // 2 - 26
	)

	# Userdata
	userdata = get_userdata(window, user, REGISTRY)

	# Logo
	globals()["user_logo"] = ImageTk.PhotoImage(
		Image.open(
			f"ROOT/"
			f"{REGISTRY['USERS_FOLDER']}/"
			f"{user}/"
			f"{REGISTRY['USERDATA_NAME']}/"
			f"{userdata['ProfileImage']}"
		).resize((128, 128))
	)

	globals()["user_logo_canvas"].create_image(
		0,
		0,
		image=globals()["user_logo"],
		anchor="nw"
	)

	globals()["user"] = user

def setup_navbar(window, REGISTRY, user, open_startup_apps: bool = True):
	"""
	Sets the navbar up
	"""
	try:
		background = REGISTRY["NAVBAR_BG_COLOR"][globals()["current_theme"]]
	except:
		ThrowBSOD(window, corrupted_key("NAVBAR_BG_COLOR"))

	try:
		navbar_size = REGISTRY["NAVBAR_SIZE"]
	except:
		ThrowBSOD(window, corrupted_key("NAVBAR_SIZE"))

	navbar_frame = tk.Frame(
		window,
		bg=background
	)

	# ------------------ NAVBAR ELEMENTS ------------------
	done_apps = []
	user_taskbar = get_userdata(window, user, REGISTRY)["taskbar"]
	startup_apps = get_userdata(window, user, REGISTRY)["startup_apps"]

	if "SOFTWARES_FOLDER" not in REGISTRY:
		ThrowBSOD(window, corrupted_key("SOFTWARES_FOLDER"))

	iterations = 0

	for software in user_taskbar:
		# Imports the software file
		try:
			importlib.import_module(f"ROOT.{REGISTRY['SOFTWARES_FOLDER']}.{software}.{software}")
		except ModuleNotFoundError as e:
			print("Module not found :", e)
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
				if app.software_dir in done_apps or app.software_dir not in user_taskbar:
					continue

				globals()["app_tkimages_" + str(iterations)] = \
					ImageTk.PhotoImage(
						Image.open(
							f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}/{app.software_dir}/{app.app_icon}"
						).resize(
							(
								int(round(navbar_size * 0.85)),
								int(round(navbar_size * 0.85))
							)
						)
					)

				globals()["app_buttons_" + str(iterations)] = \
					tk.Canvas(
						navbar_frame,
						highlightthickness=0,
						bg=background,
						width=navbar_size,
						height=navbar_size
					)
				globals()["app_buttons_" + str(iterations)].create_image(
					0,
					0,
					image=globals()["app_tkimages_" + str(iterations)],
					anchor="nw"
				)
				globals()["app_buttons_" + str(iterations)].bind("<ButtonPress-1>", partial(
					launched_app, app, app.min_size, app.max_size
				))

				globals()["app_buttons_" + str(iterations)].pack(padx=5)

				if app.software_dir in startup_apps and open_startup_apps is True:
					globals()["navbar_size"] = navbar_size
					window.after(1000, launched_app, app, app.min_size, app.max_size, None)

				done_apps.append(app.software_dir)

				iterations += 1
			except Exception as e:
				try:
					del globals()["app_tkimages_" + str(iterations)]
					del globals()["app_buttons_" + str(iterations)]
				except:
					pass
				print("Error :", e)

	# del iterations

	# ------------------ FINAL NAVBAR PLACING ------------------
	try:
		navbar_frame.place(
			x=0,
			y=navbar_size,
			width=navbar_size,
			height=REGISTRY["WIN_HEIGHT"] - navbar_size if REGISTRY["FULLSCREEN_ENABLED"] is False else window.winfo_screenheight() - navbar_size,
		)
	except:  # If there is a problem with the registry key
		ThrowBSOD(window, corrupted_key("FULLSCREEN_ENABLED"))

	# ------------------ ACOS Menu PLACING ------------------
	globals()["ACOS_Menu_icon"] = ImageTk.PhotoImage(
		Image.open(
			REGISTRY["LOGO_PATH"]
		).resize(
			(
				round(navbar_size * 0.9),
				round(navbar_size * 0.9)
			)
		)
	)
	ACOS_Menu_button = tk.Canvas(
		window,
		highlightthickness=0,
		bg=REGISTRY["NAVBAR_BG_COLOR"][globals()["current_theme"]],
		width=navbar_size,
		height=navbar_size
	)
	ACOS_Menu_button.bind("<ButtonPress-1>", ACOS_Menu_click)
	ACOS_Menu_button.create_image(
		0,
		0,
		image=globals()["ACOS_Menu_icon"],
		anchor="nw"
	)
	ACOS_Menu_button.place(
		x=0,
		y=0,
		width=navbar_size,
		height=navbar_size
	)

	globals()["navbar_size"] = navbar_size
	globals()["root"] = window

def setup_topbar(window, REGISTRY):
	"""
	Sets the topbar with the system information (date, time, WiFi info, battery...)
	"""
	try:
		navbar_size = REGISTRY["NAVBAR_SIZE"]
	except:
		ThrowBSOD(window, corrupted_key("NAVBAR_SIZE"))

	# Create the frame
	globals()["topbar_frame"] = tk.Frame(
		window,
		bg=REGISTRY["NAVBAR_BG_COLOR"][REGISTRY["CURRENT_THEME"]]
	)

	try:
		topbar_spacing = REGISTRY["SPACING_BETWEEN_TOPBAR_ELEMENTS"]
	except:
		ThrowBSOD(window, corrupted_key("SPACING_BETWEEN_TOPBAR_ELEMENTS"))

	def get_date():
		# Getting the date
		date = datetime.datetime.now()
		try:
			date = date.strftime(REGISTRY["DATETIME_FORMAT"])
		except:
			ThrowBSOD(window, corrupted_key("DATETIME_FORMAT"))
		return date

	def set_date():
		globals()["topbar_datetime"].config(text=get_date())

	def set_date_loop():
		set_date()
		window.after(1000, set_date_loop)

	# Placing the date and time
	globals()["topbar_datetime"] = tk.Label(
		globals()["topbar_frame"],
		text=get_date(),
		bg=REGISTRY["NAVBAR_BG_COLOR"][REGISTRY["CURRENT_THEME"]],
		fg=REGISTRY["MAIN_FG_COLOR"][REGISTRY["CURRENT_THEME"]]
	)
	globals()["topbar_datetime"].pack(side=tk.RIGHT)

	# Making it update
	window.after(1000, set_date_loop)

	# Battery displaying
	def get_battery_string():
		battery = psutil.sensors_battery()
		return f"{battery.percent}%{', Charging' if battery.power_plugged else ''}"

	def set_battery_string():
		globals()["topbar_battery_status"].config(text=get_battery_string())
		window.after(10000, set_battery_string)

	globals()["topbar_battery_status"] = tk.Label(
		globals()["topbar_frame"],
		text=get_battery_string(),
		bg=REGISTRY["NAVBAR_BG_COLOR"][REGISTRY["CURRENT_THEME"]],
		fg=REGISTRY["MAIN_FG_COLOR"][REGISTRY["CURRENT_THEME"]]
	)
	globals()["topbar_battery_status"].pack(side=tk.RIGHT, padx=topbar_spacing)

	# Disabled display for processor and RAM usage
	"""# Processor displaying
	def set_processor_string():
		globals()["topbar_processor_status"].config(text=psutil.cpu_percent())
		window.after(10000, set_processor_string)

	globals()["topbar_processor_status"] = tk.Label(
		globals()["topbar_frame"],
		text=psutil.cpu_percent(),
		bg=REGISTRY["NAVBAR_BG_COLOR"][REGISTRY["CURRENT_THEME"]],
		fg=REGISTRY["MAIN_FG_COLOR"][REGISTRY["CURRENT_THEME"]]
	)
	globals()["topbar_processor_status"].pack(side=tk.RIGHT, padx=topbar_spacing)

	# RAM Usage
	def set_RAM_string():
		globals()["topbar_RAM_status"].config(text=psutil.Process(os.getpid()).memory_info().rss)
		window.after(10000, set_RAM_string)

	globals()["topbar_RAM_status"] = tk.Label(
		globals()["topbar_frame"],
		text=psutil.Process(os.getpid()).memory_info().rss,
		bg=REGISTRY["NAVBAR_BG_COLOR"][REGISTRY["CURRENT_THEME"]],
		fg=REGISTRY["MAIN_FG_COLOR"][REGISTRY["CURRENT_THEME"]]
	)
	globals()["topbar_RAM_status"].pack(side=tk.RIGHT, padx=topbar_spacing)"""

	# Finally placing the topbar
	try:
		topbar_position = REGISTRY["TOPBAR_POSITION_ON_TOP"]
	except:
		ThrowBSOD(window, corrupted_key("TOPBAR_POSITION_ON_TOP"))

	globals()["topbar_frame"].place(
		x=navbar_size,
		y=0 if topbar_position is True else window.winfo_height() - (navbar_size // 4),
		width=window.winfo_width() - navbar_size,
		height=navbar_size // 4
	)

def setup_desktop(window, REGISTRY, user, lift_others: bool = False):
	"""
	Setups the user desktop.
	"""
	desktop_files = os.listdir(f"ROOT/{REGISTRY['USERS_FOLDER']}/{user}/_desktop/")
	globals()["desktop"] = tk.Frame(window, bg=REGISTRY["MAIN_BG_COLOR"][REGISTRY["CURRENT_THEME"]])

	iterations = 0

	def open_app(app, path, event):
		launched_app(app, app.min_size, app.max_size, event)
		app.on_file_open(path)

	# Splitting the files
	for file in desktop_files:
		# Getting file info
		extension_raw = file.split(".")[1]
		if extension_raw == "png":
			extension_raw = "paintapp"
		displayed_extension = extension_raw.upper()
		filename = file.split(".")[0]

		for i in dir(all_softwares):
			if i.startswith("__"):  # If it is built-in, we just ignore it
				continue
			# We get the attributes of the folder module
			item = getattr(all_softwares, i)
			# We get the real code file
			try:
				app = getattr(item, i)

				os.chdir("ROOT/" + REGISTRY["SOFTWARES_FOLDER"] + "/"
				         + extension_raw + "/")
				if app.software_dir == extension_raw:
					globals()["desktop_" + extension_raw + "_icon_" + str(iterations)] = ImageTk.PhotoImage(
						Image.open(app.app_icon).resize((REGISTRY["NAVBAR_SIZE"], REGISTRY["NAVBAR_SIZE"]))
					)
					os.chdir("../../../")
					break
				os.chdir("../../../")
			except AttributeError:
				continue

		# Try to import the opening program
		try:
			importlib.import_module("ROOT." + REGISTRY["SOFTWARES_FOLDER"] + "."
			                        + extension_raw + "." + extension_raw)
		except ModuleNotFoundError:
			extension_raw = "settings"
			importlib.import_module("ROOT." + REGISTRY["SOFTWARES_FOLDER"] + "."
			                        + extension_raw + "." + extension_raw)

		# Displaying the file on the desktop, through a grid
		try:
			globals()[f"desktop_{filename}_icon"] = tk.Label(
				globals()["desktop"],
				image=globals()["desktop_" + extension_raw + "_icon_" + str(iterations)],
				bg=REGISTRY["MAIN_BG_COLOR"][REGISTRY["CURRENT_THEME"]]
			)
		except KeyError:
			globals()[f"desktop_{filename}_icon_" + str(iterations)] = tk.Label(
				globals()["desktop"],
				image=globals()["ACOS_Menu_icon_" + str(iterations)],
				bg=REGISTRY["MAIN_BG_COLOR"][REGISTRY["CURRENT_THEME"]]
			)
		if "DESKTOP_FONT" not in REGISTRY:
			ThrowBSOD(window, corrupted_key("DESKTOP_FONT"))
		globals()[f"desktop_{filename}_label"] = tk.Label(
			globals()["desktop"],
			text=filename,
			bg=REGISTRY["MAIN_BG_COLOR"][REGISTRY["CURRENT_THEME"]],
			fg=REGISTRY["MAIN_FG_COLOR"][REGISTRY["CURRENT_THEME"]],
			font=tuple(REGISTRY["DESKTOP_FONT"])
		)

		# Binding the click to the app opening
		path = "ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + user + "/"
		globals()[f"desktop_{filename}_label"].bind("<Button-1>", partial(open_app, app,
		                                                                  remove_suffix(path, path.endswith("/")) + "/_desktop/" + file))
		globals()[f"desktop_{filename}_icon"].bind("<Button-1>", partial(open_app, app,
		                                                                 remove_suffix(path, path.endswith("/")) + "/_desktop/" + file))

		globals()[f"desktop_{filename}_icon"].grid(
			row=iterations - (iterations // 8 * 8),
			column=iterations // 8
		)
		globals()[f"desktop_{filename}_label"].grid(
			row=iterations - (iterations // 8 * 8) + 1,
			column=iterations // 8
		)

		iterations += 2

	globals()["desktop"].place(
		x=REGISTRY["NAVBAR_SIZE"],
		y=REGISTRY["NAVBAR_SIZE"] // 4,
		width=window.winfo_width() - REGISTRY["NAVBAR_SIZE"],
		height=window.winfo_height() - REGISTRY["NAVBAR_SIZE"] // 4
	)

	# Lifting the other apps if the desktop has been reset
	if lift_others is True:
		for variable in globals():
			if variable.startswith("frame_"):
				try:
					globals()[variable].lift()
				except Exception:
					pass

def launched_app(app, min_size, max_size, event):
	"""
	Attributes a frame to the app, and launches it.
	"""
	window = globals()["root"]
	global opened_apps_amount

	# Finds a new process name for the app
	instance = 0
	while f"frame_{app.software_dir}_{instance}" in globals():
		instance += 1

	background_color = globals()["REGISTRY"]["APP_FRAME_BACKGROUND_COLOR"]

	# Creates the frame
	globals()[f"frame_{app.software_dir}_{instance}"] = tk.Frame(
		window,
		bg=background_color
	)

	def Lift(event):
		"""
		Lifts the frame on top.
		"""
		globals()[f"frame_{app.software_dir}_{instance}"].lift()

	globals()[f"{app.software_dir}_{instance}_last_coords"] = \
		(randint(
			globals()["navbar_size"],
			round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_WIDTH"] * 0.25)
		), randint(
			globals()["navbar_size"],
			round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_HEIGHT"] * 0.25)
		)
		)

	def Drag(event):
		"""
		Generates the dragging of the window.
		"""
		x = event.x + (globals()[f"frame_{app.software_dir}_{instance}"].winfo_width() // 2)
		y = event.y + (globals()[f"frame_{app.software_dir}_{instance}"].winfo_height() // 2)

		if isclose(globals()[f"{app.software_dir}_{instance}_last_coords"][0],
			x, rel_tol=5) and isclose(globals()[f"{app.software_dir}_{instance}_last_coords"][1],
			y, rel_tol=5):

			globals()[f"frame_{app.software_dir}_{instance}"].place(
				x=x,
				y=y
			)

			globals()[f"{app.software_dir}_{instance}_last_coords"] = (x, y)

	globals()[f"frame_{app.software_dir}_{instance}"].bind('<B1-Motion>', Drag)
	globals()[f"frame_{app.software_dir}_{instance}"].bind('<Button-1>', Lift)

	# Generates the icon
	icon_size = globals()["REGISTRY"]["ICONS_SIZES"]

	globals()["app_icon_" + str(opened_apps_amount)] = ImageTk.PhotoImage(
		Image.open(
			f"ROOT/{globals()['REGISTRY']['SOFTWARES_FOLDER']}/{app.software_dir}/{app.app_icon}"
		).resize(
			(icon_size, icon_size)
		)
	)

	app_icon_label = tk.Label(
		globals()[f"frame_{app.software_dir}_{instance}"],
		image=globals()["app_icon_" + str(opened_apps_amount)],
		bg=background_color
	)
	app_icon_label.place(
		x=2,
		y=2,
		width=icon_size,
		height=icon_size
	)

	# Creates and places the app title
	app_title = tk.Label(
		globals()[f"frame_{app.software_dir}_{instance}"],
		text=app.software_name,
		bg=background_color,
		fg=globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
	)
	app_title.place(
		x=icon_size + 2,
		y=0
	)

	def quit_app(app):
		globals()[f"frame_{app.software_dir}_{instance}"].place_forget()
		globals()[f"frame_{app.software_dir}_{instance}"].destroy()

	def expand_app(app, software_dir):
		"""
		Expands the app.
		"""
		nonlocal parent_width
		nonlocal parent_height
		parent_width = window.winfo_width() - globals()["REGISTRY"]["NAVBAR_SIZE"]
		parent_height = window.winfo_height() - globals()["REGISTRY"]["NAVBAR_SIZE"] // 4
		globals()[app].place(
			x=globals()["REGISTRY"]["NAVBAR_SIZE"],
			y=globals()["REGISTRY"]["NAVBAR_SIZE"] // 4,
			width=parent_width,
			height=parent_height
		)
		globals()[app + "_MAIN"].place(
			x=4,
			y=icon_size + 4,
			width=parent_width - 8,
			height=parent_height - icon_size - 8
		)
		globals()[f"frame_{software_dir}_{instance}_resizeable_frame"].place(
			x=parent_width - 8,
			y=parent_height - 8,
			width=8,
			height=8
		)
		quit_button.place(
			x=parent_width - icon_size - 2,
			y=2,
			height=icon_size,
			width=icon_size
		)
		try:
			expand_button.place(
				x=parent_width - icon_size * 2 - 4,
				y=4,
				height=icon_size,
				width=icon_size
			)
		except:
			pass

	# Creates the width of the app frame
	if app.default_size is None:
		parent_width = randint(
			round(globals()["REGISTRY"]["WIN_WIDTH"] * 0.5),
			round(globals()["REGISTRY"]["WIN_WIDTH"] * 0.7)
		)

		# If it doesn't match the app requirements
		if min_size is not None and min_size[0] > parent_width:
			parent_width = min_size[0]
		elif max_size is not None and max_size[0] < parent_width:
			parent_width = max_size[0]
		parent_height = randint(
			round(globals()["REGISTRY"]["WIN_HEIGHT"] * 0.5),
			round(globals()["REGISTRY"]["WIN_HEIGHT"] * 0.7)
		)
		# If it doesn't match the app requirements
		if min_size is not None and min_size[1] > parent_height:
			parent_height = min_size[1]
		elif max_size is not None and max_size[1] < parent_height:
			parent_height = max_size[1]
	else:
		parent_width, parent_height = app.default_size

	# Quit icon
	globals()["quit_icon_" + str(opened_apps_amount)] = ImageTk.PhotoImage(
		Image.open("assets/ACOS_Bin.png").resize((16, 16))
	)
	# Expand icon
	globals()["expand_icon_" + str(opened_apps_amount)] = ImageTk.PhotoImage(
		Image.open("assets/ACOS_Expand.png").resize((16, 16))
	)

	# Creates the quit button
	quit_button = tk.Button(
		globals()[f"frame_{app.software_dir}_{instance}"],
		image=globals()["quit_icon_" + str(opened_apps_amount)],
		borderwidth=0,
		command=partial(quit_app, app),
		bg=background_color,
		activebackground=background_color
	)
	quit_button.place(
		x=parent_width - icon_size - 2,
		y=2,
		height=icon_size,
		width=icon_size
	)

	# Creates the expand button
	if app.max_size is None:
		expand_button = tk.Button(
			globals()[f"frame_{app.software_dir}_{instance}"],
			image=globals()["expand_icon_" + str(opened_apps_amount)],
			borderwidth=0,
			command=partial(expand_app, f"frame_{app.software_dir}_{instance}", app.software_dir),
			bg=background_color,
			activebackground=background_color
		)
		expand_button.place(
			x=parent_width - icon_size * 2 - 4,
			y=4,
			height=icon_size,
			width=icon_size
		)

	# Creates a new MAIN frame inside the app frame
	globals()[f"frame_{app.software_dir}_{instance}_MAIN"] = tk.Frame(
		globals()[f"frame_{app.software_dir}_{instance}"],
		width=parent_width - 8,
		height=parent_height - icon_size - 8
	)
	globals()[f"frame_{app.software_dir}_{instance}_MAIN"].place(
		x=4,
		y=icon_size + 4,
		width=parent_width - 8,
		height=parent_height - icon_size - 8
	)

	# Launches the app so it can place its elements
	app.on_app_launch(
		globals()[f"frame_{app.software_dir}_{instance}_MAIN"],
		width=parent_width - 8,
		height=parent_height - icon_size - 8
	)

	# Creates the draggable pixels
	globals()[f"frame_{app.software_dir}_{instance}_resizeable_frame"] = tk.Frame(
		globals()[f"frame_{app.software_dir}_{instance}"]
	)

	def Resize(minsize, maxsize, event):
		nonlocal parent_width
		nonlocal parent_height
		if minsize is None or maxsize is None or not (event.x + parent_width > maxsize[0] or event.x + parent_width < minsize[0]):
			parent_width = event.x + parent_width
		if minsize is None or maxsize is None or not (event.y + parent_height > maxsize[1] or event.y + parent_height < minsize[1]):
			parent_height = event.y + parent_height
		globals()[f"frame_{app.software_dir}_{instance}"].place(
			x=globals()[f"{app.software_dir}_{instance}_last_coords"][0],
			y=globals()[f"{app.software_dir}_{instance}_last_coords"][1],
			width=parent_width,
			height=parent_height
		)
		globals()[f"frame_{app.software_dir}_{instance}_resizeable_frame"].place(
			x=parent_width - 8,
			y=parent_height - 8,
			width=8,
			height=8
		)
		globals()[f"frame_{app.software_dir}_{instance}_MAIN"].place(
			x=4,
			y=icon_size + 4,
			width=parent_width - 8,
			height=parent_height - icon_size - 8
		)
		quit_button.place(
			x=parent_width - icon_size - 2,
			y=2,
			height=icon_size,
			width=icon_size
		)
		expand_button.place(
			x=parent_width - icon_size * 2 - 4,
			y=4,
			height=icon_size,
			width=icon_size
		)

	globals()[f"frame_{app.software_dir}_{instance}_resizeable_frame"].bind("<B1-Motion>", partial(Resize, app.min_size, app.max_size))
	globals()[f"frame_{app.software_dir}_{instance}_resizeable_frame"].place(
		x=parent_width - 8,
		y=parent_height - 8,
		width=8,
		height=8
	)

	# Finally places the MAIN frame in the software one
	globals()[f"frame_{app.software_dir}_{instance}"].place(
		x=globals()[f"{app.software_dir}_{instance}_last_coords"][0],
		y=globals()[f"{app.software_dir}_{instance}_last_coords"][1],
		width=parent_width,
		height=parent_height
	)

	opened_apps_amount += 1

def ACOS_Menu_click(event):
	window = globals()["root"]
	# ------------------ CREATING A MENU FRAME IF NOT EXISTING ------------------
	if "menu_frame" not in globals().keys():
		# Frame
		globals()["menu_frame"] = tk.Frame(
			window,
			bg="#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"]
		)
		globals()["menu_frame_MAIN"] = tk.Frame(
			globals()["menu_frame"],
			bg="#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"]
		)

		# ------------------ FRAME FUNCTIONS ------------------
		def close_all_windows():
			for variable in globals():
				if isinstance(globals()[variable], tk.Frame) \
						and not variable.startswith("navbar") \
						and not variable.startswith("menu_frame"):
					try:
						globals()[variable].place_forget()
						globals()[variable].destroy()
					except:
						pass

		def shutdown():
			window.destroy()
			sys.exit(0)

		def launch_task_manager():
			background_color = globals()["REGISTRY"]["APP_FRAME_BACKGROUND_COLOR"]

			# Creates the frame
			globals()[f"frame_task_manager"] = tk.Frame(
				window,
				bg=background_color
			)

			def Lift(event):
				"""
				Lifts the frame on top.
				"""
				globals()["frame_task_manager"].lift()
				task_manager_code()

			globals()["frame_task_manager_last_coords"] = \
				(randint(
					globals()["navbar_size"],
					round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_WIDTH"] * 0.25)
				), randint(
					globals()["navbar_size"],
					round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_HEIGHT"] * 0.25)
				)
				)

			def Drag(event):
				"""
				Generates the dragging of the window.
				"""
				x = event.x + (globals()["frame_task_manager"].winfo_width() // 2)
				y = event.y + (globals()["frame_task_manager"].winfo_height() // 2)

				if isclose(globals()["frame_task_manager_last_coords"][0],
				           x, rel_tol=5) and isclose(globals()["frame_task_manager_last_coords"][1],
				                                     y, rel_tol=5):

					globals()["frame_task_manager"].place(
						x=x,
						y=y
					)

					globals()["frame_task_manager_last_coords"] = (x, y)

			globals()["frame_task_manager"].bind('<B1-Motion>', Drag)
			globals()["frame_task_manager"].bind('<Button-1>', Lift)

			# Generates the icon
			icon_size = globals()["REGISTRY"]["ICONS_SIZES"]

			globals()["task_manager_icon"] = ImageTk.PhotoImage(
				Image.open(
					"assets/ACOS_TaskManager.png"
				).resize(
					(icon_size, icon_size)
				)
			)

			app_icon_label = tk.Label(
				globals()["frame_task_manager"],
				image=globals()["task_manager_icon"],
				bg=background_color
			)
			app_icon_label.place(
				x=2,
				y=2,
				width=icon_size,
				height=icon_size
			)

			# Creates and places the app title
			app_title = tk.Label(
				globals()["frame_task_manager"],
				text=TRANSLATIONS["ACOS_MENU"]["TaskManager"],
				bg=background_color,
				fg=globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
			)
			app_title.place(
				x=icon_size + 2,
				y=0
			)

			def quit_app():
				nonlocal tasks
				nonlocal task_kill_buttons
				globals()["frame_task_manager"].place_forget()
				globals()["frame_task_manager"].destroy()
				for task in tasks:
					task.destroy()
				for btn in task_kill_buttons:
					btn.destroy()

			# Creates the width of the app frame
			parent_width = randint(
				round(globals()["REGISTRY"]["WIN_WIDTH"] * 0.5),
				round(globals()["REGISTRY"]["WIN_WIDTH"] * 0.7)
			)
			parent_height = randint(
				round(globals()["REGISTRY"]["WIN_HEIGHT"] * 0.5),
				round(globals()["REGISTRY"]["WIN_HEIGHT"] * 0.7)
			)

			# Quit icon
			globals()["task_manager_quit_icon"] = ImageTk.PhotoImage(
				Image.open("assets/ACOS_Bin.png").resize((16, 16))
			)

			# Creates the quit button
			quit_button = tk.Button(
				globals()["frame_task_manager"],
				image=globals()["task_manager_quit_icon"],
				borderwidth=0,
				command=quit_app,
				bg=background_color,
				activebackground=background_color
			)
			quit_button.place(
				x=parent_width - icon_size - 2,
				y=2,
				height=icon_size,
				width=icon_size
			)

			# Creates a new MAIN frame inside the app frame
			globals()["frame_task_manager_MAIN"] = tk.Frame(
				globals()["frame_task_manager"],
				width=parent_width - 8,
				height=parent_height - icon_size - 8
			)
			globals()["frame_task_manager_MAIN"].place(
				x=4,
				y=icon_size + 4,
				width=parent_width - 8,
				height=parent_height - icon_size - 8
			)

			def kill_task(task, row):
				"""
				Kills the given task.
				"""
				nonlocal tasks
				nonlocal task_kill_buttons
				# Task destroying
				try:
					globals()[task].place_forget()
				except:
					try:
						globals()[task].grid_forget()
					except:
						try:
							globals()[task].pack_forget()
						except:
							pass
				# Elements destroying
				try:
					tasks[row - 1].grid_forget()
				except:
					pass
				try:
					task_kill_buttons[row - 1].grid_forget()
				except:
					pass
				try:
					tasks[row - 1].destroy()
				except:
					pass
				try:
					task_kill_buttons[row - 1].destroy()
				except:
					pass

				try:
					globals()[task].destroy()
					del globals()[task]
				except KeyError:
					pass

				import ROOT.softwares.software_api
				ROOT.softwares.software_api.notify(
					TRANSLATIONS["ACOS_MENU"]["TaskManager"],
					f"Killed task {task.replace('frame_', '', 1)}."
				)

			# ! TASK MANAGER CODE
			# Columns indications
			column0 = tk.Label(
				globals()["frame_task_manager_MAIN"],
				text=TRANSLATIONS["ACOS_MENU"]["TaskName"],
				font=("Impact", 12)
			)
			column0.grid(row=0, column=0)

			process = psutil.Process(os.getpid())

			column1 = tk.Label(
				globals()["frame_task_manager_MAIN"],
				text=TRANSLATIONS["ACOS_MENU"]["ProcessorUsage"] + " :\n" + str(process.cpu_percent()) + "%"
			)
			column1.grid(row=0, column=1)

			column2 = tk.Label(
				globals()["frame_task_manager_MAIN"],
				text=TRANSLATIONS["ACOS_MENU"]["MemoryUsage"] + " :\n" + \
				     str(round(process.memory_info().rss / 1024 ** 2, 2)) \
				     + f"MBs"
			)
			column2.grid(row=0, column=2)

			# TODO : Scrollbar

			tasks = []
			task_kill_buttons = []

			def task_manager_code():
				nonlocal tasks
				nonlocal task_kill_buttons

				# Emptying them
				for i in range(len(tasks)):
					tasks[i].grid_forget()
					tasks[i].destroy()
					task_kill_buttons[i].grid_forget()
					task_kill_buttons[i].destroy()

				# If the variable is an app
				for variable in globals():
					if variable.startswith("frame_") and not variable.endswith("_MAIN") \
							and not variable.startswith("frame_task_manager") and \
							not variable.endswith("_resizeable_frame"):
						# If it is an app, we display it
						tasks.append(
							tk.Label(
								globals()["frame_task_manager_MAIN"],
								text=variable.replace("frame_", "", 1)
							)
						)
						tasks[-1].grid(
							row=len(tasks),
							column=0
						)

						# And we add the task kill button
						task_kill_buttons.append(
							tk.Button(
								globals()["frame_task_manager_MAIN"],
								text=TRANSLATIONS["ACOS_MENU"]["TaskKill"],
								command=partial(kill_task, variable, len(tasks))
							)
						)
						task_kill_buttons[-1].grid(
							row=len(tasks),
							column=1
						)

			task_manager_code()

			# Finally places the MAIN frame in the software one
			globals()["frame_task_manager"].place(
				x=globals()["frame_task_manager_last_coords"][0],
				y=globals()["frame_task_manager_last_coords"][1],
				width=parent_width,
				height=parent_height
			)

		# ------------------ FRAME ELEMENTS ------------------
		btn_params = {
			"font": ("Arial", 16),
			"bg": "#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"],
			"fg": globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
		}

		button_close_all = tk.Button(
			globals()["menu_frame_MAIN"],
			text=TRANSLATIONS["ACOS_MENU"]["CloseAllWindows"],
			command=close_all_windows,
			width=globals()["menu_frame"].winfo_width() // 2,
			**btn_params
		)
		button_close_all.grid(
			row=0,
			column=0
		)

		# Task manager
		task_manager_button = tk.Button(
			globals()["menu_frame_MAIN"],
			text=TRANSLATIONS["ACOS_MENU"]["TaskManager"],
			command=launch_task_manager,
			**btn_params
		)
		task_manager_button.grid(
			row=1,
			column=0
		)

		apps_canvas = tk.Canvas(
			globals()["menu_frame_MAIN"],
			width=globals()["menu_frame"].winfo_width(),
			height=round(globals()["menu_frame"].winfo_height() * 0.8),
			bg=btn_params["bg"]
		)

		scrollbar = tk.Scrollbar(
			apps_canvas
		)
		scrollbar.pack(
			side=tk.RIGHT,
			fill=tk.Y
		)
		apps_frame = tk.Canvas(
			apps_canvas,
			yscrollcommand=scrollbar.set,
			bg=btn_params["bg"]
		)

		# Adding the apps inside
		done_apps = []
		iterations = 0
		for software in os.listdir("ROOT/" + globals()["REGISTRY"]["SOFTWARES_FOLDER"]):
			# Imports the software file
			try:
				importlib.import_module(f"ROOT.{globals()['REGISTRY']['SOFTWARES_FOLDER']}.{software}.{software}")
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

					globals()["MENU_app_buttons_" + str(iterations) + "_NAME"] = tk.Label(
						apps_canvas,
						text=app.software_name,
						**btn_params
					)
					globals()["MENU_app_buttons_" + str(iterations) + "_NAME"].pack()
					globals()["MENU_app_buttons_" + str(iterations) + "_NAME"].bind("<ButtonPress-1>", partial(
						launched_app, app, app.min_size, app.max_size
					))

					done_apps.append(app.software_dir)

					iterations += 1
				except Exception as e:
					try:
						del globals()["MENU_app_tkimages_" + str(iterations)]
						del globals()["MENU_app_buttons_" + str(iterations) + "_NAME"]
					except:
						pass
					print(e)

		apps_frame.pack(
			side=tk.LEFT,
			fill=tk.BOTH
		)
		scrollbar.config(command=apps_frame.yview)

		apps_canvas.grid(
			row=2,
			column=0,
			rowspan=6,
			columnspan=2
		)

		shutdown_button = tk.Button(
			globals()["menu_frame"],
			text=TRANSLATIONS["ACOS_MENU"]["Shutdown"],
			command=shutdown,
			**btn_params
		)
		shutdown_button.place(
			x=0,
			y=360
		)

		# ------------------ FRAME VISIBILITY ------------------

		globals()["menu_frame"].lift()
		globals()["menu_frame_MAIN"].place(x=0, y=0)
		globals()["menu_frame"].place(
			x=globals()["navbar_size"],
			y=0
		)

		# Frame enabled
		globals()["menu_frame_enabled"] = False

	# ------------------ TOGGLING FRAME VISIBILITY ------------------
	if globals()["menu_frame_enabled"] is True:
		globals()["menu_frame_enabled"] = False
		globals()["menu_frame"].place_forget()
	else:
		globals()["menu_frame_enabled"] = True
		globals()["menu_frame"].lift()
		globals()["menu_frame"].place(
			x=globals()["navbar_size"],
			y=0,
			width=400,
			height=800
		)

def create_new_user(window: tk.Tk, REGISTRY: dict):
	"""
	Creation menu at ACOS start.
	"""
	from boot import finish_boot
	background = "#0D4EB8"
	window["bg"] = "black"

	# If the users folder doesn't exist
	if REGISTRY["USERS_FOLDER"] not in os.listdir("ROOT/"):
		# We create it
		os.mkdir("ROOT/" + REGISTRY["USERS_FOLDER"])

	# Title
	title_var = tk.StringVar()
	title_var.set("Welcome to the ACOS")
	title_label = tk.Label(
		window,
		textvariable=title_var,
		font=("Haettenschweiler", 30),
		bg="black",
		fg="white"
	)
	title_label.pack(
		pady=window.winfo_height() * 0.4
	)

	# Profile picture widgets
	pfp_path = "assets/ACOS_Logo.png"
	pfp_name = "ACOS_Logo.png"

	def user_setup():
		"""
		Sets the '.userdata.json' file for the user.
		"""
		global username

		userdata = {
			"ProfileImage": pfp_name,
			"HASH": globals()["password_salt"],
			"PASSWORD": globals()["password"],
			"taskbar": REGISTRY["DEFAULT_APPS"],
			"is_admin": True,
			"startup_apps": []
		}

		userdata_file = open("ROOT/" + REGISTRY["USERS_FOLDER"] \
		                     + "/" + username + f"/{REGISTRY['USERDATA_NAME']}.json", "w")
		json.dump(userdata, userdata_file, indent=4)
		userdata_file.close()

		general_data_file = open("general_data.json", "r")
		general_data = json.load(general_data_file)
		general_data_file.close()
		general_data["last_connected_user"] = username
		general_data_file = open("general_data.json", "w")
		json.dump(general_data, general_data_file, indent=4)
		general_data_file.close()

		# Creation of the desktop
		os.mkdir("ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + username + f"/_desktop")

		del globals()["password_salt"]
		del globals()["password"]

		window.after(4200, start_text_blend, "Your account has been created.")
		window.after(9000, end_text_blend)

		def delete_title():
			title_label.pack_forget()

		window.after(5000, delete_title)
		window.after(
			5000,
			blend_tools.blend_colors_in,
			window,
			background,
			"#000000"
		)

		window.after(8000, reboot, window, REGISTRY)

	def reboot(window, REGISTRY):
		suffix = '' if platform.platform() == "Windows" else '3'
		os.system(f"python{suffix} boot.py")
		window.destroy()

	def display_password():
		password_entry.pack()
		password_validate.pack()
		blend_tools.blend_colors_in(
			window,
			background,
			"#ffffff",
			password_entry,
			password_validate,
			change_window=False,
			foreground=True
		)

	def save_password():
		"""
		Saves the password.
		"""
		# If it is empty, we do nothing.
		if password_var.get() == "":
			return

		globals()["password_salt"] = hash_utility.gen_hash("return")
		globals()["password"] = hash_utility.cipher_password(
			password_var.get(),
			"given",
			globals()["password_salt"]
		).decode()

		# Launches the next user creation part : The taskbar
		blend_tools.blend_colors_in(
			window,
			"#ffffff",
			background,
			password_entry,
			password_validate,
			ms_between=3,
			change_window=False,
			foreground=True
		)
		window.after(2000,
		             forget_elements,
		             password_entry,
		             password_validate
		             )

		window.after(2000, start_text_blend, "Thank you.")
		window.after(10000, start_text_blend, "We are setting up the user for you.", user_setup)

	# Password entry
	password_var = tk.StringVar()
	password_entry = tk.Entry(
		window,
		textvariable=password_var,
		bg=background,
		fg=background,
		font=("Calibri", 18),
		insertbackground="white"
	)
	password_validate = tk.Button(
		window,
		text="SAVE",  # TODO : Translations
		bg=background,
		fg=background,
		font=("Calibri", 18),
		command=save_password
	)

	def validate_pfp(path=None):
		"""
		Validates the profile picture :
		Copies it into the correct folder.
		"""
		nonlocal username
		nonlocal pfp_path
		nonlocal pfp_name
		if path not in (None, ""):
			pfp_path = path
		else:
			pfp_path = "assets/ACOS_Logo.png"

		pfp_name = pfp_path.split("/")[-1]
		try:
			if username == "":
				raise Exception  # Going to the except
			os.mkdir("ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + username + "/.userdata/")
		except:
			folders_list = os.listdir("ROOT/" + REGISTRY["USERS_FOLDER"] + "/")
			try:
				folders_list.remove(".userdata")
			except Exception:
				pass
			os.mkdir("ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + folders_list[0] + "/.userdata/")
		try:
			shutil.copyfile(
				pfp_path,
				"ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + username + "/.userdata/" + pfp_name
			)
		except Exception as e:
			try:
				folders_list = os.listdir("ROOT/" + REGISTRY["USERS_FOLDER"] + "/")
				try:
					folders_list.remove(".userdata")
				except Exception:
					pass
				shutil.copyfile(
					pfp_path,
					"ROOT/" + REGISTRY["USERS_FOLDER"] + "/" + folders_list[0] + "/.userdata/" + pfp_name
				)
			except Exception:
				ThrowBSOD(window, "Unable to copy profile picture.\nError : " + str(e))

		# Launches the next user creation part : The password
		blend_tools.blend_colors_in(
			window,
			"#ffffff",
			background,
			load_pfp_button,
			no_pfp_button,
			pfp_or_label,
			title_label,
			ms_between=3,
			change_window=False,
			foreground=True
		)
		window.after(2000,
		             forget_elements,
		             load_pfp_button,
		             no_pfp_button,
		             pfp_or_label
		             )
		window.after(2000, forget_elements, pfp_frame)

		window.after(6000, start_text_blend, "Choose a password.", display_password)

	def load_profile_picture():
		"""
		Loads the profile picture using a dialog box.
		"""
		global pfp_path
		path = filedialog.askopenfilename(
			filetypes=(("PNG", "*.png"), ("JPG", "*.jpg"))
		)
		if path is not None:
			validate_pfp(path)

	pfp_frame = tk.Frame(window, bg=background)
	load_pfp_button = tk.Button(
		pfp_frame,
		text="Load profile picture",
		command=load_profile_picture,
		bg=background,
		fg=background,
		font=("Impact", 16)
	)
	load_pfp_button.grid(row=0, column=0, sticky="e")
	no_pfp_button = tk.Button(
		pfp_frame,
		text="use the default one",
		command=validate_pfp,
		bg=background,
		fg=background,
		font=("Impact", 16)
	)
	no_pfp_button.grid(row=0, column=2, sticky="w")
	pfp_or_label = tk.Label(pfp_frame, text="or", bg=background, fg=background, font=("Impact", 16))
	pfp_or_label.grid(row=0, column=1)

	def display_username_entry():
		username_entry.pack()
		username_save_button.pack()

		blend_tools.blend_colors_in(
			window,
			background,
			"#ffffff",
			username_entry,
			username_save_button,
			ms_between=4,
			change_window=False,
			foreground=True
		)

	def forget_elements(*widgets, placement: str = "pack"):
		for widget in widgets:
			if placement == "pack":
				try:
					widget.pack_forget()
				except:
					try:
						widget.grid_forget()
					except:
						widget.place_forget()
			elif placement == "grid":
				widget.grid_forget()
			else:
				widget.place_forget()

	def load_profile_pic():
		pfp_frame.pack()
		blend_tools.blend_colors_in(
			window,
			background,
			"#ffffff",
			load_pfp_button,
			no_pfp_button,
			pfp_or_label,
			change_window=False,
			foreground=True
		)

	username = ""

	def save_username():
		"""
		Creates the folder for the user.
		"""
		global username
		username = username_entry_var.get().replace("../", "").replace("/", "_") \
			.replace("\\", "_")
		# If username is empty, we do nothing.
		if username == "":
			return

		# Removal of special characters
		temp_username = ""
		for letter in username:
			if letter not in tuple("\\/:?*\"<>|"):
				temp_username += letter
		username = temp_username
		del temp_username

		os.mkdir(f"ROOT/" + REGISTRY["USERS_FOLDER"] \
		         + "/" + username)

		blend_tools.blend_colors_in(
			window,
			"#ffffff",
			background,
			username_save_button,
			username_entry,
			title_label,
			ms_between=3,
			change_window=False,
			foreground=True
		)
		window.after(1500, forget_elements, username_save_button, username_entry)
		window.after(7000, change_text, "Upload a profile picture from your operating system.", load_profile_pic)

	username_entry_var = tk.StringVar()
	username_entry = tk.Entry(
		window,
		textvariable=username_entry_var,
		bg=background,
		fg=background,
		font=("Calibri", 18),
		insertbackground="white"
	)
	username_save_button = tk.Button(
		window,
		text="SAVE",
		bg=background,
		fg=background,
		command=save_username,
		bd=0,
		font=("Impact", 14)
	)

	def start_text_blend(text, function_to_execute=None):
		blend_tools.blend_colors_in(
			window,
			"#ffffff",
			background,
			title_label,
			ms_between=1,
			change_window=False,
			foreground=True
		)
		window.after(1600, change_text, text, function_to_execute)

	def change_text(text, function_to_execute=None):
		title_var.set(text)
		window.after(170, end_text_blend)
		if function_to_execute is not None:
			window.after(170, function_to_execute)

	def end_text_blend():
		blend_tools.blend_colors_in(
			window,
			background,
			"#ffffff",
			title_label,
			ms_between=4,
			change_window=False,
			foreground=True
		)

	blend_tools.blend_colors_in(
		window,
		"#000000",
		background,
		title_label,
		ms_between=3
	)

	window.after(3000, start_text_blend, "Let's create a new user.")
	window.after(11000, start_text_blend, "Select a new username.", display_username_entry)

def remove_suffix(variable: str, condition: bool = True, chars_amount: int = 1):
	"""
    Removes the suffix of a string.
    Parameter 'variable' (str) : The text where the suffix has to be removed.
    Parameter 'chars_amount' (int) : Default : 1. Number of chars to remove.
    Parameter 'condition' (bool) : Default : True. Will only remove if the condition is True.
    """
	if condition is True:  # If the condition is respected
		variable = variable[:-chars_amount]  # Suffix gets removed
	return variable
