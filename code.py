import time
import board
import displayio
from adafruit_button import Button
from adafruit_pyportal import PyPortal
import adafruit_touchscreen
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# -------Rotate 0:
SIZE = (320, 240)
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(320, 240))

# Show AfM splash screen on startup
pyportal = PyPortal(default_bg="/images/AfM_StreamDeck.bmp")

# Load Button Images
btn_group = displayio.Group()

# This will handle switching Images and Icons
def set_image(group, filename):
    print("Set image to ", filename)
    if group:
        group.pop()

    if not filename:
        return  # we're done, no icon desired
    try:
        if image_file:
            image_file.close
    except NameError:
        pass
    image_file = open(filename, "rb")
    image = displayio.OnDiskBitmap(image_file)
    image_sprite = displayio.TileGrid(image, pixel_shader=getattr(image, 'pixel_shader', displayio.ColorConverter()))
    group.append(image_sprite)
board.DISPLAY.show(btn_group)

set_image(btn_group,"/images/Buttons.bmp")

# Set buttons
btn1 = Keycode.A
btn2 = Keycode.B
btn3 = Keycode.C
btn4 = Keycode.D
btn5 = Keycode.E
btn6 = Keycode.F
btn7 = Keycode.G
btn8 = Keycode.H
btn9 = Keycode.I
btn10 = Keycode.J
btn11 = Keycode.K
btn12 = Keycode.L
btn13 = Keycode.M
btn14 = Keycode.N
btn15 = Keycode.O
btn16 = Keycode.P
btn17 = Keycode.Q
btn18 = Keycode.R
btn19 = Keycode.S
btn20 = Keycode.T
btn21 = Keycode.U
btn22 = Keycode.V
btn23 = Keycode.W
btn24 = Keycode.X

def key_press(btn_num):
    keyboard.press(btn_num)
    keyboard.release(btn_num)

_page_number=1

def load_page_1():
    # if touch is on top row
    if p[1] < 80:
        # Button 1
        if p[0] <80:
            key_press(btn1)
        # Button 2
        elif p[0] >80 and p[0] <160:
            key_press(btn2)
        # Button 3
        elif p[0] >160 and p[0] <240:
            key_press(btn3)
        # Button 4
        elif p[0] >240:
            key_press(btn4)
    #if touch is on middle row
    elif p[1] > 80 and p[1] <160:
        # Button 5
        if p[0] <80:
            key_press(btn5)
        # Button 6
        elif p[0] >80 and p[0] <160:
            key_press(btn6)
        # Button 7
        elif p[0] >160 and p[0] <240:
            key_press(btn7)
        # Button 8
        elif p[0] >240:
            key_press(btn8)
    # if touch is on Bottom row
    elif p[1] >160:
        # Button 9
        #if p[0] <80:
            #key_press(btn9)
        # Button 10
        if p[0] >80 and p[0] <160:
            key_press(btn10)
        # Button 11
        elif p[0] >160 and p[0] <240:
            key_press(btn11)
        # Button 12
        elif p[0] >240:
            key_press(btn12)

def load_page_2():
    # if touch is on top row
    if p[1] < 80:
        # Button 1
        if p[0] <80:
            key_press(btn13)
        # Button 2
        elif p[0] >80 and p[0] <160:
            key_press(btn14)
        # Button 3
        elif p[0] >160 and p[0] <240:
            key_press(btn15)
        # Button 4
        elif p[0] >240:
            key_press(btn16)
    #if touch is on middle row
    elif p[1] > 80 and p[1] <160:
        # Button 5
        if p[0] <80:
            key_press(btn17)
        # Button 6
        elif p[0] >80 and p[0] <160:
            key_press(btn18)
        # Button 7
        elif p[0] >160 and p[0] <240:
            key_press(btn19)
        # Button 8
        elif p[0] >240:
            key_press(btn20)
    # if touch is on Bottom row
    elif p[1] >160:
        # Button 9
        #if p[0] <80:
            #key_press(btn21)
        # Button 10
        if p[0] >80 and p[0] <160:
            key_press(btn22)
        # Button 11
        elif p[0] >160 and p[0] <240:
            key_press(btn23)
        # Button 12
        elif p[0] >240:
            key_press(btn24)

# must wait at least this long between touch events
TOUCH_COOLDOWN = 0.1  # seconds

#time.sleep(1)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# previous iteration touch events
_previous_touch = None

# last time a touch occured
_previous_touch_time = 0

# main loop
while True:
    # check for touch events
    p = ts.touch_point
    _now = time.monotonic()
    # if touch cooldown time has elapsed
    if _now >= _previous_touch_time + TOUCH_COOLDOWN:
        # if there is a touch
        if p and not _previous_touch:
            # store the time to compare with next iteration
            _previous_touch_time = _now
            if p[1] <160 or p[0] >80:
                if _page_number<=1:
                    load_page_1()
	        elif _page_number>=2:
        	    load_page_2()
            elif p[1] >160 and p[0] <80:
                if _page_number<=1:
                    load_page_2()
                    set_image(btn_group,"/images/Buttons2.bmp")
		    _page_number=2
	        elif _page_number>=2:
        	    load_page_2()
		    set_image(btn_group,"/images/Buttons.bmp")
		    _page_number=1

    # store previous touch event t compare with next iteration
    _previous_touch = p
