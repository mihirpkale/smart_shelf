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


#these values are standard, dont mess with them
hx = HX711(5, 6)
hx.set_reading_format("LSB", "MSB")


#Set this for calibration of the load cell
hx.set_reference_unit(-355)

#ignore these, let them be where they are
hx.reset()
hx.tare()


#########
## These are important configuration parameters
########

#Weight below which a FINISHED alert will be generated
THRESHHOLD_TRIGGER = 1200


# This is to bypass the error in the load cell
# sometimes the load cell gives random values at zero load
# adjust this value is required
ZERO_RANGE = 250

# keep these as they are
LAST_HIGH_READING = 0
LAST_RELOAD_TIME = datetime.datetime.now() - datetime.timedelta(hours=5)
LAST_ALERT_SENT = datetime.datetime.now() - datetime.timedelta(hours=5)

# These values are in Minutes, keep them small for demo
# In real life they would be in hours
# to convert to hours, change the paramter where-ever "timedelta" is called
ALERT_FREQ = 2
SHELF_LIFE = 1



def call_alert(message):
	if message == "EXPIRED":
		print "alert called for EXPIRY"
	if message =="FINISHED":
		print "alert called for FINISHED"




while True:
	try:
       		val = max(0,int(hx.get_weight(5)))
        	print "Current reading is...:" +str(val)
		if val > ZERO_RANGE:
			if val < THRESHHOLD_TRIGGER:
				if datetime.datetime.now() > (LAST_ALERT_SENT + datetime.timedelta(minutes=ALERT_FREQ)):
					LAST_ALERT_SENT = datetime.datetime.now()	
					call_alert("FINISHED")
				else: print "Last FINISHED alert was sent and have not crossed ALERT FREQ, so will not send"
			elif val > LAST_HIGH_READING:
				LAST_HIGH_READING = val
				LAST_RELOAD_TIME = datetime.datetime.now()
				print "NEW RELOAD READ AND RELOAD TIME IS...." +str(LAST_HIGH_READING)+"....."+str(LAST_RELOAD_TIME)
			elif datetime.datetime.now() > (LAST_RELOAD_TIME + datetime.timedelta(minutes=SHELF_LIFE)):
				if datetime.datetime.now() > (LAST_ALERT_SENT + datetime.timedelta(minutes=ALERT_FREQ)):
					LAST_ALERT_SENT = datetime.datetime.now()
					call_alert("EXPIRED")
				else: print "LAST EXPIRED alert was sent and have not yet crossed ALERT FREQ, so will not send new Alert"	
			else: print "No action required, current reading is higher than THRESHHOLD"
		else: print "val is less than ZERO_RANGE, will do nothing"

			
        	hx.power_down()
        	hx.power_up()
    	except (KeyboardInterrupt, SystemExit):
        	cleanAndExit()
