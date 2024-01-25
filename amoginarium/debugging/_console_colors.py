"""
_console_colors.py
25. January 2024

defines a few console colors

Author:
Nilusink
"""
import os


if os.name == "nt":
    os.system("color")


BLACK = '\u001b[30m'
WHITE = '\u001b[37m'
MAGENTA = '\u001b[35m'
BLUE = '\u001b[34m'
CYAN = '\u001b[36m'
GREEN = '\u001b[32m'
ORANGE = '\u001b[33m'
YELLOW = '\033[93m'
RED = '\u001b[31m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

    
