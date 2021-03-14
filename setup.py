import os
import platform

if platform.platform() == "Windows":
	suffix = ''
else:
	suffix = '3'

os.system(f"pip{suffix} install -r requirements.txt")
