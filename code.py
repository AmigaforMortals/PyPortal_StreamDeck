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

# Load 
group = displayio.Group()
#group.x = 0
#group.y = 0

image_file = open("/images/Buttons.bmp", "rb")
image = displayio.OnDiskBitmap(image_file)
image_sprite = displayio.TileGrid(image, pixel_shader=getattr(image, 'pixel_shader', displayio.ColorConverter()))

group.append(image_sprite)
board.DISPLAY.show(group)

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

# must wait at least this long between touch events
TOUCH_COOLDOWN = 0.5  # seconds

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
            # if touch is on top row
            if p[1] < 80:
                # Button 1
                if p[0] <80:
                    keyboard.press(btn1)
                    keyboard.release(btn1)
                # Button 2
                elif p[0] >80 and p[0] <160:
                    keyboard.press(btn2)
                    keyboard.release(btn2)
                # Button 3
                elif p[0] >160 and p[0] <240:
                    keyboard.press(btn3)
                    keyboard.release(btn3)
                # Button 4
                else:
                    keyboard.press(btn4)
                    keyboard.release(btn4)
	    #if touch is on middle row
	    elif p[1] > 80 and p[1] <160:
		# Button 5
                if p[0] <80:
                    keyboard.press(btn5)
                    keyboard.release(btn5)
                # Button 6
                elif p[0] >80 and p[0] <160:
                    keyboard.press(btn6)
                    keyboard.release(btn6)
                # Button 7
                elif p[0] >160 and p[0] <240:
                    keyboard.press(btn7)
                    keyboard.release(btn7)
                # Button 8
                else:
                    keyboard.press(btn8)
                    keyboard.release(btn8)
            # if touch is on Bottom row
	    else:
		# Button 9
                if p[0] <80:
                    keyboard.press(btn9)
                    keyboard.release(btn9)
                # Button 10
                elif p[0] >80 and p[0] <160:
                    keyboard.press(btn10)
                    keyboard.release(btn10)
                # Button 11
                elif p[0] >160 and p[0] <240:
                    keyboard.press(btn11)
                    keyboard.release(btn11)
                # Button 12
                else:
                    keyboard.press(btn12)
                    keyboard.release(btn12)

    # store previous touch event t compare with next iteration
    _previous_touch = p
