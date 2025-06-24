
import gpiozero
import time

i = 0

led = gpiozero.LED(17)

while i < 100:
    led.on()
    time.sleep(1)
    led.off()
    time.sleep(0.1)
    i += 1


