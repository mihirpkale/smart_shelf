import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711
import datetime
import boto3
import paho.mqtt.client as mqtt

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
THRESHHOLD_TRIGGER =300


# This is to bypass the error in the load cell
# sometimes the load cell gives random values at zero load
# adjust this value is required
ZERO_RANGE = 100

# keep these as they are
LAST_HIGH_READING = 0
LAST_RELOAD_TIME = datetime.datetime.now()
LAST_ALERT_SENT = datetime.datetime.min

# These values are in Minutes, keep them small for demo
# In real life they would be in hours
# to convert to hours, change the paramter where-ever "timedelta" is called
ALERT_FREQ = 0.75
SHELF_LIFE = 1
RESET_INTERVAL = 20

client = boto3.client("sns")

def call_alert(message):
	if message == "EXPIRED":
		broadcastmsgstr = "Item at or near USE BY Date. Please replace Item"
		print "Item at or near USE BY Date. Please replace the Item"
	if message =="FINISHED":
		broadcastmsgstr = "Item quantity BELOW REORDER LEVEL. Please REORDER Item"
		print "Item Quantity BELOW Reorder Level. Please Order the Item again"

	client.publish(Message=broadcastmsgstr, TopicArn='arn:aws:sns:us-east-1:893516415443:smartShelfAlerts')

def on_connect(mqclient, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	mqclient.subscribe("t_level")
	mqclient.subscribe("alrt_freq")
	mqclient.subscribe("shelf_life")

def on_message(mqclient, userdata, msg):
	if msg.topic == "t_level":
		THRESHHOLD_TRIGGER = int(msg.payload.decode())
		print str(THRESHHOLD_TRIGGER)
	if msg.topic == "alrt_freq":
		ALERT_FREQ = int(msg.payload.decode())
		print str(ALERT_FREQ)
	if msg.topic == "shelf_life":
		SHELF_LIFE = int(msg.payload.decode())
		print str(SHELF_LIFE)



while True:
	try:
			mqclient = mqtt.Client()
			mqclient.connect("localhost",1883,60)
			mqclient.on_connect = on_connect
			mqclient.on_message = on_message
			
			val = max(0,int(hx.get_weight(5)))
			print "Current reading is...:" +str(val)
			if val==0:
				if datetime.datetime.now() > (LAST_RELOAD_TIME + datetime.timedelta(seconds=RESET_INTERVAL)):
					LAST_RELOAD_TIME = datetime.datetime.now()
					LAST_HIGH_READING = 0
					LAST_ALERT_SENT = datetime.datetime.min
					print "Resetting LAST_RELOAD_TIME and READING, Shelf is empty for a considerable amount of time"
			else:
				if val > ZERO_RANGE:
					if val < THRESHHOLD_TRIGGER:
						if datetime.datetime.now() > (LAST_ALERT_SENT + datetime.timedelta(minutes=ALERT_FREQ)):
							LAST_ALERT_SENT = datetime.datetime.now()
							call_alert("FINISHED")
						else: print "Last alert was recently sent. Next alert will be sent after ALERT FREQ interval has passed."
					elif datetime.datetime.now() > (LAST_RELOAD_TIME + datetime.timedelta(minutes=SHELF_LIFE)):
						if datetime.datetime.now() > (LAST_ALERT_SENT + datetime.timedelta(minutes=ALERT_FREQ)):
							LAST_ALERT_SENT = datetime.datetime.now()
							LAST_HIGH_READING = val
							call_alert("EXPIRED")
						else: print "Last alert was recently sent. Next alert will be sent after ALERT FREQ interval has passed."
					elif val >= (LAST_HIGH_READING + 100):
						#Keeping the 100 gms to account for sensor reading variations
						if LAST_RELOAD_TIME > (datetime.datetime.now() - datetime.timedelta(minutes=5)):
							#which means we dont want to reset the LAST RELOAD TIME, it was set less than 5 minutes ago
							LAST_HIGH_READING = val
							print "New load sensed but last reload was less than 5 minutes ago so not re-setting last reload time"
						else:
							LAST_HIGH_READING = val
							LAST_RELOAD_TIME = datetime.datetime.now()
							print "NEW LOAD DETECTED at " +str(LAST_HIGH_READING)+".....at time..."+str(LAST_RELOAD_TIME)
					else: 
						LAST_HIGH_READING = val
						print "No action required, current reading is higher than THRESHHOLD"
				else: print "Recorded weight is less than ZERO_RANGE, Shelf appears to be empty. No action required"
			mqclient.loop_forever()
			hx.power_down()
			hx.power_up()
	except (KeyboardInterrupt, SystemExit):
			cleanAndExit()
