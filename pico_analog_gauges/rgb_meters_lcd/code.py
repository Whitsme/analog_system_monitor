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
from bitmaptools import fill_region, draw_line
from rainbowio import colorwheel
from time import sleep
from adafruit_display_text import label
from adafruit_display_shapes import rect
import adafruit_displayio_sh1106

pixel_pin = board.GP0
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

RED = [255, 0, 0]
YELLOW = [255, 150, 0]
GREEN = [0, 255, 0]
CYAN = [0, 255, 255]
BLUE = [0, 0, 255]
PURPLE = [180, 0, 255]
teal = [0, 200, 100]
amber = [255, 194, 0]

activator = digitalio.DigitalInOut(board.GP22)
activator.direction = digitalio.Direction.OUTPUT
activator.value = True

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 b"
    size_name = ("b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    d = round(size_bytes / p, 2)
    if i == 0:
        return "%d %s" % (d, size_name[i])
    else:
        return "%0.2f %s" % (d, size_name[i])


def calc_load(update_ms, update_span, old_load, target_load):
    diff_ms = abs(time.monotonic() - update_ms)
    if diff_ms > update_span:
        diff_ms = update_span
    glide = diff_ms / float(update_span)

    load_diff = target_load - old_load
    return old_load + load_diff * glide

class Gauge:
    BAR_HEIGHT = 72
    BAR_WIDTH = 18
    BAR_REDUCTION = 20

    HEAT_PALETTE = displayio.Palette(50)
    HEAT_PALETTE[48] = 0xFFFFFF
    color_range = len(HEAT_PALETTE) - 2
    for i in range(0, color_range):
        if i <= color_range / 2:
            g = int(255 * (i / float(color_range / 2)))
            HEAT_PALETTE[i] = (255, g, 0)
        else:
            r = int(255 - (255 * ((i - (color_range / 2)) / float(color_range / 2))))
            HEAT_PALETTE[i] = (r, 255, 0)

    HEAT_BMP = displayio.Bitmap(BAR_WIDTH - 2, BAR_HEIGHT - BAR_REDUCTION - 2, 49)
    for i in range(0, BAR_HEIGHT - BAR_REDUCTION - 2):
        draw_line(HEAT_BMP, 0,
                  i,
                  BAR_WIDTH - 3, i,
                  int((len(HEAT_PALETTE) - 2) * (i / (BAR_HEIGHT - BAR_REDUCTION - 2)))
                  # i % 48
                  )

    def __init__(self, x, y, update_span=1.0):
        self.x = x
        self.y = y

        self.load = 1
        self.target_load = 0
        self.old_load = 0
        self.update_span = update_span
        self.update_ms = 0

        self.group = displayio.Group(x=x, y=y)
        self.bar_bitmap, color_sprite = self.bar()
        self.group.append(color_sprite)
        self.caption_l = self.caption_load()
        self.group.append(self.caption_l)

    def bar(self):
        color_bitmap = displayio.Bitmap(Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        fill_region(color_bitmap, 0, 0, Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        color_sprite = displayio.TileGrid(color_bitmap, pixel_shader=Gauge.HEAT_PALETTE, x=0, y=0)
        return color_bitmap, color_sprite

    def caption_load(self):
        text_area = label.Label(terminalio.FONT, text="0%", color=0xFFFFFF)
        text_area.x = int((Gauge.BAR_WIDTH - text_area.bounding_box[2]) / 2)
        text_area.y = Gauge.BAR_HEIGHT - 14
        return text_area

    def set_load(self, level):
        if level > 100:
            level = 100
        elif level < 0:
            level = 0
        self.target_load = level
        self.old_load = self.load
        self.update_ms = time.monotonic()

    def get_graphics(self):
        return self.group

    def tick(self):
        if int(self.target_load) == int(self.load):
            return
        self.load = calc_load(self.update_ms, self.update_span, self.old_load, self.target_load)

        if self.load > 100:
            self.load = 100
        elif self.load < 0:
            self.load = 0
        fill_region(self.bar_bitmap, 0, 0, Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        self.bar_bitmap.blit(1, 1, Gauge.HEAT_BMP)
        fill_region(self.bar_bitmap, 1, 1, Gauge.BAR_WIDTH - 1,
                    int((Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION - 2) * ((100 - (self.load)) / 100.0)) + 1, 49)
        self.caption_l.text = "%d%%" % int(self.load)
        self.caption_l.x = int((Gauge.BAR_WIDTH - self.caption_l.bounding_box[2]) / 2)

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
    baudrate=1000000
)

WIDTH = 130
HEIGHT = 64
BORDER = 5

display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

main_group = displayio.Group()
display.show(main_group)
display.auto_refresh=False

label_hight = 4

cpu_one_label = label.Label(terminalio.FONT, text="C", color=0xFFFFFF, x=21, y=label_hight)
cpu_two_label = label.Label(terminalio.FONT, text="P", color=0xFFFFFF, x=21, y=label_hight+10)
cpu_three_label = label.Label(terminalio.FONT, text="U", color=0xFFFFFF, x=21, y=label_hight+20)
mem_one_label = label.Label(terminalio.FONT, text="M", color=0xFFFFFF, x=51, y=label_hight)
mem_two_label = label.Label(terminalio.FONT, text="E", color=0xFFFFFF, x=51, y=label_hight+10)
mem_three_label = label.Label(terminalio.FONT, text="M", color=0xFFFFFF, x=51, y=label_hight+20)
net_one_label = label.Label(terminalio.FONT, text="N", color=0xFFFFFF, x=81, y=label_hight)
net_two_label = label.Label(terminalio.FONT, text="E", color=0xFFFFFF, x=81, y=label_hight+10)
net_three_label = label.Label(terminalio.FONT, text="T", color=0xFFFFFF, x=81, y=label_hight+20)
ssd_one_label = label.Label(terminalio.FONT, text="S", color=0xFFFFFF, x=111, y=label_hight)
ssd_two_label = label.Label(terminalio.FONT, text="S", color=0xFFFFFF, x=111, y=label_hight+10)
ssd_three_label = label.Label(terminalio.FONT, text="D", color=0xFFFFFF, x=111, y=label_hight+20)

main_group.append(cpu_one_label)
main_group.append(cpu_two_label)
main_group.append(cpu_three_label)
main_group.append(mem_one_label)
main_group.append(mem_two_label)
main_group.append(mem_three_label)
main_group.append(net_one_label)
main_group.append(net_two_label)
main_group.append(net_three_label)
main_group.append(ssd_one_label)
main_group.append(ssd_two_label)
main_group.append(ssd_three_label)

g = Gauge(2, 0)
g2 = Gauge(32, 0, 0.001)
g3 = Gauge(62, 0, 0.001)
g4 = Gauge(92, 0, 0.001)
main_group.append(g.get_graphics())
main_group.append(g2.get_graphics())
main_group.append(g3.get_graphics())
main_group.append(g4.get_graphics())

logo_label = label.Label(terminalio.FONT, text="A\nS\nM\nP", color=0xFFFFFF, x=124, y=6)
main_group.append(logo_label)

logo_box = rect.Rect(121, 0, 12, 64, outline=0xffffff, stroke=1)
main_group.append(logo_box)

tick_counter = 0

duty_min = 500
duty_max = 12000
freq = 500

meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)

while True:
    pixels.fill(amber)
    pixels.show()
    try:
        available = usb_cdc.data.in_waiting
        while available >= 14:
            raw = usb_cdc.data.read(available)
            data = struct.unpack("bbbbIIf", raw)
            power = data[1]
            g.set_load(data[1])
            g2.set_load(data[4])
            g3.set_load(data[2])
            g4.set_load(data[3])
            power = power * 120
            if power >= duty_max:
                power = duty_max
            elif power <= duty_min:
                power = duty_min
            meter.duty_cycle = power
            available = usb_cdc.data.in_waiting
        g.tick()
        g2.tick()
        g3.tick()
        g4.tick()
        display.refresh()
        if tick_counter % 4 == 0:
            network.tick()
    except:        
        meter.deinit()
    
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
from bitmaptools import fill_region, draw_line
from rainbowio import colorwheel
from time import sleep
from adafruit_display_text import label
from adafruit_display_shapes import rect
import adafruit_displayio_sh1106

pixel_pin = board.GP0
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

RED = [255, 0, 0]
YELLOW = [255, 150, 0]
GREEN = [0, 255, 0]
CYAN = [0, 255, 255]
BLUE = [0, 0, 255]
PURPLE = [180, 0, 255]
teal = [0, 200, 100]
amber = [255, 194, 0]

activator = digitalio.DigitalInOut(board.GP22)
activator.direction = digitalio.Direction.OUTPUT
activator.value = True

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 b"
    size_name = ("b", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    d = round(size_bytes / p, 2)
    if i == 0:
        return "%d %s" % (d, size_name[i])
    else:
        return "%0.2f %s" % (d, size_name[i])


def calc_load(update_ms, update_span, old_load, target_load):
    diff_ms = abs(time.monotonic() - update_ms)
    if diff_ms > update_span:
        diff_ms = update_span
    glide = diff_ms / float(update_span)

    load_diff = target_load - old_load
    return old_load + load_diff * glide

class Gauge:
    BAR_HEIGHT = 72
    BAR_WIDTH = 18
    BAR_REDUCTION = 20

    HEAT_PALETTE = displayio.Palette(50)
    HEAT_PALETTE[48] = 0xFFFFFF
    color_range = len(HEAT_PALETTE) - 2
    for i in range(0, color_range):
        if i <= color_range / 2:
            g = int(255 * (i / float(color_range / 2)))
            HEAT_PALETTE[i] = (255, g, 0)
        else:
            r = int(255 - (255 * ((i - (color_range / 2)) / float(color_range / 2))))
            HEAT_PALETTE[i] = (r, 255, 0)

    HEAT_BMP = displayio.Bitmap(BAR_WIDTH - 2, BAR_HEIGHT - BAR_REDUCTION - 2, 49)
    for i in range(0, BAR_HEIGHT - BAR_REDUCTION - 2):
        draw_line(HEAT_BMP, 0,
                  i,
                  BAR_WIDTH - 3, i,
                  int((len(HEAT_PALETTE) - 2) * (i / (BAR_HEIGHT - BAR_REDUCTION - 2)))
                  # i % 48
                  )

    def __init__(self, x, y, update_span=1.0):
        self.x = x
        self.y = y

        self.load = 1
        self.target_load = 0
        self.old_load = 0
        self.update_span = update_span
        self.update_ms = 0

        self.group = displayio.Group(x=x, y=y)
        self.bar_bitmap, color_sprite = self.bar()
        self.group.append(color_sprite)
        self.caption_l = self.caption_load()
        self.group.append(self.caption_l)

    def bar(self):
        color_bitmap = displayio.Bitmap(Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        fill_region(color_bitmap, 0, 0, Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        color_sprite = displayio.TileGrid(color_bitmap, pixel_shader=Gauge.HEAT_PALETTE, x=0, y=0)
        return color_bitmap, color_sprite

    def caption_load(self):
        text_area = label.Label(terminalio.FONT, text="0%", color=0xFFFFFF)
        text_area.x = int((Gauge.BAR_WIDTH - text_area.bounding_box[2]) / 2)
        text_area.y = Gauge.BAR_HEIGHT - 14
        return text_area

    def set_load(self, level):
        if level > 100:
            level = 100
        elif level < 0:
            level = 0
        self.target_load = level
        self.old_load = self.load
        self.update_ms = time.monotonic()

    def get_graphics(self):
        return self.group

    def tick(self):
        if int(self.target_load) == int(self.load):
            return
        self.load = calc_load(self.update_ms, self.update_span, self.old_load, self.target_load)

        if self.load > 100:
            self.load = 100
        elif self.load < 0:
            self.load = 0
        fill_region(self.bar_bitmap, 0, 0, Gauge.BAR_WIDTH, Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION, 48)
        self.bar_bitmap.blit(1, 1, Gauge.HEAT_BMP)
        fill_region(self.bar_bitmap, 1, 1, Gauge.BAR_WIDTH - 1,
                    int((Gauge.BAR_HEIGHT - Gauge.BAR_REDUCTION - 2) * ((100 - (self.load)) / 100.0)) + 1, 49)
        self.caption_l.text = "%d%%" % int(self.load)
        self.caption_l.x = int((Gauge.BAR_WIDTH - self.caption_l.bounding_box[2]) / 2)

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
    baudrate=1000000
)

WIDTH = 130
HEIGHT = 64
BORDER = 5

display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

main_group = displayio.Group()
display.show(main_group)
display.auto_refresh=False

label_hight = 4

cpu_one_label = label.Label(terminalio.FONT, text="C", color=0xFFFFFF, x=21, y=label_hight)
cpu_two_label = label.Label(terminalio.FONT, text="P", color=0xFFFFFF, x=21, y=label_hight+10)
cpu_three_label = label.Label(terminalio.FONT, text="U", color=0xFFFFFF, x=21, y=label_hight+20)
mem_one_label = label.Label(terminalio.FONT, text="M", color=0xFFFFFF, x=51, y=label_hight)
mem_two_label = label.Label(terminalio.FONT, text="E", color=0xFFFFFF, x=51, y=label_hight+10)
mem_three_label = label.Label(terminalio.FONT, text="M", color=0xFFFFFF, x=51, y=label_hight+20)
net_one_label = label.Label(terminalio.FONT, text="N", color=0xFFFFFF, x=81, y=label_hight)
net_two_label = label.Label(terminalio.FONT, text="E", color=0xFFFFFF, x=81, y=label_hight+10)
net_three_label = label.Label(terminalio.FONT, text="T", color=0xFFFFFF, x=81, y=label_hight+20)
ssd_one_label = label.Label(terminalio.FONT, text="S", color=0xFFFFFF, x=111, y=label_hight)
ssd_two_label = label.Label(terminalio.FONT, text="S", color=0xFFFFFF, x=111, y=label_hight+10)
ssd_three_label = label.Label(terminalio.FONT, text="D", color=0xFFFFFF, x=111, y=label_hight+20)

main_group.append(cpu_one_label)
main_group.append(cpu_two_label)
main_group.append(cpu_three_label)
main_group.append(mem_one_label)
main_group.append(mem_two_label)
main_group.append(mem_three_label)
main_group.append(net_one_label)
main_group.append(net_two_label)
main_group.append(net_three_label)
main_group.append(ssd_one_label)
main_group.append(ssd_two_label)
main_group.append(ssd_three_label)

g = Gauge(2, 0)
g2 = Gauge(32, 0, 0.001)
g3 = Gauge(62, 0, 0.001)
g4 = Gauge(92, 0, 0.001)
main_group.append(g.get_graphics())
main_group.append(g2.get_graphics())
main_group.append(g3.get_graphics())
main_group.append(g4.get_graphics())

logo_label = label.Label(terminalio.FONT, text="A\nS\nM\nP", color=0xFFFFFF, x=124, y=6)
main_group.append(logo_label)

logo_box = rect.Rect(121, 0, 12, 64, outline=0xffffff, stroke=1)
main_group.append(logo_box)

tick_counter = 0

duty_min = 500
duty_max = 12000
freq = 500

meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)

while True:
    pixels.fill(amber)
    pixels.show()
    try:
        available = usb_cdc.data.in_waiting
        while available >= 14:
            raw = usb_cdc.data.read(available)
            data = struct.unpack("bbbbIIf", raw)
            power = data[1]
            g.set_load(data[1])
            g2.set_load(data[4])
            g3.set_load(data[2])
            g4.set_load(data[3])
            power = power * 120
            if power >= duty_max:
                power = duty_max
            elif power <= duty_min:
                power = duty_min
            meter.duty_cycle = power
            available = usb_cdc.data.in_waiting
        g.tick()
        g2.tick()
        g3.tick()
        g4.tick()
        display.refresh()
        if tick_counter % 4 == 0:
            network.tick()
    except:        
        meter.deinit()
    

