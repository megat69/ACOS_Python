"""
The ACOS "operating system".
Is a software, but whatver, still fun to use.
"""
from main import *
import json
from random import randint

# ------------------ ESSENTIAL VARS ------------------
WIN_WIDTH, WIN_HEIGHT = 1024, 512

if __name__ == '__main__':
	import tkinter as tk
	from PIL import Image, ImageTk
	window = tk.Tk()

	# ------------------ REGISTRY USE ------------------
	try:
		temp_registry_file = open("registry.json", "r", encoding="utf-8")
	except FileNotFoundError:
		ThrowBSOD(window, "Registry could not be loaded.")
	except:
		ThrowBSOD(window, "An unknown error occured while trying to open registry.")
	try:
		REGISTRY = json.load(temp_registry_file)
	except:
		ThrowBSOD(window, "An unknown error occured while trying to open registry.")
	temp_registry_file.close()

	# ------------------ LANGUAGE DETECTION ------------------
	try:
		language = REGISTRY["SYSTEM_LANG"]
	except:
		ThrowBSOD(window, corrupted_key("SYSTEM_LANG") + "\nCould not load system language.")

	# Setting it for recurrent_classes
	set_locale(language)

	# ------------------ WINDOW CREATION ------------------
	window.resizable(0, 0)
	window.title("ACOS")
	try:
		window.iconbitmap("assets/ACOS_Logo.ico")
	except:
		ThrowBSOD(window, "Icon not found")

	# Loading fullscreen
	if "FULLSCREEN_ENABLED" not in REGISTRY or not isinstance(REGISTRY["FULLSCREEN_ENABLED"], bool):
		ThrowBSOD(window, corrupted_key("FULLSCREEN_ENABLED"))
	elif REGISTRY["FULLSCREEN_ENABLED"] is True:
		window.attributes("-fullscreen", True)
		WIN_WIDTH = window.winfo_screenwidth()
		WIN_HEIGHT = window.winfo_screenheight()
	else:
		# Loading the window dimensions keys.
		try:
			WIN_WIDTH = REGISTRY["WIN_WIDTH"]
		except:
			ThrowBSOD(window, corrupted_key("WIN_WIDTH"))
		try:
			WIN_HEIGHT = REGISTRY["WIN_HEIGHT"]
		except:
			ThrowBSOD(window, corrupted_key("WIN_HEIGHT"))

	window.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")

	# Window BG for loading
	try:
		window["bg"] = REGISTRY["LOADING_BACKGROUND_COLOR"]
	except:
		ThrowBSOD(window, corrupted_key("LOADING_BACKGROUND_COLOR"))

	# ------------------ LOGO DISPLAYING ------------------
	if "LOGO_PATH" not in REGISTRY:
		ThrowBSOD(window, corrupted_key("LOGO_PATH"))
		sys.exit(1)

	logo_size = 128

	try:
		logo = ImageTk.PhotoImage(
			Image.open(
				REGISTRY["LOGO_PATH"]
			).resize(
				(logo_size, logo_size),
				Image.NEAREST
			)
		)
	except:
		ThrowBSOD(window, "Logo image not found")

	# Displaying it
	logo_label = tk.Label(
		window,
		image=logo,
		bg=REGISTRY["LOADING_BACKGROUND_COLOR"]
	)
	logo_label.place(
		x = WIN_WIDTH // 2 - logo_size //2,
		y = WIN_HEIGHT // 2 - logo_size
	)

	# Clearing memory
	del logo_size

	# ------------------ PROGRESS BAR ------------------
	progress = 0
	current_progress = tk.StringVar()
	current_progress.set("░" * 10)

	# Displaying it
	progress_label = tk.Label(
		window,
		textvariable = current_progress,
		bg = REGISTRY["LOADING_BACKGROUND_COLOR"],
		fg = "white",
		font = ("Impact", 20)
	)
	progress_label.place(
		x = WIN_WIDTH // 2 - 100,
		y = WIN_HEIGHT // 2 + 35
	)

	def increment_progress():
		global progress
		global current_progress
		global logo_label
		current_progress.set("▓" * progress + "░" * (10 - progress))
		progress += 1
		if progress <= 10:
			window.after(randint(100, 300), increment_progress)
		else:
			start_OS(window, REGISTRY)
			progress_label.place_forget()
			progress_label.destroy()
			logo_label.place_forget()
			logo_label.destroy()

	# ------------------ WINDOW DISPLAYING ------------------
	window.after(randint(100, 300), increment_progress)
	window.mainloop()
