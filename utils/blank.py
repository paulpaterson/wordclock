import pi5neo  # type: ignore
import sys

p = pi5neo.Pi5Neo('/dev/spidev0.0', 16*16, 1000)
if len(sys.argv) > 1:
    print('Showing white')
    #p.set_led_color(1, 255, 255, 255)
    p.fill_strip(255, 255, 255)
    p.update_strip()
else:
    print('Clearing strip')
    p.clear_strip()


