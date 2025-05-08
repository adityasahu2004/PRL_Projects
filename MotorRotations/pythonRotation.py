import serial
import time

serialPort = serial.Serial(port="COM3", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
time.sleep(2)
serialPort.write(b"Ready?")
time.sleep(5)
print(serialPort.readline())

serialPort.write(b"m100")
time.sleep(5)
print(serialPort.readline())
print(serialPort.readline())


serialPort.write(b"p100")
time.sleep(5)
print(serialPort.readline())
print(serialPort.readline())


serialPort.close()
