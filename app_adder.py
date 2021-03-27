"""
App adder ; allows you to install/uninstall apps.
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import requests
import os
import json
import zipfile
import shutil

try:
	registry_file = open("../../registry.json", "r")
except FileNotFoundError:
	registry_file = open("registry.json", "r")
REGISTRY = json.load(registry_file)
registry_file.close()

window = tk.Tk()
window.geometry("400x200")
window.title("App adder")
window.iconbitmap("assets/ACOS_Logo.ico")

def get_zip_link(app:str):
	return f"https://raw.githubusercontent.com/megat69/ACOS_Apps/main/{app}/{app}.zip"


# ------------------------- GUI ELEMENTS -------------------------
def install_app():
	r = requests.get(get_zip_link(app_name_entry.get()))
	# If there has been a problem
	if r.status_code != 200:
		message.config(
			text=f"An error occurred with code {r.status_code}." +\
			     ("\nThe app doesn't seem to exist." if r.status_code == 404 else ""),
			fg = "red"
		)
		return

	try:
		os.mkdir("temp")
	except FileExistsError:
		pass
	# ------- Writing the zip -------
	with open(f"temp/{app_name_entry.get()}.zip", "wb") as zip_contents:
		zip_contents.write(r.content)

	# ------- Extracting the zip -------
	with zipfile.ZipFile(f"temp/{app_name_entry.get()}.zip", "r") as zip_ref:
		zip_ref.extractall(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}")

	# ------- Deleting the temp folder -------
	shutil.rmtree("temp")

	# ------- End message -------
	message.config(
		text=f"Correctly installed {app_name_entry.get()}",
		fg="green"
	)
	app_name_entry.delete(0, tk.END)


install_app_button = tk.Button(
	window,
	text = "Install app",
	command = install_app
)
install_app_button.pack()

def uninstall_app():
	if app_name_entry.get() not in os.listdir(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}")\
			or app_name_entry.get() in ("ACOS_Console", "app_browser", "Ideaglue", "textrock", "Micr0n",
				"paintapp", "RegistryVisualizer", "settings", "SYSTEM_Filesystem"):
		message.config(
			text=f"The app {app_name_entry.get()} is not installed.",
			fg="red"
		)
		return

	# ------- CONFIRM -------
	confirm_box = messagebox.askquestion(
		f"Uninstall {app_name_entry.get()}",
		f"Are you sure you want to uninstall {app_name_entry.get()} ?\n"
		"This action cannot be undone.",
		icon = "warning"
	)
	if confirm_box == "no":
		message.config(
			text="Uninstall cancelled.",
			fg="red"
		)
		return

	# ------- App uninstall --------
	shutil.rmtree(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}/{app_name_entry.get()}")

	# ------- End message -------
	message.config(
		text=f"App '{app_name_entry.get()}' uninstalled.",
		fg="black"
	)
	app_name_entry.delete(0, tk.END)

uninstall_app_button = tk.Button(
	window,
	text = "Uninstall app",
	command = uninstall_app
)
uninstall_app_button.pack()

def install_local_app():
	file = filedialog.askopenfilename(filetypes=(("ZIP", "*.zip"),), title="Install app from local file")
	if file == "" or file is None:
		message.config(
			text="Install cancelled.",
			fg="red"
		)
		return

	# ------- App extracting -------
	with zipfile.ZipFile(file, "r") as zip_ref:
		zip_ref.extractall(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}")

	# ------- End message -------
	file = file.split("/")[-1][:-4]
	message.config(
		text=f"App '{file}' installed.",
		fg="green"
	)

install_local_app_button = tk.Button(
	window,
	text = "Install local app",
	command = install_local_app
)
install_local_app_button.pack()

def update_app():
	app_name = app_name_entry.get()
	uninstall_app()
	app_name_entry.insert(0, app_name)
	install_app()

update_app_button = tk.Button(
	window,
	text = "Update app",
	command = update_app
)
update_app_button.pack()

app_name_entry = tk.Entry(
	window
)
app_name_entry.pack(pady=5)

message = tk.Label(window)
message.pack()

window.mainloop()
