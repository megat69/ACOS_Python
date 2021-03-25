from .. import software_api
import tkinter as tk
from functools import partial
import os

app_icon = "ACOS_Logo.png"
software_name = "ACOS Console"
software_dir = "ACOS_console"
is_GUI = True
default_size = (520, 300)
min_size = default_size
max_size = None

current_dir = f"ROOT/{software_api.REGISTRY['USERS_FOLDER']}/{software_api.current_user}/"

def on_app_launch(frame:tk.Frame, width:int=default_size[0], height:int=default_size[1]):
	frame.config(bg = "black")
	params = {
		"bg": "black",
		"fg": "white",
		"anchor": "w",
		"font": ("Consolas", 10)
	}
	welcome_message = tk.Label(
		frame,
		text = f"ACOS console version {software_api.os_version}. TheAssassin creation. No rights reserved.\n",
		**params
	).pack(
		fill = tk.X,
		pady=10
	)

	# Inputter
	globals()["inputter_frame"] = tk.Frame(frame, bg = params["bg"])
	globals()["inputter_label"] = tk.Label(globals()["inputter_frame"], text = ">>> ", **params)
	globals()["inputter_label"].grid(row=0, column=0, sticky="w")
	globals()["main_inputter"] = tk.Entry(
		globals()["inputter_frame"],
		insertbackground=params["fg"],
		bg = params["bg"],
		fg = params["fg"],
		font = params["font"],
		borderwidth = 0,
		highlightthickness = 0,
		width = round(width * 0.4)
	)
	globals()["main_inputter"].bind("<Return>", partial(treat_input, frame, params))
	globals()["main_inputter"].grid(row=0, column=1, sticky="w")
	globals()["inputter_frame"].pack(fill=tk.X)

def treat_input(frame, params, event):
	global current_dir

	def display(text, *args, color="white"):
		def without_keys(d, keys):
			return {x: d[x] for x in d if x not in keys}
		wanted_params = without_keys(params, "fg")
		wanted_params["fg"] = color

		displayed_text = tk.Label(
			frame,
			text = text + " " + software_api.recreate_string(args, " ") if len(args) > 0 else text,
			**wanted_params
		).pack(fill=tk.X)

	def exit_function():
		# Resetting the inputter and re-displaying it
		globals()["main_inputter"].delete(0, tk.END)
		globals()["inputter_frame"].pack(fill=tk.X, pady=10)

	# Removing sight of the inputter
	globals()["inputter_frame"].pack_forget()
	# Displaying the command as text
	display(">>>  " + globals()["main_inputter"].get())
	user_command = globals()["main_inputter"].get()

	# Treating the command
	if user_command.lower().startswith("dir"):
		display(current_dir)
		for file in os.listdir(current_dir):
			if not file.startswith("."):
				display(file)
	elif user_command.lower().startswith("cd"):
		user_command = user_command.replace("cd ", "", 1)

		# Getting all the given subfolders
		user_command = user_command.split("/")
		# As long as the user wants to get back in the files
		while user_command[0] == "..":
			# If it is not the root folder
			if not current_dir in ("ROOT", "ROOT/"):
				current_dir = current_dir.split("/")
				while current_dir[-1] == "":
					current_dir.pop()
				current_dir.pop()
				current_dir = software_api.recreate_string(current_dir, "/")
				user_command.pop(0)
			else:  # If it is root folder and can't go further
				display("Unable to go further than the root folder.", color="red")
				exit_function()
				return

		# Removing empty elements in the list
		for element in user_command:
			if element == "":
				user_command.remove(element)

		# We change the current directory
		temp = current_dir + software_api.recreate_string(user_command, "/")
		if not os.path.exists(temp):
			display("Unexisting path :", temp, color="red")
			exit_function()
			return
		current_dir = temp
		del temp

		# While it ends with bad slashes, we remove them.
		while current_dir.endswith("//"):
			current_dir = software_api.remove_suffix(current_dir)

	elif user_command.lower().startswith("cls"):
		software_api.destroy_all_widgets(frame)

		# Recreating Inputter
		globals()["inputter_frame"] = tk.Frame(frame, bg=params["bg"])
		globals()["inputter_label"] = tk.Label(globals()["inputter_frame"], text=">>> ", **params)
		globals()["inputter_label"].grid(row=0, column=0, sticky="w")
		globals()["main_inputter"] = tk.Entry(
			globals()["inputter_frame"],
			insertbackground=params["fg"],
			bg=params["bg"],
			fg=params["fg"],
			font=params["font"],
			borderwidth=0,
			highlightthickness=0,
			width=round(frame.winfo_width() * 0.4)
		)
		globals()["main_inputter"].bind("<Return>", partial(treat_input, frame, params))
		globals()["main_inputter"].grid(row=0, column=1, sticky="w")
		globals()["inputter_frame"].pack(fill=tk.X)

	elif user_command.lower().startswith("help"):
		for line in """Help :
		- 'dir' : Shows the content of the current directory.
		- 'cd <relative path>' : Changes the current directory to the specified relative path.
		- 'cls' : Clears the screen.""".split("\n"):
			display(line.replace("\t", ""))

	else:
		display("Unknown command : " + user_command, color="red")

	exit_function()
