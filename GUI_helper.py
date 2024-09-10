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

PLAYER_CANVAS_COLOR = "#FFFFFF"

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

BOT_TEXT_MAX_HEIGHT = 230
BOT_TEXT_MAX_WIDTH = WINDOW_WIDTH - LEFT_CANVAS_WIDTH - 40

LINE_MAX_CHARS = 35

CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720

CARD_HEIGHT = 65
CARD_WIDTH = LEFT_CANVAS_WIDTH - 120
SCORE_SQUARE_SIZE = CARD_HEIGHT

CARD_NORMAL_BG = "#2f52c5"
CARD_SPEAKER_BG = "#2F97C5"
CARD_SCORE_BG = "#3962e9"
CARD_TEXT_COLOR = "#FFFFFF"

CARD_FONT_SIZE = 70
# Helper function.
def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)