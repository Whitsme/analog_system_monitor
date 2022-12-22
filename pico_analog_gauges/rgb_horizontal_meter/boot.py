from time import sleep
import board
import pwmio
import usb_cdc
from rainbowio import colorwheel
import neopixel

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
teal = [0, 128, 128]
amber = [255, 194, 0]
white = [255, 255, 255]
duty_min = 500
duty_max = 12000
freq = 500
sweep = duty_min
num_pixels = 1
pixel_pin = board.GP0
pixel_bright = 0.3
color = [255, 255, 255]
goal = amber
color_shift = []
meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=pixel_bright, auto_write=False)

usb_cdc.enable(console=False, data=True)

def calc_adds():
    color_shift.clear()
    if goal[0] != 255 and goal[0] != 0:
        div_a = goal[0] * 0.4
        div_b = div_a/255
        mult = div_b * 40
        r_add = int(mult)
        color_shift.append(r_add)
    else:
        r_add = 0
        color_shift.append(r_add)
        
    if goal[1] != 255 and goal[1] != 0:
        div_a = goal[1] * 0.4
        div_b = div_a/255
        mult = div_b * 40
        g_add = int(mult)
        color_shift.append(g_add)
    else: 
        g_add = 0
        color_shift.append(g_add)
        
    if goal[2] != 255 and goal[2] != 0:
        div_a = goal[2] * 0.4
        div_b = div_a/255
        mult = div_b * 40
        b_add = int(mult)
        color_shift.append(b_add)
    else: 
        b_add = 0
        color_shift.append(b_add)     

def change_color(color):
    color[0] = color[0] + color_shift[0]
    color[1] = color[1] + color_shift[1]
    color[2] = color[2] + color_shift[2]
    return color

calc_adds()

while sweep <= duty_max:
    meter.duty_cycle = sweep
    pixels.fill(color)
    sleep(0.05)
    pixels.show()
    sweep = sweep + 300
    color = change_color(color)
    
while sweep >= (duty_max - 100):
    meter.duty_cycle = sweep
    sleep(0.01)
    sweep = sweep - 30

while sweep >= duty_min:
    meter.duty_cycle = sweep
    sleep(0.05)
    sweep = sweep - 300

meter.deinit()



