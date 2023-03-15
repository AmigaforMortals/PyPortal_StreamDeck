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

# Configuration
BTN_COLS = 4
BTN_ROWS = 3
TOUCH_COOLDOWN = 0.2  # minimum amount of seconds to wait between touch events

IMG_PATH_SPLASH = '/images/Splash.bmp'

IMG_PATH_PAGES = [
    '/images/Page1.bmp',
    '/images/Page2.bmp',
    '/images/Page3.bmp',
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
            getattr(
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
previousTouch = None
previousTouchTime = 0
currentPage = 0

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
    currentTime = time.monotonic()

    # skip if still in touch cooldown
    if currentTime < (previousTouchTime + TOUCH_COOLDOWN):
        continue

    currentTouch = touchScreen.touch_point

    # skip if not being touched or current touch matches the last touch
    if currentTouch is None or currentTouch == previousTouch:
        continue

    # work out which row/col has been pressed
    touchX = math.floor(currentTouch[0] / (board.DISPLAY.width / BTN_COLS))
    touchY = math.floor(currentTouch[1] / (board.DISPLAY.height / BTN_ROWS))

    currentKeyCodes = BTN_PAGE_MAP[currentPage][touchY][touchX]

    # send press/release for key(s) defined in row/col
    if currentKeyCodes == 'prevPage':
        prevPage()
    elif currentKeyCodes == 'nextPage':
        nextPage()
    elif type(currentKeyCodes) in [list, tuple]:
        keyboard.send(*currentKeyCodes)
    else:
        keyboard.send(currentKeyCodes)

    # store the time/touch event to compare against next iteration
    previousTouchTime = currentTime
    previousTouch = currentTouch
