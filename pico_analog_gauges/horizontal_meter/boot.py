from time import sleep
import board
import pwmio
import usb_cdc

usb_cdc.enable(console=False, data=True)

duty_min = 0
duty_max = 51000
freq = 500
duty_up = 1000
sweep_down = 0.05
duty_down = 500

sweep = 30000

meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=sweep)

while sweep <= duty_max:
    meter.duty_cycle = sweep
    sweep = sweep + duty_up

sleep(5.1)
