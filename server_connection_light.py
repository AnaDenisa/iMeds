from network import LoRa
import socket
import time
import binascii

from machine import PWM
import math
import time

from machine import ADC

class Servo:
    """
    A simple class for controlling hobby servos.

    Args:
        pin (machine.Pin): The pin where servo is connected. Must support PWM.
        freq (int): The frequency of the signal, in hertz.
        min_us (int): The minimum signal length supported by the servo.
        max_us (int): The maximum signal length supported by the servo.
        angle (int): The angle between the minimum and maximum positions.

    """
    def __init__(self, pin, freq=50, min_us=600, max_us=2400, angle=180):
        self.min_us = min_us
        self.max_us = max_us
        self.us = 0
        self.freq = freq
        self.angle = angle
        print (freq)
        pwm = PWM(0, frequency=freq)
        self.pwm = pwm.channel (0, pin=pin, duty_cycle=0)

    def write_us(self, us):
        """Set the signal to be ``us`` microseconds long. Zero disables it."""
        if us == 0:
            self.pwm.duty_cycle(0)
            return
        us = min(self.max_us, max(self.min_us, us))
        duty = us * 1024 * self.freq // 1000000
        print ('duty: '+str(duty/1023))
        self.pwm.duty_cycle(duty/1023)

    def write_angle(self, degrees=None, radians=None):
        """Move to the specified angle in ``degrees`` or ``radians``."""
        if degrees is None:
            degrees = math.degrees(radians)
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.angle
        self.write_us(us)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('70B3D57EF00069DD'.replace(' ',''))
app_key = binascii.unhexlify('84AE14D0729414351DE9795779D8E15B'.replace(' ',''))

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

servo_var = Servo(pin='P23')

adc = ADC(0)
adc_c = adc.channel(pin='P17', attn=ADC.ATTN_11DB)

# send some data
while True:
    print ('Sending data')
    # send some data
    s.setblocking(True)
    # s.send('LoPy trimite')

    # get any data received...
    s.setblocking(False)

    data = s.recv(64)
    #print(type(str(data, 'utf-8')))
    if str(data, 'utf-8') == 'ana':
        print('received Costi signal')
        for i in range (0, 180):
            servo_var.write_angle(i)
            time.sleep (0.08)
            print(data)


    light_value = adc_c.value()
    print ('Sending the light value')

    # send some data
    s.setblocking(True)

    s.send(str(light_value))
    print(light_value)

    s.setblocking(False)

    # wait a random amount of time
    time.sleep(machine.rng() & 0x0F)
