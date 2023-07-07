import adafruit_touchscreen
import board
import displayio
import json
import math
import time
import usb_hid

from adafruit_button import Button
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from secrets import secrets

debugging = secrets.get('streamDeckDebug', 0)

# Theme Configuration
theme = secrets.get('streamDeckTheme', 'Default')

with open('/config/{}/settings.json'.format(theme)) as themeJSON:
	themeConfig = json.load(themeJSON)

# Image Configuration
imgPath = '/config/{}/img/'.format(theme)

# Functions
def refreshDisplay():
	if board.DISPLAY.auto_refresh:
		return

	board.DISPLAY.refresh()

def getCurrentTouch():
	time.sleep(0.05)
	touch = touchScreen.touch_point

	if touch:
		return {
			'x': math.floor(touch[0] / (board.DISPLAY.width / getPageColumns())),
			'y': math.floor(touch[1] / (board.DISPLAY.height / getPageRows()))
		}
	else:
		return {
			'x': None,
			'y': None
		}

def getCurrentButton():
	return themeConfig['pages'][currentPage][currentTouch['y']][currentTouch['x']]

def getKeyCode(value):
	return getattr(Keycode, value)

def getPageRows():
	return len(themeConfig['pages'][currentPage])

def getPageColumns():
	return len(themeConfig['pages'][currentPage][0])

def getTileWidth():
	return math.floor(board.DISPLAY.width / getPageColumns())

def getTileHeight():
	return math.floor(board.DISPLAY.height / getPageRows())

def setBacklight(value):
	value = max(0, min(1.0, value))
	board.DISPLAY.brightness = value

	if debugging:
		print('Backlight: ' + str(board.DISPLAY.brightness))

def transitionIn():
	if themeConfig.get('transitionType', None) is None:
		return

	transitionStep = themeConfig.get('transitionStep', 0.1)
	transitionSpeed = themeConfig.get('transitionSpeed', 0.05)

	if themeConfig.get('transitionType', None) is 'fade':
		fadeIn(
			transitionStep,
			transitionSpeed
		)

def transitionOut():
	if themeConfig.get('transitionType', None) is None:
		return

	transitionStep = themeConfig.get('transitionStep', 0.1)
	transitionSpeed = themeConfig.get('transitionSpeed', 0.05)

	if themeConfig.get('transitionType', None) is 'fade':
		fadeOut(
			transitionStep,
			transitionSpeed
		)

def fadeIn(step = 0.1, speed = 0.05):
	setBacklight(0)
	time.sleep(speed)

	while board.DISPLAY.brightness < 1:
		setBacklight(board.DISPLAY.brightness + step)
		time.sleep(speed)

def fadeOut(step = 0.1, speed = 0.05):
	setBacklight(1)
	time.sleep(speed)

	while board.DISPLAY.brightness > 0:
		setBacklight(board.DISPLAY.brightness - step)
		time.sleep(speed)

def setTile(touch, state = 0, refreshAfterUpdate = 1):
	if type(touch['x']) is int and type(touch['y']) is int:
		i = (touch['y'] * getPageColumns()) + touch['x']
		btn = themeConfig['pages'][currentPage][touch['y']][touch['x']]["button"]
		btnGrid[i] = themeConfig['buttons'][btn][state]

		if refreshAfterUpdate:
			refreshDisplay()

def setPage(index, refreshAfterUpdate = 1):
	global currentTouch
	global currentPage

	if index < 0 or index >= len(themeConfig['pages']):
		return

	currentPage = index

	if debugging:
		print('Current page: ' + str(currentPage))

	for tileY in range(0, getPageRows()):
		for tileX in range(0, getPageColumns()):
			setTile(
				{
					'x': tileX,
					'y': tileY
				},
				refreshAfterUpdate = refreshAfterUpdate
			)

def prevPage():
	if currentPage > 0:
		setPage(currentPage - 1)
	else:
		setPage(len(themeConfig['pages']) - 1)

def nextPage():
	if currentPage < len(themeConfig['pages']) - 1:
		setPage(currentPage + 1)
	else:
		setPage(0)

def displaySplashScreen():
	if themeConfig.get('images', {}).get('splash', None) is None:
		return

	if debugging:
		print('Displaying Splash Screen')

	setBacklight(0)

	transitionStep = themeConfig.get('transitionStep', 0.1)
	transitionSpeed = themeConfig.get('transitionSpeed', 0.05)

	splash = displayio.OnDiskBitmap(
		imgPath + themeConfig.get('images', {}).get('splash', 'Splash.bmp')
	)

	splashGrid = displayio.TileGrid(
		splash,
		pixel_shader = splash.pixel_shader
	)

	displayGroup.append(
		splashGrid
	)

	refreshDisplay()

	fadeIn(
		transitionStep,
		transitionSpeed
	)

	time.sleep(3)

	fadeOut(
		transitionStep,
		transitionSpeed
	)

	displayGroup.remove(
		splashGrid
	)

	refreshDisplay()

# Turn the auto refreshing of the dispaly on/off
board.DISPLAY.auto_refresh = bool(themeConfig.get('autoRefresh', True))

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

# Configure initial values
currentPage = 0
currentTouch = getCurrentTouch()
previousTouch = currentTouch
currentButton = None
previousButton = None
timeTouched = None

btns = displayio.OnDiskBitmap(
	imgPath + themeConfig.get('images', {}).get('buttons', 'Buttons.bmp')
)

btnVariations = math.floor(btns.width / (board.DISPLAY.width / getPageColumns()));

# Initialise keyboards
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Initialise display group
displayGroup = displayio.Group()

board.DISPLAY.show(
	displayGroup
)

# Show splash image on startup
displaySplashScreen()

# Turn backlight off
if board.DISPLAY.brightness > 0:
	setBacklight(0)

btnGrid = displayio.TileGrid(
	btns,
	pixel_shader = btns.pixel_shader,
	width = getPageColumns(),
	height = getPageRows(),
	tile_width = getTileWidth(),
	tile_height = getTileHeight()
)

displayGroup.append(
	btnGrid
)

setPage(currentPage)

fadeIn(
	themeConfig.get('transitionStep', 0.1),
	themeConfig.get('transitionSpeed', 0.05)
)

# main loop
while True:
	currentTime = time.monotonic()

	# make a note of the previous touch state
	previousTouch = currentTouch

	# get the current touch state
	currentTouch = getCurrentTouch()

	# check button up - reset stuff when the touch has been released
	if previousTouch != currentTouch and type(previousTouch['x']) is int and type(previousTouch['y']) is int:
		setTile(
			previousTouch
		)

		# if a previously-touched button is used for pagination, trigger it
		if previousButton and currentTouch['x'] is None and currentTouch['y'] is None:
			buttonPage = previousButton.get('page', None)

			if buttonPage is not None:
				transitionOut()

				# perform a pagination action if pagination is enabled
				if buttonPage in ['prev', 'previous']:
					prevPage()
				elif buttonPage == 'next':
					nextPage()
				elif type(buttonPage) is int:
					setPage(buttonPage)

				transitionIn()

		previousButton = None
		timeTouched = None

	# check button down - trigger actions when current/previous touches match (helps to filter out inconsistencies)
	elif previousTouch == currentTouch and type(currentTouch['x']) is int and type(currentTouch['y']) is int:
		if timeTouched is None:
			timeTouched = currentTime

		# get the current button
		currentButton = getCurrentButton()

		# unless specified to repeat after a defined delay, skip triggering the button if we've previously triggered it
		if currentButton == previousButton:
			repeatAfter = previousButton.get('repeatAfter', themeConfig.get('repeatAfter', None))

			if repeatAfter is None or currentTime < (timeTouched + repeatAfter):
				continue
			else:
				timeTouched = currentTime

		if debugging:
			print(currentButton)

		# set the tile for the button currently being touched
		setTile(
			currentTouch,
			1
		)

		# get the button's keys
		buttonKeyCodes = currentButton.get('keyCodes', None)

		if type(buttonKeyCodes) is list:
			keyboard.send(
				*map(getKeyCode, buttonKeyCodes)
			)
		elif type(buttonKeyCodes) is str:
			keyboard.send(
				getKeyCode(buttonKeyCodes)
			)

		# make a note of what button we've just used
		previousButton = currentButton
