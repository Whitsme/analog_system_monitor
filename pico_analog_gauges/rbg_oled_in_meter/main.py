
import busio
import board
import math
import struct
import pwmio
import usb_cdc
import digitalio
import displayio
import terminalio
import neopixel
import time
import random
import adafruit_displayio_ssd1306
from bitmaptools import fill_region, draw_line
from rainbowio import colorwheel
from time import sleep
from digitalio import DigitalInOut,Pull
from adafruit_display_text import label
from adafruit_display_shapes import rect
from adafruit_display_shapes.sparkline import Sparkline

activator = digitalio.DigitalInOut(board.GP22)
activator.direction = digitalio.Direction.OUTPUT
activator.value = True

pixel_pin = board.GP6
num_pixels = 1
pixel_bright = 0.4
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=pixel_bright, auto_write=False)

red = [255, 0, 0]
yellow = [255, 150, 0]
green = [0, 255, 0]
cyan = [0, 255, 255]
blue = [0, 0, 255]
purple = [180, 0, 255]
teal = [0, 200, 100]
amber = [255, 194, 0]  
orange = [255,120,0]

freq = 500
duty_min = 500
meter = pwmio.PWMOut(board.GP8, frequency=freq, duty_cycle=duty_min)

displayio.release_displays()

WIDTH = 128
HEIGHT = 256
ROTATION = 180

i2c = busio.I2C(board.GP5, board.GP4)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION)

main_group = displayio.Group()
display.show(main_group)

load = 0
power = 500

cpu_text = [39, 43, 47, 20, 0xFFFFFF]

def cpu_tick():
    cpu_one_label = label.Label(terminalio.FONT, text="C", color=cpu_text[4], x=cpu_text[0], y=7)
    cpu_two_label = label.Label(terminalio.FONT, text="P", color=cpu_text[4], x=cpu_text[1], y=17)
    cpu_three_label = label.Label(terminalio.FONT, text="U", color=cpu_text[4], x=cpu_text[2], y=27)  
    
    text_area = label.Label(terminalio.FONT, text="{}%".format(load), color=cpu_text[4], x=80, y=27)

    main_group.append(cpu_one_label)
    main_group.append(cpu_two_label)
    main_group.append(cpu_three_label)
    
    main_group.append(text_area)
            
cpu_tick()

load = 0

sparkline = Sparkline(width=cpu_text[3], height=24, max_items=5, y_min=0, y_max=10, x=cpu_text[3], y=2)
main_group.append(sparkline)

while True:
    sparkline.add_value(random.uniform(0, 10))
    meter.duty_cycle = power
    if power < 4000:
        if power < 1000:
            pixels[0] = (teal)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 1100:
            pixels[0] = (red)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 1400:
            pixels[0] = (green)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 1500:
            pixels[0] = (orange)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 2000:
            pixels[0] = (blue)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 2100:
            pixels[0] = (red)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 2400:
            pixels[0] = (teal)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 2500:
            pixels[0] = (yellow)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 2700:
            pixels[0] = (green)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 2800:
            pixels[0] = (orange)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 3400:
            pixels[0] = (blue)
            pixels.show() 
            x = [1,1,1,2]
        elif power < 3500:
            pixels[0] = (amber)
            pixels.show() 
            x = [3,2,1,4]
        elif power < 3800:
            pixels[0] = (blue)
            pixels.show() 
            x = [1,1,1,1]
        power = power + 100
        cpu_text[4]=0x000000
        cpu_tick()
        cpu_text[4]=0xFFFFFF
        cpu_text[0]+=x[0]
        cpu_text[1]+=x[1]
        cpu_text[2]+=x[2]
        cpu_text[3]+=x[3]
        cpu_tick()
    time.sleep(0.5)
    
       

"""
while True:
    if power < 5000 and power in shift_range:
        vis_state = 0x000000
        cpu_tick(teal, c_x, p_x, u_x, vis_state)
        power+=10
        c_x += x_shift
        p_x += x_hold
        u_x += x_stall
        vis_state = 0xFFFFFF
        cpu_tick(purple, c_x, p_x, u_x, vis_state)
    elif power < 5000:
        time.sleep(0.5):
        vis_state = 0x000000
        cpu_tick(amber, c_x, p_x, u_x, vis_state)
        power+=10
        c_x += x_hold
        p_x += x_hold
        u_x += x_hold
        vis_state = 0xFFFFFF
        cpu_tick(teal, c_x, p_x, u_x, vis_state)
        time.sleep(0.5)

    else:
        meter.deinit()
             
    #sparkline.add_value(random.uniform(0, 10))

"""


"""
from kmk.extensions.RGB import RGB
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.mouse_keys import MouseKeys
from kmk.keys import KC
from kmk.scanners import DiodeOrientation


keyboard = KMKKeyboard()

# rgb = RGB(pixel_pin=board.GP15, num_pixels=1, val_default=100)
# keyboard.extensions.append(rgb)

# keyboard.modules.append(MouseKeys())

keyboard.col_pins = (
    board.GP0, 
    board.GP1, 
    board.GP2, 
    board.GP3, 
    board.GP4, 
    board.GP5, 
    board.GP6, 
    board.GP7, 
    board.GP8, 
    board.GP9, 
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    )
keyboard.row_pins = (
    board.GP16, 
    board.GP17, 
    board.GP18, 
    board.GP19, 
    board.GP20,
    )
keyboard.diode_orientation = DiodeOrientation.COL2ROW

XXXXXXX = KC.TRNS

keyboard.keymap = [
    # Qwerty
    # Pico GPIO
    # ,--------------------------------------------------------------------------------------------------------.
    # | ESC  |   1  |   2  |   3  |   4  |   5  |   6  |   7  |   8  |   9  |   0  |   -  |   =  | Bksp |  ~`  |
    # | 0+16 | 1+16 | 2+16 | 3+16 | 4+16 | 5+16 | 6+16 | 7+16 | 8+16 | 9+16 |10+16 |11+16 |12+16 |13+16 |14+16 |
    # |------+------+------+------+------+------+------+------+------+------+------+------+------+------+------| 
    # | Tab  |   Q  |   W  |   E  |   R  |   T  |   Y  |   U  |   I  |   O  |   P  |   [  |   ]  |   \  | Del  | 
    # | 0+17 | 1+17 | 2+17 | 3+17 | 4+17 | 5+17 | 6+17 | 7+17 | 8+17 | 9+17 |10+17 |11+17 |12+17 |13+17 |14+17 | 
    # |------+------+------+------+------+-------------+------+------+------+------+------+------+------+------|
    # | Caps |   A  |   S  |   D  |   F  |   G  |   H  |   J  |   K  |   L  |   ;  |   '  |XXXXXX| Enter| pgup |
    # | 0+18 | 1+18 | 2+18 | 3+18 | 4+18 | 5+18 | 6+18 | 7+18 | 8+18 | 9+18 |10+18 |11+18 |12+18 |13+18 |14+18 | 
    # |------+------+------+------+------+------+------+------+------+------+------+------+------+------+------|
    # | Shift|   Z  |   X  |   C  |   V  |   B  |   N  |   M  |   ,  |   .  |   /  |XXXXXX|Shift |  Up  | pgdn |
    # | 0+19 | 1+19 | 2+19 | 3+19 | 4+19 | 5+19 | 6+19 | 7+19 | 8+19 | 9+19 |10+19 |11+19 |12+19 |13+19 |14+19 | 
    # |------+------+------+------+------+------+------+------+------+------+------+------+------+------+------|
    # | Ctrl | GUI  |  Alt |XXXXXX|XXXXXX| Space|XXXXXX|XXXXXX|XXXXXX| Alt  | GUI  | Ctrl |  <-  | Down |  ->  |
    # | 0+20 | 1+20 | 2+20 | 3+20 | 4+20 | 5+20 | 6+20 | 7+20 | 8+20 | 9+20 |10+20 |11+20 |12+20 |13+20 |14+20 | 
    # `-------------------------------------------------------------------------------------------------+------'
    [
        KC.ESC,  KC.N1, KC.N2,   KC.N3,   KC.N4,   KC.N5,  KC.N6,   KC.N7,   KC.N8,   KC.N9,   KC.N0,   KC.MINS, KC.EQUAL, KC.BSPC, KC.GRAVE,
        KC.TAB,   KC.Q,    KC.W,    KC.E,    KC.R,    KC.T,   KC.Y,    KC.U,    KC.I,    KC.O,    KC.P,    KC.LBRC, KC.RBRC,  KC.BSLASH, KC.DEL,
        KC.CAPS,  KC.A,    KC.S,    KC.D,    KC.F,    KC.G,   KC.H,    KC.J,    KC.K,    KC.L,    KC.SCLN, KC.QUOT, XXXXXXX,  KC.ENTER, KC.PGUP,
        KC.LSFT,  KC.Z,    KC.X,    KC.C,    KC.V,    KC.B,   KC.N,    KC.M,    KC.COMM, KC.DOT,  KC.SLSH, XXXXXXX, KC.RSFT,  KC.UP, KC.PGDN,
        KC.LCTRL, KC.LGUI, KC.LALT, XXXXXXX, XXXXXXX, KC.SPC, XXXXXXX, XXXXXXX, XXXXXXX, KC.RALT, KC.RGUI, KC.RCTL, KC.LEFT, KC.DOWN, KC.RIGHT
    ],
]
"""
