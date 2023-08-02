from ctypes.wintypes import BOOL, HWND, LONG
import ctypes
from ctypes import windll
from PIL import Image, ImageTk

windll.shcore.SetProcessDpiAwareness(1)

# Defining functions
GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW

# Constants
GWL_STYLE = -16
GWLP_HWNDPARENT = -8
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000

# COLORS
TOP_BAR_COLOR = "#FFFFFF"
LEFT_CANVAS_COLOR = "#2E3859"
MAIN_WINDOW_COLOR = "#131E40"


#LEFT_CANVAS_COLOR = "#131E40"
#MAIN_WINDOW_COLOR = "#2E3859"

# DIMENSIONS
WINDOW_HEIGHT = 1250
WINDOW_WIDTH = 2000
TOP_BAR_HEIGHT = 75
TOP_BAR_WIDTH = 1250
LEFT_CANVAS_WIDTH = 630
LEFT_CANVAS_HEIGHT = 1250
CAMERA_HEIGHT = 315
CAMERA_WIDTH = 560

LINE_MAX_CHARS = 37

CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720


# Helper function.
def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)


def break_str(text, max_chars):
    words = text.split()
    current_len, current_words = 0, 0
    final = ""
    for i in range(0, len(words)):
        if current_len + len(words[i]) > max_chars:
            if current_words > 0:
                final += "\n"
            current_len = 0
            current_words = 0

        if current_words > 0:
            final += " "
        final += words[i]
        current_len += len(words[i])
        current_words += 1
    return final
