import os
import platform

system = platform.system()

os.system('pyinstaller -F -w main.py')
