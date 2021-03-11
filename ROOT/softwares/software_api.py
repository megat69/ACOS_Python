"""
A bunch of APIs for the ACOS sotwares.
"""
import json

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

def api_params(function):
	"""
	Decorator function, used to give the app access a
	read-only registry and the current username.
	"""
	global REGISTRY
	global current_user
	def wrapper(*args, **kwargs):
		return function(*args, **kwargs)
	return wrapper

def refresh_registry():
	global REGISTRY
	try:
		registry_file = open("../../registry.json", "r")
	except FileNotFoundError:
		registry_file = open("registry.json", "r")
	REGISTRY = json.load(registry_file)
	registry_file.close()

def notify(title:str, text:str):
	pass
