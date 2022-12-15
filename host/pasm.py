import serial
import psutil
import struct
from dataclasses import dataclass


@dataclass
class Temp:
    temp = 0

ser = serial.Serial(
    '/dev/ttyACM0',  # Change this lino to the port the device is connected
    baudrate=115200,
    timeout=0.2)

# This is a stub for code to fetch temperature from your system
temp_sensor = Temp()

counter = 0

disk_percent = 0
net_stat = psutil.net_io_counters()
acc_bytes_sent = net_stat.bytes_sent
acc_bytes_recv = net_stat.bytes_recv
while True:
    cpu_percent = round(psutil.cpu_percent(interval=1))
    if counter % 20 == 0:
        disk_percent = psutil.disk_usage('/').percent

    net_stat = psutil.net_io_counters()
    bits_sent_per_sec = (psutil.net_io_counters().bytes_sent - acc_bytes_sent) * 8
    bits_recv_per_sec = (psutil.net_io_counters().bytes_recv - acc_bytes_recv) * 8
    if bits_recv_per_sec < 0:
        bits_recv_per_sec = 0
    if bits_sent_per_sec < 0:
        bits_sent_per_sec = 0
    acc_bytes_sent = net_stat.bytes_sent
    acc_bytes_recv = net_stat.bytes_recv
    
    print(f"cpu %: {cpu_percent}")
    print(f"mem %: {psutil.virtual_memory().percent}")
    print(f"disk %: {disk_percent}")
    print(f"net down: {bits_recv_per_sec}")
    print(f"net up: {bits_sent_per_sec}")
    print(f"cpu temp: {temp_sensor.temp}")

    message = struct.pack("bbbbIIf", cpu_percent, 0, int(psutil.virtual_memory().percent),
                          int(disk_percent), int(bits_recv_per_sec), int(bits_sent_per_sec), temp_sensor.temp)

    ser.write(message)
    ser.flush()
    counter = counter + 1
    if counter > 20000000:
        counter = 0
