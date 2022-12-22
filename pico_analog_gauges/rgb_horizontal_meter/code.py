from time import sleep

import busio
import board
import math
import struct
import pwmio
import usb_cdc
import digitalio
import terminalio
from rainbowio import colorwheel
import neopixel


pixel_pin = board.GP0
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = colorwheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
teal = [0, 200, 100]
amber = [255, 194, 0]

while True:
    pixels.fill(amber)
    pixels.show()
    # Increase or decrease to change the speed of the solid color change.
    time.sleep(1)
    pixels.fill(GREEN)
    pixels.show()
    time.sleep(1)
    pixels.fill(BLUE)
    pixels.show()
    time.sleep(1)

    color_chase(RED, 0.1)  # Increase the number to slow down the color chase
    color_chase(YELLOW, 0.1)
    color_chase(GREEN, 0.1)
    color_chase(CYAN, 0.1)
    color_chase(BLUE, 0.1)
    color_chase(PURPLE, 0.1)

    rainbow_cycle(0)  # Increase the number to slow down the rainbowv

duty_min = 500
duty_max = 12000
freq = 500

meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)

while True:
    try:
        available = usb_cdc.data.in_waiting
        while available >= 14:
            raw = usb_cdc.data.read(available)
            data = struct.unpack("bbbbIIf", raw)
            power = data[2]
            power = power * 60
            if power >= duty_max:
                power = duty_max
            elif power <= duty_min:
                power = duty_min
            meter.duty_cycle = power
            available = usb_cdc.data.in_waiting
    except:        
        meter.deinit()
        
meter.deinit()


    

        



