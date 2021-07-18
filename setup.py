import os
import platform
import shutil
import requests
import json
import zipfile

suffix = '' if platform.platform() == "Windows" else '3'

os.system(f"pip{suffix} install -r requirements.txt")
if os.name != "nt":
  os.system("sudo apt-get install python3-tk")
  os.system("sudo apt-get install python3-pil python3-pil.imagetk")

def download_repo(URL:str, folder:str, files_to_delete:(list, tuple)=(".gitattributes", "README.md"), log:bool=True, notify_function=print, *args, **kwargs):
	"""
	Downloads the specified repository into the specified folder.
	:param URL: The URL of the repository main archive.
	:param folder: The folder to place the repository in.
	:param files_to_delete: The files to delete after downloading the repository. DEFAULT : '.gitattributes', 'README.md'
	:param log: Log the informations in the console. DEFAULT : True
	"""
	if log: notify_function("Downloading... This might take a while.", *args, **kwargs)
	r = requests.get(URL)
	assert r.status_code == 200, "Something happened.\nStatus code : " + str(r.status_code)

	if log: notify_function("Writing the zip...", *args, **kwargs)
	# Writing the zip
	with open(f"{folder}.zip", "wb") as code:
		code.write(r.content)
		code.close()

	# Creating a folder for the zip content
	if not os.path.exists(folder):
		os.mkdir(folder)

	if log: notify_function("Extracting...", *args, **kwargs)
	# Extracting the zip
	with zipfile.ZipFile(f"{folder}.zip", "r") as zip_ref:
		zip_ref.extractall(folder)

	if log: notify_function("Moving the files...", *args, **kwargs)
	suffix = URL.split("/")[-1].replace(".zip", "", 1)
	repo_name = URL.split("/")[4]
	# Moving the file to parent
	for filename in os.listdir(os.path.join(folder, f'{repo_name}-{suffix}')):
		shutil.move(os.path.join(folder, f'{repo_name}-{suffix}', filename), os.path.join(folder, filename))
	# Deleting unnecessary files
	shutil.rmtree(f"{folder}/{repo_name}-{suffix}")
	os.remove(f"{folder}.zip")
	for file in files_to_delete:
		try:
			os.remove(f"{folder}/{file}")
		except FileNotFoundError:
			pass

	if log: notify_function("Download complete !", *args, **kwargs)

with open("registry.json", "r") as f:
	REGISTRY = json.load(f)
# Installing GhostScript if not installed
if not os.path.exists(f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}/paintapp/gs9.53.3/"):
	print("Downloading GhostScript...")
	download_repo("https://github.com/megat69/GhostScript/archive/refs/heads/main.zip", f"ROOT/{REGISTRY['SOFTWARES_FOLDER']}/paintapp/gs9.53.3")
else:
	print("GhostScript already installed.")
