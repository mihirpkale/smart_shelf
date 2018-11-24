import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711
import datetime

def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

hx = HX711(5, 6)
hx.set_reading_format("LSB", "MSB")
#hx.set_reference_unit(-411)
hx.reset()
hx.tare()

THRESHHOLD_TRIGGER = 
LAST_HIGH_READING = 0
LAST_ALERT_SENT

def call_init(reading, curr_time):
	print "Init function called"
	LAST_HIGH_READING = reading
	LAST_RELOAD_TIME = curr_time

def call_smart_shelf_logic(reading):
	if reading < THRESHHOLD_TRIGGER:
		call_alert()
	else:
		if reading >= LAST_HIGH_READING:
			curr_time = datetime.datetime.now()
			call_init(reading, curr_time)
			print "New load detected...resetting HIGH_LOAD and LOAD_TIME"


def main():

	while True:
    	try:
       		val = hx.get_weight(5)
        	print val
		call_smart_shelf_logic(int(val))
        	hx.power_down()
        	hx.power_up()
    	except (KeyboardInterrupt, SystemExit):
        	cleanAndExit()
