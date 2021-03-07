"""
Utility to clean corrupted keys of the registry or reset the software.
"""
import json
from main import *
import tkinter as tk

try:
	registry_file = open("registry.json", "r", encoding="utf-8")
except FileNotFoundError:
	ThrowBSOD(tk.Tk(), "Registry could not be loaded.")
except:
	ThrowBSOD(tk.Tk(), "An unknown error occured while trying to open registry.")
REGISTRY = json.load(registry_file)
registry_file.close()

def check_key(key:str, supposed_value=None):
	"""
	Checks the required key in the registry.
	"""
	# Detects if the key is not in the registry
	if key not in REGISTRY:
		print(f"The key '{key}' is not in the registry.")
		if supposed_value is not None:
			REGISTRY[key] = supposed_value
			json.dumps(REGISTRY, "registry.json")
			return True
		else:
			print("No given value to replace with.")
			return False

	elif REGISTRY[key] != supposed_value and supposed_value is not None:
		# If the key doesn't have the right value
		REGISTRY[key] = supposed_value
		json.dumps(REGISTRY, "registry.json")
		return True

	else:
		# Else
		print(f"No error found, key '{key}' equals to '{REGISTRY[key]}'.")
		return False

if __name__ == "__main__":
	check_key("CURRENT_THEME")
