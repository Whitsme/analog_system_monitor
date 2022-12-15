from time import sleep

import busio
import board
import math
import struct
import pwmio
import usb_cdc
import digitalio
import terminalio

duty_min = 500
duty_max = 6000
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


    

        



