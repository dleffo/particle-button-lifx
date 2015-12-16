#### need to put your deviceID here
deviceID = "infrared"
delay = 1000
sqlite_file = '/home/david/lifx/automation.db'

import time
import sqlite3
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/#")
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = str(msg.payload)
    topic = msg.topic
#    try:
#        c.execute('''INSERT INTO mqtt (topic, message) VALUES(?,?)''', (payload, topic))
#    except sqlite3.IntegrityError:
#        print("ERROR")
#    conn.commit()
    try:
        if str(msg.topic) == "particle/" + str(deviceID) + "/sensors/temp":
            print("Temperature data detected")
            try:
                c.execute('''INSERT INTO sensors (device, temperature) VALUES(?,?)''', (str(deviceID), payload))
            except sqlite3.IntegrityError:
                print("ERROR")
            conn.commit()
            min = 16
            max = 30
            brightness = 100
            temp = float(payload)
            red = round((temp-min)*brightness/(max-min))
            blue = round((max-temp)*brightness/(max-min))
            if (temp < (max+min)/2):
                green = round(brightness/2 - ((brightness/2) * ((max + min)/2 - temp) / ((max - min)/2)))
            else:
                green = round(brightness/2 - ((brightness/2 * (temp - (max + min)/2))/ ((max - min)/2)))
            msgtopic = "house/lounge/temperature"
            print msgtopic
            print payload
            client.publish(msgtopic, payload, 2, True)
            payload = "Power:True/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
            msgtopic = "particle/InternetButton/buttons/2"
            print msgtopic
            print payload
            client.publish(msgtopic, payload, 2, True)
            msgtopic = "home/lounge/temperature"
            print msgtopic
            print payload
            client.publish(msgtopic, payload, 2, True)

    except KeyError:
        print "Hokey lightbulb code shat it's duds on a KeyError!"
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttsensors.py','KeyError'))
        conn.commit()
    except AttributeError:
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttsensors.py', 'AttributeError'))
        print "Hokey lightbulb code shat it's duds on an AttributeError!"
        conn.commit()
    except KeyboardInterrupt:
        print "Keyboard Interrupt.  Exiting"

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()
client = mqtt.Client()
time.sleep(1)
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.home.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
