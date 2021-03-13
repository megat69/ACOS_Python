"""
A bunch of APIs for the ACOS sotwares.
"""
import json
import tkinter as tk

# The registry
try:
	registry_file = open("../../registry.json", "r")
except FileNotFoundError:
	registry_file = open("registry.json", "r")
REGISTRY = json.load(registry_file)
registry_file.close()

# The current user
try:
	general_data_file = open("../../general_data.json", "r")
except FileNotFoundError:
	general_data_file = open("general_data.json", "r")
general_data = json.load(general_data_file)

current_user = general_data["last_connected_user"]
os_version = general_data["version"]

general_data_file.close()

__window = None

def __set_window(win):
	global __window
	__window = win

def refresh_registry():
	global REGISTRY
	try:
		registry_file = open("../../registry.json", "r")
	except FileNotFoundError:
		registry_file = open("registry.json", "r")
	REGISTRY = json.load(registry_file)
	registry_file.close()

def notify(title:str, text:str):
	"""
	Creates a notification of the user desktop.
	"""
	global __window

	temp_text = [text[i:i+22] for i in range(0, len(text), 22)]
	text = ""
	for i in range(len(temp_text)):
		temp_text[i] += "\n"
		text += temp_text[i]
	del temp_text

	globals()["notification"] = tk.Frame(
		__window
	)
	notification_title = tk.Label(
		globals()["notification"],
		text = title,
		font = ("Impact", 16)
	)
	notification_title.pack()
	notification_message = tk.Label(
		globals()["notification"],
		text = text,
		font = ("Calibri", 12)
	)
	notification_message.pack()

	height = 120
	width = 240

	globals()["notification"].place(
		width = width,
		height = height,
		x = __window.winfo_width() - 10 - width,
		y = __window.winfo_height() - 10 - height
	)

	def destroy_notification(notification:tk.Frame):
		notification.place_forget()
		notification.destroy()

	try:
		__window.after(REGISTRY["NOTIFICATION_STAYING_TIME"], destroy_notification, globals()["notification"])
	except:
		from ...main import ThrowBSOD, corrupted_key
		ThrowBSOD(__window, corrupted_key("NOTIFICATION_STAYING_TIME"))

