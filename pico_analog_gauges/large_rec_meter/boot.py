from time import sleep
import board
import pwmio
import usb_cdc

usb_cdc.enable(console=False, data=True)

duty_min = 500
duty_max = 12000
freq = 500

meter = pwmio.PWMOut(board.GP5, frequency=freq, duty_cycle=duty_min)

sweep = duty_min

while sweep <= duty_max:
    meter.duty_cycle = sweep
    sleep(0.05)
    sweep = sweep + 275
    
while sweep >= (duty_max - 100):
    meter.duty_cycle = sweep
    sleep(0.01)
    sweep = sweep - 30

while sweep >= duty_min:
    meter.duty_cycle = sweep
    sleep(0.05)
    sweep = sweep - 275

meter.deinit()
