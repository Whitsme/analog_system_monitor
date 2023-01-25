import board
import busio
import displayio
import terminalio
import pwmio
import usb_cdc
import neopixel
import time
import adafruit_displayio_ssd1306
from time import sleep
from rainbowio import colorwheel
from digitalio import DigitalInOut,Pull
from adafruit_display_text import label
from adafruit_display_shapes import rect

red = [255, 0, 0]
yellow = [255, 150, 0]
green = [0, 255, 0]
cyan = [0, 255, 255]
blue = [0, 0, 255]
purple = [180, 0, 255]
teal = [0, 128, 128]
amber = [255, 194, 0]
white = [255, 255, 255]
duty_min = 500
duty_max = 5000
freq = 500
sweep = duty_min
num_pixels = 1
pixel_pin = board.GP6
pixel_bright = 0.1
color = white
meter_a = pwmio.PWMOut(board.GP8, frequency=freq, duty_cycle=duty_min)
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=pixel_bright, auto_write=False)

usb_cdc.enable(console=False, data=True)

displayio.release_displays()

i2c = busio.I2C(board.GP5, board.GP4)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)

WIDTH = 128
HEIGHT = 256  # Change to 64 if needed
ROTATION = 180
BORDER = 5

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(60, 30, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=34, y=1
)
splash.append(inner_sprite)

text = "ASMP"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=54, y=16
    )
splash.append(text_area)

while sweep <= duty_max:
    meter_a.duty_cycle = sweep
    pixels[0] = (amber)
    pixels.show()
    sleep(0.05) 
    sweep = sweep + 200
    
while sweep >= (duty_max - 10):
    meter_a.duty_cycle = sweep
    pixels[0] = (purple)
    pixels.show()
    sleep(0.01)
    sweep = sweep - 10

while sweep >= duty_min:
    meter_a.duty_cycle = sweep
    pixels[0] = (teal)
    pixels.show()
    sleep(0.05)
    sweep = sweep - 200

meter_a.deinit()




