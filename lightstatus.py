import lifx
import MySQLdb
from lifx.color import HSBK
import time
import paho.mqtt.client as mqtt
import colorsys
import mysqlinit

version = 0.32
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/status")
    client.publish("particle/status","lightstatus is alive, version" + str(0.4))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.

def on_message(client, userdata, msg):
    print "message received"

def on_disconnect(client, userdata, rc):
    if rc!=0:
        client.reconnect()

dimfactor = 10


user = mysqlinit.user()
password = mysqlinit.password()
cnx = MySQLdb.connect(user=user, passwd=password, host='127.0.0.1', db='automation')
cursor=cnx.cursor()
lights = lifx.Client()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect("mqtt.home.local", 1883, 60)

while(1):
    try:
        for l in lights.get_devices():
            label = l.label
            if l.power == True:
                power = 1
            else:
                power = 0
            color = l.color
            hue = color.hue
            saturation = color.saturation
            brightness = color.brightness
            kelvin = color.kelvin
            button = 0
            cursor.execute('''SELECT * FROM lights WHERE id = (SELECT  MAX(ID) FROM lights WHERE label='%s')''' % (label,))
            row = cursor.fetchone()
            if row == None:
                cursor.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES('%s','%s','%s','%s','%s','%s')''' % (label, power, round(hue,0), round(saturation,2), round(brightness,2), kelvin))
                print "New Lightbulb Detected!  Adding to database."
                cnx.commit()
            else:
                if power != row[1]  or round(hue,0) != row[2] or round(saturation,2) != row[3] or round(brightness,2) != row[4] or kelvin != row[5]:
                    cursor.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES('%s','%s','%s','%s','%s','%s')''' % (label, power, round(hue,0), round(saturation,2), round(brightness,2), kelvin))
                    print "Change in lightbulb state detected!"
                    cnx.commit()
                    cursor.execute('''SELECT * FROM lightsettings WHERE ID = (SELECT MAX(ID) FROM lightsettings WHERE label='%s')''' % (label,))
                    buttonrow = cursor.fetchone()
                    button = buttonrow[4]
                    print button
                    rgb = colorsys.hsv_to_rgb(hue/360, saturation, brightness)
                    red = round(rgb[0] * 255 / dimfactor)
                    green = round(rgb[1] * 255 / dimfactor)
                    blue = round(rgb[2] * 255 / dimfactor)
                    if power != row[1]:
                        payload = "Power:" + str(l.power) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                        msgtopic = "particle/InternetButton/buttons/" + str(button)
                        print "topic is: " + msgtopic
                        client.publish(msgtopic, payload, 2, True)
                    elif power == 1:
                        if hue != row[2] or saturation != row[3] or brightness != row[4]:
                            payload = "Power:" + str(l.power) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                            msgtopic = "particle/InternetButton/buttons/" + str(button)
                            print msgtopic
                            print payload
                            client.publish(msgtopic, payload, 2, True)

        time.sleep(0.1)
        client.loop()

    except KeyError:
        cursor.execute('''INSERT INTO error (app, error) VALUES ('%s','%s')''' % ('lightstatus.py','TypeError'))
        cnx.commit()
        raise
    except AttributeError:
        cursor.execute('''INSERT INTO error (app, error) VALUES ('%s','%s')''' % ('lightstatus.py','TypeError'))
        cnx.commit()
        raise
    except KeyboardInterrupt:
        print "Keyboard Interrupt.  Exiting"
        exit()
