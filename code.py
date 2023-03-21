import adafruit_touchscreen
import board
import displayio
import math
import time
import usb_hid

from adafruit_button import Button
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_pyportal import PyPortal
from secrets import secrets

# Configuration
BTN_COLS = 4
BTN_ROWS = 3
THEME = secrets['streamDeckTheme'] or 'AmigaForMortals'

IMG_PATH_SPLASH = '/config/' + THEME + '/img/Splash.bmp'

IMG_PATH_PAGES = [
    '/config/' + THEME + '/img/Page1.bmp',
    '/config/' + THEME + '/img/Page2.bmp',
    '/config/' + THEME + '/img/Page3.bmp',
]

BTN_PAGE_MAP = [
    [
        [Keycode.A, Keycode.B, Keycode.C, Keycode.D],
        [Keycode.E, Keycode.F, Keycode.G, Keycode.H],
        ['prevPage', Keycode.J, Keycode.K, 'nextPage'],
    ],
    [
        [Keycode.M, Keycode.N, Keycode.O, Keycode.P],
        [Keycode.Q, Keycode.R, Keycode.S, Keycode.T],
        ['prevPage', Keycode.V, Keycode.W, 'nextPage'],
    ],
    [
        [(Keycode.SHIFT, Keycode.A), (Keycode.SHIFT, Keycode.B), (Keycode.SHIFT, Keycode.C), (Keycode.SHIFT, Keycode.D)],
        [(Keycode.SHIFT, Keycode.E), (Keycode.SHIFT, Keycode.F), (Keycode.SHIFT, Keycode.G), (Keycode.SHIFT, Keycode.H)],
        ['prevPage', (Keycode.SHIFT, Keycode.J), (Keycode.SHIFT, Keycode.K), 'nextPage'],
    ],
]

# Functions
def setPage(index):
    global currentPage

    if index >= len(IMG_PATH_PAGES):
        return

    currentPage = index

    if btnGroup:
        btnGroup.pop()

    # Load current page button bitmap
    image = displayio.OnDiskBitmap(
        open(IMG_PATH_PAGES[currentPage], "rb")
    )

    btnGroup.append(
        displayio.TileGrid(
            image,
            pixel_shader = getattr(
                image,
                'pixel_shader',
                displayio.ColorConverter()
            )
        )
    )

    board.DISPLAY.show(btnGroup)

def prevPage():
    if currentPage > 0:
        setPage(currentPage - 1)
    else:
        setPage(len(IMG_PATH_PAGES) - 1)

def nextPage():
    if currentPage < len(IMG_PATH_PAGES) - 1:
        setPage(currentPage + 1)
    else:
        setPage(0)

# Configure initial values
currentPage = 0
currentTouchX = None
currentTouchY = None

# Initialise keyboards
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Initialise touchscreen
touchScreen = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration = (
        (5200, 59000),
        (5800, 57000)
    ),
    size = (
        board.DISPLAY.width,
        board.DISPLAY.height
    )
)

# Show splash image on startup
pyportal = PyPortal(
    default_bg = IMG_PATH_SPLASH
)

# Initialise button image group
btnGroup = displayio.Group()

setPage(currentPage)

# main loop
while True:
    currentTouch = touchScreen.touch_point

    # reset current X/Y values if screen is not being touched
    if currentTouch is None:
        currentTouchX = None
        currentTouchY = None
        continue

    # skip if we've already handled the current touch
    if type(currentTouchX) is int and type(currentTouchY) is int:
        continue

    # work out which button row/col is being pressed
    currentTouchX = math.floor(currentTouch[0] / (board.DISPLAY.width / BTN_COLS))
    currentTouchY = math.floor(currentTouch[1] / (board.DISPLAY.height / BTN_ROWS))

    # look up the button action based on the X/Y values
    currentButtonAction = BTN_PAGE_MAP[currentPage][currentTouchY][currentTouchX]

    # Trigger a function or send press/release for key(s) defined for current button action
    if currentButtonAction == 'prevPage':
        prevPage()
    elif currentButtonAction == 'nextPage':
        nextPage()
    elif type(currentButtonAction) in [list, tuple]:
        keyboard.send(*currentButtonAction)
    else:
        keyboard.send(currentButtonAction)
