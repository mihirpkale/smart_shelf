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

THRESHHOLD_TRIGGER = 3000
LAST_HIGH_READING = 0
LAST_RELOAD_TIME = 0
LAST_ALERT_SENT = 0
ZERO_RANGE = 200



def call_alert(message):
	if message == "EXPIRED":
		print "alert called for EXPIRY"
	if message =="FINISHED":
		print "alert called for FINISHED"




while True:
	try:
       		val = hx.get_weight(5)
        	print val
		if val > ZERO_RANGE:
			if val < THRESHHOLD_TRIGGER:
				call_alert("FINISHED")
			elif val > LAST_HIGH_READING:
				LAST_HIGH_READING = val
				LAST_RELOAD_TIME = datetime.datetime.now()
				print "NEW RELOAD READ AND RELOAD TIME IS....", +str(LAST_HIGH_READING)+"....."+str(LAST_RELOAD_TIME)
			elif datetime.datetime.now() < (LAST_RELOAD_TIME + datetime.timedelta(days=SHELF_LIFE)):
				call_alert("EXPIRED")
		else: print "val is less than ZERO_RANGE, will do nothing"

			
        	hx.power_down()
        	hx.power_up()
    	except (KeyboardInterrupt, SystemExit):
        	cleanAndExit()
