"""
Updater script for ACOS.
"""
import os
import shutil

def rewriter():
	# Rewriting the old files
	for element in os.listdir("update"):

		if element != "updater.py":
			print(f"Rewriting '{element}'...")
			old_file = open(element, "w", encoding="utf-8")
			new_file = open("update/" + element, "r", encoding="utf-8")
			try:
				old_file.writelines(new_file.readlines())
			except:
				pass
			old_file.close()
			new_file.close()
			print(f"{element} rewritten.")

	shutil.rmtree("update")

if __name__ == "__main__":
	rewriter()
