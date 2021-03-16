"""
ACOS registry cleanup utility.
"""
import json
import sys
import requests

registry_url = "https://raw.githubusercontent.com/megat69/ACOS/main/registry.json"

try:
	registry_file = open("registry.json", "r")
except:
	print("The registry file hasn't been found.")
	print("Do you want to download it from the ACOS GitHub repository ?\n"
        "All your settings will be lost forever, but your system will"
        " probably work again.\n"
        "If you modified manually any of the keys of the registry, you will need "
        "to make these changes again, otherwise the ACOS might not be functional.\n"
        "Remember key modification is only done at your own risk.")
	# Confirming the update
	confirm = input("Type 'yes' to download a new registry image, or 'no' to cancel.\n")
	while confirm[0].lower() not in ("y", "n"):
		print("Invalid answer.")
		confirm = input("Type 'yes' to download a new registry image, or 'no' to cancel.")

	# Exiting if answer is no
	if confirm[0].lower() == "n":
		print("Update dismissed.")
		sys.exit(0)

	# Otherwise, downloading the registry file from GitHub.
	url = registry_url
	r = requests.get(url)
	existing = r.status_code == 200
	if not existing:
		# Error : File does not exist !
		print("An error occurred.")
		sys.exit(1)
	with open(f"registry.json", "wb") as code:
		code.write(r.content)

	print("Registry rewritten.\nTry booting up the ACOS again.")
	sys.exit(0)
else:
	print("Seemingly no critic error with the registry file.")

REGISTRY = json.load(registry_file)
registry_file.close()

def reset_key(key):
	"""
	Resets a key of the registry.
	:param key: A registry key.
	"""
	global REGISTRY
	# Looking at the file
	url = registry_url
	r = requests.get(url)
	existing = r.status_code == 200
	if not existing:
		# Error : File does not exist !
		print("An error occurred.")
		sys.exit(1)

	# Parsing the GitHub registry
	GitHub_REGISTRY = json.loads(r.content)

	if key not in GitHub_REGISTRY:
		print(f"The registry key '{key}' does not exist, even in the backup registry.")
		return False

	# Resetting the key
	print(f"Resetting the key '{key}'...")
	REGISTRY[key] = GitHub_REGISTRY[key]

	# Writing the file on the disk
	registry_file = open("registry.json", "w")
	json.dump(REGISTRY, registry_file, indent=4)
	registry_file.close()
	print(f"Key '{key}' has been reset.")

def clean_registry_skeletons():
	"""
	Gets the backup registry file on GitHub and compares the keys,
	to see when keys are useless in the computers registry, and delete them.
	"""
	global REGISTRY
	# Looking at the file
	url = registry_url
	r = requests.get(url)
	existing = r.status_code == 200
	if not existing:
		# Error : File does not exist !
		print("An error occurred.")
		sys.exit(1)

	# Parsing the GitHub registry
	GitHub_REGISTRY = json.loads(r.content)

	# If the keys are the exact same, returning there (optimization)
	if REGISTRY.keys() == GitHub_REGISTRY.keys():
		print("No skeletons to clean.")
		return False

	# Going through all the keys in the registry
	temp_dict = {}
	cleaned_keys = []
	for key in REGISTRY.keys():
		if key in GitHub_REGISTRY.keys():
			temp_dict[key] = REGISTRY[key]
		else:
			cleaned_keys.append(key)

	REGISTRY = temp_dict

	registry_file = open("registry.json", "w")
	json.dump(REGISTRY, registry_file, indent=4)
	registry_file.close()

	print("Cleaned keys :")
	for key in cleaned_keys:
		print(f"- {key}")


if __name__ == "__main__":
	clean_registry_skeletons()
