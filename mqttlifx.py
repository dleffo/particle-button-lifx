#### need to put your deviceID here
deviceID = "InternetButton"
delay = 1000
########################################
#Change the path to your sqlite database here
sqlite_file = '/home/david/lifx/automation.db'
########################################


import lifx
import paho.mqtt.client as mqtt
from lifx.color import HSBK
import sqlite3
import time

def toggle_lights(button):
    try:
        c.execute('''SELECT * FROM lightsettings WHERE button=? AND IsGroup=?''', (button,0))
    except sqlite3.IntegrityError:
        print("SQLite IntegrityError")
    finish = 0
    while (finish == 0):
        row = c.fetchone()
        if row == None:
            finish = 1
        else:
            toggle = ""
            print "Row is: " + str(row)
            for l in lights.by_label(row[1]):
                print l
                if str(l.power) == "True":
                    toggle = "Off"
                    print str(l.label) + "is on"

    if toggle == "Off":
        power = False
    else:
        power = True
    try:
        c.execute('''SELECT * FROM lightsettings WHERE button=? AND IsGroup=?''', (button,0))
    except sqlite3.IntegrityError:
        print("SQLite IntegrityError")
    finish = 0
    while (finish == 0):
        row = c.fetchone()
        if row == None:
            finish = 1
        else:
            for l in lights.by_label(row[1]):
                if l.label == row[1]:
                    l.power = power


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/#")
    client.subscribe("lifx/#")
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = str(msg.payload)
    topic = msg.topic
    print topic
    print payload
    print " "
    try:
        c.execute('''INSERT INTO mqtt (topic, message) VALUES(?,?)''', (payload, topic))
    except sqlite3.IntegrityError:
        print("ERROR")
        raise
    conn.commit()
    try:
        if str(msg.topic) == "particle/" + str(deviceID) + "/buttons":
            if str(msg.payload) == 'Button 1 Pressed':
                button = 1
                toggle_lights(button)
            if str(msg.payload) == 'Button 2 Pressed':
                colour = HSBK(0,0,0.75,3200)
                for l in lights.get_devices():
                    l.fade_color(colour)
                    topic = str(msg.topic) + "/2"
                    client.publish(topic, "Power:True/Red:32/Green:32/Blue:32")
                client.publish(msg.topic, "Set lights to standard colour")
            if str(msg.payload) == 'Button 3 Pressed':
                button = 3
                toggle_lights(button)
            if str(msg.payload) == 'Button 4 Pressed':
                button = 4
                toggle_lights(button)
    except KeyError:
        print "Hokey lightbulb code shat it's duds on a KeyError!"
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttlifx.py','KeyError'))
        conn.commit()
        raise
    except AttributeError:
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttlifx.py', 'AttributeError'))
        print "Hokey lightbulb code shat it's duds on an AttributeError!"
        conn.commit()
        raise
    except KeyboardInterrupt:
        print "Keyboard Interrupt.  Exiting"

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

lights = lifx.Client()
print lights
client = mqtt.Client()
print client
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.home.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
