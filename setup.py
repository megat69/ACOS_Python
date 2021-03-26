import os
import platform

suffix = '' if platform.platform() == "Windows" else '3'

os.system(f"pip{suffix} install -r requirements.txt")
