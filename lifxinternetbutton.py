#### need to put your deviceID here
version = 0.5
deviceID = "InternetButton"
deviceID2 = "gamma"
mqttclient = "mqtt.home.local"
up = True
hotter = True


import lifx
import paho.mqtt.client as mqtt
from lifx.color import HSBK
import time
import MySQLdb
import mysqlinit

def toggle_lights(button):
    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s' AND Power = '%s'""" % (button,0,1))
    row = cursor.fetchone()
    if row is not None:
        power = False
    else:
        power = True
    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s'""" %(button,0))
    dbid = [i[0] for i in cursor.fetchall()]
    for n in dbid:
        try:
            for l in lights.by_id(int(n,16)):
                l.power = power
        except IndexError:
            print "IndexError.  Probably can't find the bulb"
            print n
        except lifx.device.DeviceTimeoutError:
            print "Bulb Timeout Error"


def toggle_lounge(button,up,hotter):
    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s' AND Power = '%s'""" % (4,0,1))
    row = cursor.fetchone()
    if row is not None:
        power = False
    else:
        power = True
    cursor.execute("""SELECT * FROM lightsettings WHERE label='%s' """ % ("Lounge1"))
    row = cursor.fetchone()
    if float(row[8]) < 0.05:
        movie = True
    else:
        movie = False

    cursor.execute("""SELECT * FROM lightsettings WHERE button='%s' AND IsGroup='%s'""" %(4,0))
    dbid = [i[0] for i in cursor.fetchall()]
    if button == 2:
        for n in dbid:
            try:
                for l in lights.by_id(int(n,16)):
                    l.power = power
            except IndexError:
                print "IndexError.  Probably can't find the bulb"
                print n
            except lifx.device.DeviceTimeoutError:
                print "Bulb Timeout Error"
    if button == 5:
        for n in dbid:
            try:
                for l in lights.by_id(int(n,16)):
                    color = l.color
                    hue = color.hue
                    saturation = color.saturation
                    brightness = color.brightness
                    kelvin = color.kelvin
                    if hotter == True:
                        kelvin = kelvin + 500
                    else:
                        kelvin = kelvin - 500
                    if kelvin > 9000:
                        kelvin = 9000
                        hotter = False
                    if kelvin <3500:
                        kelvin = 3500
                        hotter = True
                    colour = HSBK(0,0,brightness,kelvin)
                    l.fade_color(colour,1000)
            except IndexError:
                print "IndexError.  Probably can't find the bulb"
                print n
            except lifx.device.DeviceTimeoutError:
                print "Bulb Timeout Error"
    if button == 4:
        for n in dbid:
            try:
                for l in lights.by_id(int(n,16)):
                    color = l.color
                    hue = color.hue
                    saturation = color.saturation
                    brightness = color.brightness
                    kelvin = color.kelvin
                    if up == True:
                        brightness = brightness + 0.1
                    else:
                        brightness = brightness - 0.1
                    if brightness < 0.1:
                        brightness = 0.1
                        up = True
                    if brightness > 1:
                        brightness = 1
                        up = False
                    colour = HSBK(0,0,brightness,kelvin)
                    l.fade_color(colour,1000)
            except IndexError:
                print "IndexError.  Probably can't find the bulb"
                print n
            except lifx.device.DeviceTimeoutError:
                print "Bulb Timeout Error"
    if button == 3:
        for n in dbid:
            try:
                for l in lights.by_id(int(n,16)):
                    if movie == False:
                        if l.label == "Lounge3" or l.label == "Lounge4":
                            colour = l.color
                            brightness = colour.brightness
                            colour = HSBK(0,1,0.05,3200)
                            l.fade_color(colour,30000)
                        else:
                            colour = HSBK(0,1,0,3200)
                            l.fade_color(colour,30000)
                    if movie == True:
                            colour = HSBK(0,0,0.6,3200)
                            l.fade_color(colour,30000)


            except IndexError:
                print "IndexError.  Probably can't find the bulb"
                print n
            except lifx.device.DeviceTimeoutError:
                print "Bulb Timeout Error"




# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/#")
    client.subscribe("lifx/#")
    client.publish("particle/status","lifxinternetbutton is alive, version" + str(version))
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
        cursor.execute('''INSERT INTO mqtt (topic, message) VALUES('%s','%s')''' % (payload, topic))
        cnx.commit()
    except:
        print "SQL error"
    try:
        if str(msg.topic) == "particle/" + str(deviceID) + "/buttons":
            if str(msg.payload) == 'Button 1 Pressed':
                button = 1
                toggle_lights(button)
            if str(msg.payload) == 'Button 2 Pressed':
                button = 2
                toggle_lights(button)
            if str(msg.payload) == 'Button 3 Pressed':
                button = 3
                toggle_lights(button)
            if str(msg.payload) == 'Button 4 Pressed':
                button = 4
                toggle_lights(button)
            if str(msg.payload) == 'Button 5 Pressed':
                colour = HSBK(0,0,0.75,3200)
                for l in lights.get_devices():
                    l.fade_color(colour)
                    topic = str(msg.topic) + "/2"
                    client.publish(topic, "Power:True/Red:32/Green:32/Blue:32")
                client.publish(msg.topic, "Set lights to standard colour")

        if str(msg.topic) == "particle/" + str(deviceID2) + "/buttons":
            if str(msg.payload) == 'Button 1 Pressed':
                button = 1
            if str(msg.payload) == 'Button 2 Pressed':
                button = 2
            if str(msg.payload) == 'Button 3 Pressed':
                button = 3
            if str(msg.payload) == 'Button 4 Pressed':
                button = 4
            toggle_lounge(button,hotter,up)

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
ipaddress = mysqlinit.get_lan_ip()
cnx = MySQLdb.connect(user=user, passwd=password, host='127.0.0.1', db='automation')
cursor=cnx.cursor()
lights = lifx.Client(address=ipaddress, discoverpoll=600, devicepoll=60)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttclient, 1883, 60)
client.loop_forever()
