import lifx
import sqlite3
from lifx.color import HSBK
import time
import paho.mqtt.client as mqtt
import colorsys

version = 0.32
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/status")
    client.publish("particle/status","sqlitev2.py is alive, version" + str(0.3))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.

def on_message(client, userdata, msg):
    print "message received"

def on_disconnect(client, userdata, rc):
    if rc!=0:
        client.reconnect()

dimfactor = 10
########################################
#Change the path to your sqlite database here
sqlite_file = '/home/david/lifx/automation.db'
########################################
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()
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
            power = l.power
            color = l.color
            hue = color.hue
            saturation = color.saturation
            brightness = color.brightness
            kelvin = color.kelvin
            button = 0
            try:
                c.execute('''SELECT * FROM lights WHERE id = (SELECT  MAX(ID) FROM lights WHERE label=?)''', (label,))
            except sqlite3.IntegrityError:
                print("SQLite IntegrityError")
            row = c.fetchone()
            try:
                if power != row[1] or hue != row[2] or saturation != row[3] or brightness != row[4] or kelvin != row[5]:
                    try:
                        c.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES(?,?,?,?,?,?)''', (label, power, hue, saturation, brightness, kelvin))
                        print "Change in lightbulb state detected!"
                        conn.commit()
                    except sqlite3.IntegrityError:
                        print("ERROR")
###############################
# There has to be a better way... add the light labels here, and which button should react to their status
###############################
                    if label == "Study":
                        button = 3
                    if label == "Robe" or label == "Lamp1" or label == "Ensuite" or label == "Bedroom1" or label == "Lamp2":
                        button = 1
                    if label.startswith("Lounge"):
                        button = 4
                        print "button 4"
                    rgb = colorsys.hsv_to_rgb(hue/360, saturation, brightness)
                    red = round(rgb[0] * 255 / dimfactor)
                    green = round(rgb[1] * 255 / dimfactor)
                    blue = round(rgb[2] * 255 / dimfactor)
                    print "hsb colour: " + str(hue) + ":" + str(saturation) + ":" + str(brightness)
                    print "rgb colour: " + str(red) + ":" + str(green) + ":" + str(blue)
                    if power != row[1]:
                        payload = "Power:" + str(power) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                        print payload
                        msgtopic = "particle/InternetButton/buttons/" + str(button)
                        client.publish(msgtopic, payload, 2, True)
                    elif str(power) == "True":
                        if hue != row[2] or saturation != row[3] or brightness != row[4]:
                            payload = "Power:" + str(power) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                            msgtopic = "particle/InternetButton/buttons/" + str(button)
                            print msgtopic
                            print payload
                            client.publish(msgtopic, payload, 2, True)
                    time.sleep(1)
            except TypeError:
                c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttlifx.py','TypeError'))
                conn.commit()
                try:
                    c.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES(?,?,?,?,?,?)''', (label, power, hue, saturation, brightness, kelvin))
                    print "New Lightbulb Detected!  Adding to database."
                    conn.commit()
                except:
                    print ("SQLite IntegrityError")
                print ("TypeError")


        client.loop()

    except KeyError:
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttlifx.py','KeyError'))
        conn.commit()
        raise
    except AttributeError:
        c.execute('''INSERT INTO error (app, error) VALUES (?,?)''', ('mqttlifx.py', 'AttributeError'))
        conn.commit()
        raise
    except KeyboardInterrupt:
        print "Keyboard Interrupt.  Exiting"
        exit()
