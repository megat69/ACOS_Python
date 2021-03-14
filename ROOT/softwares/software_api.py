"""
A bunch of APIs for the ACOS sotwares.
"""
import json
import tkinter as tk

# os.chdir(os.path.dirname(os.path.realpath(__file__)))
# os.chdir("../../../")

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

def get_all_widgets(window:tk.Frame):
	_list = window.winfo_children()

	for item in _list:
		if item.winfo_children():
			_list.extend(item.winfo_children())

	return _list


def destroy_all_widgets(window:tk.Frame):
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

def recreate_string(variable:(list, tuple), char_in_between:str=""):
    """
    Recreates a string from a list.
    Parameter 'variable' (list) : The list to put together to a string.
    Parameter 'char_in_between' (str) : The char to put between the elements to recompose. Nothing by default.
    """
    temp_str = ""
    for element in variable:
        temp_str += str(element) + char_in_between
    return temp_str

def remove_suffix(variable:str, condition:bool=True, chars_amount:int=1):
    """
    Removes the suffix of a string.
    Parameter 'variable' (str) : The text where the suffix has to be removed.
    Parameter 'chars_amount' (int) : Default : 1. Number of chars to remove.
    Parameter 'condition' (bool) : Default : True. Will only remove if the condition is True.
    """
    if condition is True:  # If the condition is respected
        variable = variable[:-chars_amount]  # Suffix gets removed
    return variable

def remove_prefix(variable:str, condition:bool=True, chars_amount:int=1):
    """
        Removes the prefix of a string.
        Parameter 'variable' (str) : The text where the prefix has to be removed.
        Parameter 'chars_amount' (int) : Default : 1. Number of chars to remove.
        Parameter 'condition' (bool) : Default : True. Will only remove if the condition is True.
        """
    if condition is True:  # If the condition is respected
        variable = variable[chars_amount:len(variable)]  # Prefix gets removed
    return variable
