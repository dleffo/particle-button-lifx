#### need to put your deviceID here
deviceID = "infrared"
mqttclient = "mqtt.home.local"
delay = 1000

import time
import MySQLdb
import paho.mqtt.client as mqtt
import mysqlinit

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
    try:
        if str(msg.topic) == "particle/" + str(deviceID) + "/sensors/temp":
            print("Temperature data detected")
            cursor.execute('''INSERT INTO sensors (device, temperature) VALUES('%s','%s')''' % (str(deviceID), payload))
            cnx.commit()
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
            msgtopic = "home/lounge/temperature"
            client.publish(msgtopic, payload, 2, True)
            payload = "Power:True/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
            msgtopic = "particle/InternetButton/buttons/2"
            client.publish(msgtopic, payload, 2, True)

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
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttclient, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
