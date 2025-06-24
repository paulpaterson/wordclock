
import gpiozero
import time
import signal

i = 0

#led = gpiozero.LED(17)

#while i < 100:
#    led.on()
#    time.sleep(1)
#    led.off()
#    time.sleep(0.1)
#    i += 1

b = gpiozero.Button(2)
print('Waiting for the button to be pressed')
#b.wait_for_press()
#print('The button was pressed')

def on():
    print('Button is on')

def off():
    print('Button is off')

b.when_pressed = on
b.when_released = off

signal.pause()


