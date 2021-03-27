"""
Updater script for ACOS.
"""
import json

import requests
import os
import zipfile
import shutil

def download_repo(URL:str, folder:str, files_to_delete:(list, tuple)=(".gitattributes", "README.md"), log:bool=True, notify_function=print, *args, **kwargs):
	"""
	Downloads the specified repository into the specified folder.
	:param URL: The URL of the repository main archive.
	:param folder: The folder to place the repository in.
	:param files_to_delete: The files to delete after downloading the repository. DEFAULT : '.gitattributes', 'README.md'
	:param log: Log the informations in the console. DEFAULT : True
	:param notify_function: The function that will get the log as argument. DEFAULT : print()
	"""
	if log: notify_function("Downloading... This might take a while.", *args, **kwargs)
	r = requests.get(URL)
	assert r.status_code == 200, "Something happened.\nStatus code : " + str(r.status_code)

	if folder == "":
		folder = "_"

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

def get_zip_link(username:str, repository:str, branch:str="main"):
	"""
	Gets the link to the main zip of a repository.
	:param username: The username of the repository owner.
	:param repository: The repository name.
	:param branch: The branch to download. Default : 'main'.
	:return: The link to the zip.
	"""
	return f"https://github.com/{username}/{repository}/archive/refs/heads/{branch}.zip"

def move_files(source_dir:str):
	for filename in os.listdir("_"):
		try:  # Folder
			if "ROOT" in filename:
				continue
			shutil.rmtree(filename)
		except NotADirectoryError:  # File
			os.remove(filename)
		except PermissionError:
			continue
		if filename is not "registry.json":
			shutil.move(os.path.join(source_dir, filename), filename)
		else:
			f = open("registry.json", "r")
			registry = json.load(f)
			f.close()
			f = open("_/registry.json", "r")
			new_registry = json.load(f)
			f.close()

			for key in new_registry:
				if key not in registry:
					registry[key] = new_registry[key]

			f = open("registry.json", "w")
			json.dump(registry, f, indent=4)
			f.close()


if __name__ == "__main__":
	download_repo(get_zip_link("megat69", "ACOS"), "", (".gitattributes", "README.md", "LICENSE"))
	print("Replacing files...")
	move_files("_/")
	shutil.rmtree("_/")
	print("Update applied done !")
