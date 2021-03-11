"""
Updater script for ACOS.
"""
import os

def rewriter(path:str):
	# Rewriting the old files
	for element in os.listdir(path):
		if os.path.isdir(element):
			rewriter(path + "/" + element)

		if element != "updater.py":
			print(f"Rewriting '{path}/{element}'...")
			old_file = open(path + "/" + element, "w", encoding="utf-8")
			new_file = open("update/" + path + "/" + element, "r", encoding="utf-8")
			try:
				old_file.writelines(new_file.readlines())
			except:
				pass
			old_file.close()
			new_file.close()
			print(f"{path}/{element} rewritten.")

if __name__ == "__main__":
	rewriter("update")
