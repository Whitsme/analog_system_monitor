from time import sleep
import board
import busio
import displayio
import terminalio
import pwmio
import usb_cdc
import neopixel
import time
from rainbowio import colorwheel
from digitalio import DigitalInOut,Pull
import adafruit_displayio_sh1106
from adafruit_display_text import label
from adafruit_display_shapes import rect

RED = [255, 0, 0]
YELLOW = [255, 150, 0]
GREEN = [0, 255, 0]
CYAN = [0, 255, 255]
BLUE = [0, 0, 255]
PURPLE = [180, 0, 255]
teal = [0, 128, 128]
amber = [255, 194, 0]
white = [255, 255, 255]
duty_min = 500
duty_max = 12000
freq = 500
sweep = duty_min
num_pixels = 1
pixel_pin = board.GP0
pixel_bright = 0.1
color = white
goal = amber
r_shift = []
g_shift = []
b_shift = []
meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=pixel_bright, auto_write=False)

usb_cdc.enable(console=False, data=True)

displayio.release_displays()

MOSI = board.GP15 # white_19
SCK = board.GP14 # brown_23
OLED_DC = board.GP13 # purple_18
OLED_CS = board.GP12 # blue_24
OLED_RESET = board.GP11 # yellow_22

spi = busio.SPI(SCK, MOSI)
display_bus = displayio.FourWire(
    spi,
    command=OLED_DC,
    chip_select=OLED_CS,
    reset=OLED_RESET,
    baudrate=1000000,
)

WIDTH = 130
HEIGHT = 64
BORDER = 5
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

def r_shift(color):
	if color[0] != goal[0]:
		if color[0] - goal[0] <= 0:
			r_new = color[0] + 5
			return r_new
		elif color[0] - goal [0] >= 0:
			r_new = color[0] - 5
			return r_new
		elif color[0] >= 255:
			r_new = 255
			return r_new
		elif color[0] < 0:
			r_new = 0
			return r_new
	return goal[0]
			
def g_shift(color):
	if color[1] != goal[1]:
		if color[1] - goal[1] <= 0:
			g_new = color[1] + 5
			return g_new
		elif color[1] - goal [1] >= 0:
			g_new = color[1] - 5
			return g_new
		elif color[1] >= 255:
			g_new = 255
			return g_new
		elif color[1] < 0:
			g_new = 0
			return g_new
	return goal[1]

def b_shift(color):
	if color[2] != goal[2]:
		if color[2] - goal[2] <= 0:
			b_new = color[2] + 5
			return b_new
		elif color[2] - goal[2] >= 0:
			b_new = color[2] - 5
			return b_new
		elif color[2] >= 255:
			b_new = 255
			return b_new
		elif color[2] < 0:
			b_new = 0
			return b_new
	return goal[2]
	
def change_color(color):
	r_new = r_shift(color)
	g_new = g_shift(color)
	b_new = b_shift(color)
	color = [int(r_new), int(g_new), int(b_new)]
	return color

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_display = "\nanalog system monitor\n\n         pico\n".format(color, goal)

text_area = label.Label(
    terminalio.FONT, text=text_display, color=0xFFFFFF, x=2, y=3,
)

logo_box = rect.Rect(53, 48, 30, 16, outline=0xffffff, stroke=1)

splash.append(logo_box)
splash.append(text_area)

	
while sweep <= duty_max:
    meter.duty_cycle = sweep
    pixels.fill(color)
    sleep(0.05)
    pixels.show()
    sweep = sweep + 300
    color = change_color(color)
    
while sweep >= (duty_max - 100):
    meter.duty_cycle = sweep
    pixels.fill(goal)
    sleep(0.01)
    sweep = sweep - 30

while sweep >= duty_min:
    meter.duty_cycle = sweep
    pixels.fill(goal)
    sleep(0.05)
    sweep = sweep - 300

pixels.fill(goal)
meter.deinit()




