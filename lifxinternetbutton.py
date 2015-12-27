#### need to put your deviceID here
deviceID = "InternetButton"
mqttclient = "mqtt.home.local"
delay = 1000

import lifx
import paho.mqtt.client as mqtt
from lifx.color import HSBK
import time
import MySQLdb
import mysqlinit

def toggle_lights(button):
    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s'""" % (button,0))
    row = cursor.fetchone()
    while row is not None:
        toggle = ""
        for l in lights.by_label(row[1]):
            if str(l.power) == "True":
                toggle = "Off"
        row = cursor.fetchone()
    if toggle == "Off":
        power = False
    else:
        power = True
    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s'""" %(button,0))
    row = cursor.fetchone()
    while row is not None:
        for l in lights.by_label(row[1]):
            l.power = power
            row = cursor.fetchone()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/#")
    client.subscribe("lifx/#")
    client.publish("particle/status","lifxinternetbutton is alive, version" + str(0.4))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = str(msg.payload)
    topic = msg.topic
    print topic
    print payload
    print " "
    cursor.execute("""INSERT INTO mqtt (topic, message) VALUES('%s','%s')""" % (payload, topic))
    cnx.commit()
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
        cursor.execute("""INSERT INTO error (app, error) VALUES ('%s','%s')""" % ('lifxinternetbutton.py','KeyError'))
        cnx.commit()
        raise
    except AttributeError:
        cursor.execute('''INSERT INTO error (app, error) VALUES ('%s','%s')''' % ('lifxinternetbutton.py', 'AttributeError'))
        cnx.commit()
        raise
    except KeyboardInterrupt:
        print "Keyboard Interrupt.  Exiting"

user = mysqlinit.user()
password = mysqlinit.password()
cnx = MySQLdb.connect(user=user, passwd=password, host='127.0.0.1', db='automation')
cursor=cnx.cursor()
lights = lifx.Client()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttclient, 1883, 60)
client.loop_forever()
