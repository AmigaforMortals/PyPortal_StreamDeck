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

def refreshAfterTileUpdate():
	return int(themeConfig.get('displayRefreshMode', 'page') == 'tile')

def isIdle():
	idleDuration = themeConfig.get('idle', {}).get('duration', None)

	if idleDuration is None or currentTime < (timeStateChanged + idleDuration):
		return 0

	return 1

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

def sendKeyCodes(keyCodes):
	if keyCodes is None:
		return
	elif type(keyCodes) is list:
		keyboard.send(
			*map(getKeyCode, keyCodes)
		)
	elif type(keyCodes) is str:
		keyboard.send(
			getKeyCode(keyCodes)
		)

def getPageRows():
	return len(themeConfig['pages'][currentPage])

def getPageColumns():
	return len(themeConfig['pages'][currentPage][0])

def getTileWidth():
	return math.floor(board.DISPLAY.width / getPageColumns())

def getTileHeight():
	return math.floor(board.DISPLAY.height / getPageRows())

def setBacklight(value: float):
	value = max(0, min(1.0, value))
	board.DISPLAY.brightness = value

	if debugging:
		print('Backlight: ' + str(board.DISPLAY.brightness))

def transitionIn(transitionType):
	if transitionType is None:
		return

	if transitionType is 'cut':
		setBacklight(1)

	if transitionType is 'fade':
		fadeTo(1)

def transitionOut(transitionType):
	if transitionType is None:
		return

	if transitionType is 'cut':
		setBacklight(0)

	if transitionType is 'fade':
		fadeTo(0)

def fadeTo(value, startFrom = None):
	transitionStep = themeConfig.get('transitionStep', 0.1)
	transitionSpeed = themeConfig.get('transitionSpeed', 0.05)

	if startFrom is None:
		startFrom = board.DISPLAY.brightness

	if startFrom != board.DISPLAY.brightness:
		startFrom = float(startFrom)
		setBacklight(startFrom)
		time.sleep(transitionSpeed)

	if value > startFrom:
		while board.DISPLAY.brightness < value:
			setBacklight(board.DISPLAY.brightness + transitionStep)
			time.sleep(transitionSpeed)
	elif value < startFrom:
		while board.DISPLAY.brightness > value:
			setBacklight(board.DISPLAY.brightness - transitionStep)
			time.sleep(transitionSpeed)

def setTile(touch, state = 0):
	if type(touch['x']) is int and type(touch['y']) is int:
		i = (touch['y'] * getPageColumns()) + touch['x']
		btn = themeConfig['pages'][currentPage][touch['y']][touch['x']]["button"]
		btnGrid[i] = themeConfig['buttons'][btn][state]

		if refreshAfterTileUpdate():
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
			setTile({
				'x': tileX,
				'y': tileY
			})

	if not refreshAfterTileUpdate():
		refreshDisplay()

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
	if themeConfig.get('splash', None) is None:
		return

	if debugging:
		print('Displaying Splash Screen')

	setBacklight(0)

	splash = displayio.OnDiskBitmap(
		imgPath + themeConfig.get('splash', {}).get('image', 'Splash.bmp')
	)

	splashGrid = displayio.TileGrid(
		splash,
		pixel_shader = splash.pixel_shader
	)

	displayGroup.append(
		splashGrid
	)

	refreshDisplay()

	transitionIn(
		themeConfig.get('splash', {}).get('transition', 'fade')
	)

	time.sleep(
		themeConfig.get('splash', {}).get('duration', 3)
	)

	transitionOut(
		themeConfig.get('splash', {}).get('transition', 'fade')
	)

	displayGroup.remove(
		splashGrid
	)

	refreshDisplay()

# Turn off display auto refreshing
board.DISPLAY.auto_refresh = 0

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
idleMode = 0

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

transitionIn(
	themeConfig.get('splash', {}).get('transition', 'cut')
)

timeStateChanged = time.monotonic()

# main loop
while True:
	currentTime = time.monotonic()

	# make a note of the previous touch state
	previousTouch = currentTouch

	# get the current touch state
	currentTouch = getCurrentTouch()

	# check & handle entering/exiting idle state
	if isIdle():
		if not idleMode and currentTouch['x'] is None and currentTouch['y'] is None:
			if debugging:
				print('Entering idle mode')

			idleMode = 1

			transitionOut(
				themeConfig.get('idle', {}).get('transition', 'fade')
			)

			sendKeyCodes(
				themeConfig.get('idle', {}).get('keyCodes', {}).get('enter', None)
			)

			continue
		elif idleMode and type(previousTouch['x']) is int and type(previousTouch['y']) is int:
			if debugging:
				print('Exiting idle mode')

			idleMode = 0

			sendKeyCodes(
				themeConfig.get('idle', {}).get('keyCodes', {}).get('exit', None)
			)

			transitionIn(
				themeConfig.get('idle', {}).get('transition', 'fade')
			)

			timeStateChanged = currentTime

			continue

	# check button up - reset stuff when the touch has been released
	if previousTouch != currentTouch and type(previousTouch['x']) is int and type(previousTouch['y']) is int:
		setTile(
			previousTouch
		)

		# if a previously-touched button is used for pagination, trigger it
		if previousButton and currentTouch['x'] is None and currentTouch['y'] is None:
			buttonPage = previousButton.get('page', None)

			if buttonPage is not None:
				transitionOut(
					themeConfig.get('transitionType', None)
				)

				# perform a pagination action if pagination is enabled
				if buttonPage in ['prev', 'previous']:
					prevPage()
				elif buttonPage == 'next':
					nextPage()
				elif type(buttonPage) is int:
					setPage(buttonPage)

				transitionIn(
					themeConfig.get('transitionType', None)
				)

		previousButton = None
		timeTouched = None

	# check button down - trigger actions when current/previous touches match (helps to filter out inconsistencies)
	elif previousTouch == currentTouch and type(currentTouch['x']) is int and type(currentTouch['y']) is int:
		timeStateChanged = currentTime

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

		# send the button's defined keys
		sendKeyCodes(
			currentButton.get('keyCodes', None)
		)


		# make a note of what button we've just used
		previousButton = currentButton
