import tkinter as tk
import sys
import json
import os
import importlib
import ROOT.softwares as all_softwares
from PIL import Image, ImageTk
from functools import partial
from random import randint
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

def set_locale(locale:str):
	"""
	Sets the system language.
	"""
	global lang
	global TRANSLATIONS
	lang = locale.upper()
	language_file = open(f"SYSTEM_LANG_{lang}.json", "r", encoding = "utf-8")
	TRANSLATIONS = json.load(language_file)
	language_file.close()

def ThrowBSOD(window:tk.Tk, message=""):
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
	).place(
		x = 40,
		y = 40
	)
	message_label = tk.Label(
		window,
		text=TRANSLATIONS["BSOD"][message] if message in TRANSLATIONS.keys() else message,
		font=("Impact", 18),
		bg=BSOD_COLOR,
		fg="white"
	).place(
		x = 40,
		y = 180
	)
	reboot_label = tk.Label(
		window,
		text=TRANSLATIONS["BSOD"]["RebootMsg"],
		font=("Impact", 24),
		bg=BSOD_COLOR,
		fg="white"
	).place(
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

	for item in _list :
		if item.winfo_children() :
			_list.extend(item.winfo_children())

	return _list

def destroy_all_widgets(window:tk.Tk):
	"""
	Destroys all widgets in given window.
	"""
	widget_list = get_all_widgets(window)
	for item in widget_list:
		item.place_forget()
		item.destroy()

def corrupted_key(key, general_data:bool=False):
	return TRANSLATIONS["BSOD"]["CorruptedKey"].format(key=key) + \
	       ("\n" + TRANSLATIONS["BSOD"]["GeneralDataKey"] if general_data is True else "")

def error(message):
	# TODO !
	pass

def start_OS(window:tk.Tk, REGISTRY:dict):
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
				text = user,
				borderwidth = 0,
				command = partial(select_user, user, window, REGISTRY),
				bg = REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]],
				fg = REGISTRY["MAIN_FG_COLOR"][globals()["current_theme"]],
				font = ("Calibri Light", 20)
			)
		)
		users_list[-1].place(
			x = 2,
			y = window.winfo_height() - (32 * (i + 1)),
			height = 32
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
		text = last_connected_user,
		font = ("Calibri Light", 26),
		fg = REGISTRY["MAIN_FG_COLOR"][globals()["current_theme"]],
		bg = REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]]
	)
	globals()["username_label"].place(
		x = window.winfo_width() // 2 - (len(last_connected_user) // 2 * 12),
		y = window.winfo_height() // 2 - 26
	)

	# Displaying the ACOS logo on top of it
	globals()["user_logo_canvas"] = tk.Canvas(
		window,
		width = 128,
		height = 128,
		bg = REGISTRY["MAIN_BG_COLOR"][globals()["current_theme"]],
		bd = 0,
		highlightthickness = 0,
		relief='ridge'
	)
	globals()["user_logo_canvas"].place(
		x = window.winfo_width() // 2 - 32 * 1.5,
		y = window.winfo_height() // 2 - 128 * 1.5
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
		image = globals()["user_logo"],
		anchor = "nw"
	)

	# Password field
	globals()["password_field"] = tk.Entry(
		window,
		show = "*"  # TODO : ECOLEDIRECTE APP -> USES ECOLEDIRECTE API
	)

	if globals()["current_theme"] == "dark":  # Dark theme modifiers
		globals()["password_field"].config(
			bg = "#404040",
			fg = "white",
			insertbackground = "white"
		)

	globals()["password_field"].place(
		x = window.winfo_width() // 2 - 32 * 1.4,
		y = window.winfo_height() // 2 + 32,
		width = 128,
		height = 24
	)
	# And send button
	globals()["password_send_button"] = tk.Button(
		window,
		text = "->",
		font = ("JetBrains Mono", 16),
		command = partial(compute_password, "password_field", window),
		borderwidth = 0
	)

	if globals()["current_theme"] == "dark":  # Dark theme modifiers
		globals()["password_send_button"].config(
			bg = "#404040",
			fg = "white"
		)

	globals()["password_send_button"].place(
		x = window.winfo_width() // 2 - 32 * 1.4 + 128,
		y = window.winfo_height() // 2 + 32,
		height = 24
	)

def compute_password(entry_name:str, window:tk.Tk):
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
		json.dump(general_data, general_data_file, indent = 4)
		general_data_file.close()

		# ------------------ SETUP NAVBAR ------------------
		setup_navbar(window, globals()["REGISTRY"], user)
	else:
		incorrect_password_label = tk.Label(
			window,
			text = globals()["TRANSLATIONS"]["LOGIN"]["IncorrectPassword"],
			fg = "red",
			bg = globals()["REGISTRY"]["MAIN_BG_COLOR"][globals()["current_theme"]]
		)
		incorrect_password_label.place(
			x = window.winfo_width() // 2\
			    - len(globals()["TRANSLATIONS"]["LOGIN"]["IncorrectPassword"]),
			y = window.winfo_height() // 2 + 96
		)

def get_userdata(window, user, REGISTRY):
	try:
		userdata_file = open(
			f"ROOT/{REGISTRY['USERS_FOLDER']}/{user}/{REGISTRY['USERDATA_NAME']}.json",
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
	globals()["username_label"].config(text = user)
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

def setup_navbar(window, REGISTRY, user):
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
		bg = background
	)

	# ------------------ NAVBAR ELEMENTS ------------------
	done_apps = []
	user_taskbar = get_userdata(window, user, REGISTRY)["taskbar"]

	if "SOFTWARES_FOLDER" not in REGISTRY:
		ThrowBSOD(window, corrupted_key("SOFTWARES_FOLDER"))

	iterations = 0
	for software in os.listdir(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}/"):
		# Imports the software file
		try:
			importlib.import_module(f"ROOT.{REGISTRY['SOFTWARES_FOLDER']}.{software}.{software}")
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
				if app.software_dir in done_apps or app.software_dir not in user_taskbar:
					continue


				globals()["app_tkimages_"+str(iterations)] = \
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


				globals()["app_buttons_"+str(iterations)] = \
					tk.Canvas(
						navbar_frame,
						highlightthickness = 0,
						bg = background,
						width = navbar_size,
						height = navbar_size
					)
				globals()["app_buttons_"+str(iterations)].create_image(
					0,
					0,
					image = globals()["app_tkimages_"+str(iterations)],
					anchor = "nw"
				)
				globals()["app_buttons_"+str(iterations)].bind("<ButtonPress-1>", partial(launched_app, app))
				"""image = globals()["app_tkimages_"+str(iterations)],
				command = partial(launched_app, app),
				borderwidth = 0,
				"""

				globals()["app_buttons_"+str(iterations)].pack(padx = 5)

				done_apps.append(app.software_dir)

				iterations += 1
			except Exception as e:
				del globals()["app_tkimages_"+str(iterations)]
				del globals()["app_buttons_"+str(iterations)]
				print(e)

	#del iterations

	# ------------------ FINAL NAVBAR PLACING ------------------
	try:
		navbar_frame.place(
			x = 0,
			y = navbar_size,
			width = navbar_size,
			height = REGISTRY["WIN_HEIGHT"] - navbar_size if REGISTRY["FULLSCREEN_ENABLED"] is False else window.winfo_screenheight() - navbar_size,
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
		image = globals()["ACOS_Menu_icon"],
		anchor = "nw"
	)
	"""tk.Button(
		window,
		image = ACOS_Menu_icon,
		#text = "MENU",
		command = ACOS_Menu_click,
		borderwidth = 0,
		bg = REGISTRY["NAVBAR_BG_COLOR"][globals()["current_theme"]],
		fg = REGISTRY["MAIN_FG_COLOR"][globals()["current_theme"]],
		font = ("Impact", 20)
	)"""
	ACOS_Menu_button.place(
		x = 0,
		y = 0,
		width = navbar_size,
		height = navbar_size
	)

	globals()["navbar_size"] = navbar_size
	globals()["root"] = window

def launched_app(app, event):
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
		bg = background_color
	)

	# Generates the icon
	icon_size = globals()["REGISTRY"]["ICONS_SIZES"]

	globals()["app_icon_"+str(opened_apps_amount)] = ImageTk.PhotoImage(
		Image.open(
			f"ROOT/{globals()['REGISTRY']['SOFTWARES_FOLDER']}/{app.software_dir}/{app.app_icon}"
		).resize(
			(icon_size, icon_size)
		)
	)

	app_icon_label = tk.Label(
		globals()[f"frame_{app.software_dir}_{instance}"],
		image = globals()["app_icon_"+str(opened_apps_amount)],
		bg = background_color
	)
	app_icon_label.place(
		x = 2,
		y = 2,
		width = icon_size,
		height = icon_size
	)

	# Creates and places the app title
	app_title = tk.Label(
		globals()[f"frame_{app.software_dir}_{instance}"],
		text = app.software_name,
		bg = background_color,
		fg = globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
	)
	app_title.place(
		x = icon_size + 2,
		y = 0
	)

	def quit_app():
		globals()[f"frame_{app.software_dir}_{instance}"].place_forget()
		globals()[f"frame_{app.software_dir}_{instance}"].destroy()

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
	globals()["quit_icon_"+str(opened_apps_amount)] = ImageTk.PhotoImage(
		Image.open("assets/ACOS_Bin.png").resize((16, 16))
	)

	# Creates the quit button
	quit_button = tk.Button(
		globals()[f"frame_{app.software_dir}_{instance}"],
		image = globals()["quit_icon_"+str(opened_apps_amount)],
		borderwidth = 0,
		command = quit_app,
		bg = background_color,
		activebackground = background_color
	)
	quit_button.place(
		x = parent_width - icon_size - 2,
		y = 2,
		height = icon_size,
		width = icon_size
	)

	# Creates a new MAIN frame inside the app frame
	globals()[f"frame_{app.software_dir}_{instance}_MAIN"] = tk.Frame(
		globals()[f"frame_{app.software_dir}_{instance}"]
	)
	globals()[f"frame_{app.software_dir}_{instance}_MAIN"].place(
		x = 4,
		y = icon_size + 4,
		width = parent_width  - 8,
		height = parent_height - icon_size - 8
	)

	# Launches the app so it can place its elements
	app.on_app_launch(globals()[f"frame_{app.software_dir}_{instance}_MAIN"])

	# Finally places the MAIN frame in the software one
	globals()[f"frame_{app.software_dir}_{instance}"].place(
		x = randint(
			globals()["navbar_size"],
			round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_WIDTH"] * 0.25)
		),
		y = randint(
			globals()["navbar_size"],
			round(globals()["navbar_size"] + globals()["REGISTRY"]["WIN_HEIGHT"] * 0.25)
		),
		width = parent_width,
		height = parent_height
	)

	opened_apps_amount += 1

def ACOS_Menu_click(event):
	window = globals()["root"]
	# ------------------ CREATING A MENU FRAME IF NOT EXISTING ------------------
	if "menu_frame" not in globals().keys():
		# Frame
		globals()["menu_frame"] = tk.Frame(
			window,
			bg = "#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"]
		)
		globals()["menu_frame_MAIN"] = tk.Frame(
			globals()["menu_frame"],
			bg = "#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"]
		)

		# ------------------ FRAME FUNCTIONS ------------------
		def close_all_windows():
			for variable in globals():
				if isinstance(globals()[variable], tk.Frame)\
						and not variable.startswith("navbar")\
						and not variable.startswith("menu_frame"):
					try:
						globals()[variable].place_forget()
						globals()[variable].destroy()
					except:
						pass

		def shutdown():
			window.destroy()
			sys.exit(0)

		# ------------------ FRAME ELEMENTS ------------------
		button_close_all = tk.Button(
			globals()["menu_frame_MAIN"],
			text = TRANSLATIONS["ACOS_MENU"]["CloseAllWindows"],
			command = close_all_windows,
			font = ("Arial", 16),
			width = globals()["menu_frame"].winfo_width() // 2,
			bg = "#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"],
			fg = globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
		)
		button_close_all.grid(
			row = 0,
			column = 0
		)

		shutdown_button = tk.Button(
			globals()["menu_frame"],
			text = TRANSLATIONS["ACOS_MENU"]["Shutdown"],
			command = shutdown,
			font=("Arial", 16),
			bg = "#f0f0f0" if globals()["current_theme"] == "light" else globals()["REGISTRY"]["MAIN_BG_COLOR"]["light-dark"],
			fg = globals()["REGISTRY"]["MAIN_FG_COLOR"][globals()["current_theme"]]
		)
		shutdown_button.place(
			x = 0,
			y = 360
		)

		# ------------------ FRAME VISIBILITY ------------------

		globals()["menu_frame"].lift()
		globals()["menu_frame_MAIN"].place(x=0, y=0)
		globals()["menu_frame"].place(
			x = globals()["navbar_size"],
			y = 0
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
			height=400
		)

