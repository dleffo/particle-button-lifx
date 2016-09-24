# import lifx
import MySQLdb
import MySQLdb.cursors
# from lifx.color import HSBK
import time
import paho.mqtt.client as mqtt
import colorsys


import requests
import json
import mysqlinit

version = 0.1

def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.publish("particle/status","httplightstatus is alive, version" + str(version))

def on_message(client, userdata, msg):
    print "message received"

def on_disconnect(client, userdata, rc):
    if rc!=0:
        client.reconnect()

user = mysqlinit.user()
password = mysqlinit.password()
ipaddress = mysqlinit.get_lan_ip()
cnx = MySQLdb.connect(user=user, passwd=password, host='127.0.0.1', db='automation', cursorclass=MySQLdb.cursors.DictCursor)
cursor=cnx.cursor()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect("mqtt.home.local", 1883, 60)
token = mysqlinit.get_token()
headers = {
    "Authorization": "Bearer %s" % token,
}
dimfactor = 10
while(1):
    start = time.time()
    response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
    lights = json.loads(response.text)
    cursor.execute('''SELECT * FROM lightsettings WHERE IsGroup=0''')
    dblabel = [i['label'] for i in cursor.fetchall()]
    for n in dblabel:
        for l in lights:
            if l['label'] == n:
                if l['power'] == 'off':
                    power = 0
                    buttonpower = False
                else:
                    power = 1
                    buttonpower = True
                color = l['color']
                hue = color['hue']
                saturation = color['saturation']
                brightness = l['brightness']
                kelvin = color['kelvin']
                button = 0
                label = l['label']
                cursor.execute('''SELECT * FROM lights WHERE id = (SELECT  MAX(ID) FROM lights WHERE label='%s')''' % (label,))
                row = cursor.fetchone()
                if row == None:
                    cursor.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES('%s','%s','%s','%s','%s','%s')''' % (label, power, round(hue,0), round(saturation,2), round(brightness,2), kelvin))
                    print "New Lightbulb Detected!  Adding to database."
                    cnx.commit()
                else:
                    if power != row['power']  or round(hue,0) != row['hue'] or round(saturation,2) != row['saturation'] or round(brightness,2) != row['brightness'] or kelvin != row['kelvin']:
                        cursor.execute('''INSERT INTO lights (label, power, hue, saturation, brightness, kelvin) VALUES('%s','%s','%s','%s','%s','%s')''' % (label, power, round(hue,0), round(saturation,2), round(brightness,2), kelvin))
                        print "Change in lightbulb state detected!"
                        cnx.commit()
                        cursor.execute('''SELECT * FROM lightsettings WHERE ID = (SELECT MAX(ID) FROM lightsettings WHERE label='%s')''' % (label,))
                        buttonrow = cursor.fetchone()
                        button = buttonrow['Button']
                        cursor.execute("""UPDATE lightsettings SET Power = '%s', Hue = '%s', Saturation = '%s', Brightness = '%s' WHERE label = '%s' AND IsGroup = 0""" % (power,round(hue,0), round(saturation,2), round(brightness,2),label))
                        cnx.commit()
                        cursor.execute("""SELECT AVG(Hue), AVG(Saturation), AVG(Brightness) FROM lightsettings WHERE button='%s' AND IsGroup='%s' AND Power = 1""" %(button,0))
                        dbbutton = cursor.fetchone()
                        if dbbutton['AVG(Hue)'] is not None:
                            hue = dbbutton['AVG(Hue)']
                            saturation = dbbutton['AVG(Saturation)']
                            brightness = dbbutton['AVG(Brightness)']
                        rgb = colorsys.hsv_to_rgb(hue/360, saturation, brightness)
                        red = round(rgb[0] * 255 / dimfactor)
                        green = round(rgb[1] * 255 / dimfactor)
                        blue = round(rgb[2] * 255 / dimfactor)
                        if power != row['power']:
                            payload = "Power:" + str(buttonpower) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                            msgtopic = "particle/InternetButton/buttons/" + str(button)
                            client.publish(msgtopic, payload, 2, True)
                        elif power == 1:
                            if hue != row['hue'] or saturation != row['saturation'] or brightness != row['brightness']:
                                payload = "Power:" + str(buttonpower) + "/" + "Red:" + str(red) + "/" + "Green:" + str(green) + "/" + "Blue:" + str(blue) + "/"
                                msgtopic = "particle/InternetButton/buttons/" + str(button)
                                client.publish(msgtopic, payload, 2, True)
    client.loop()
    end = time.time()
    elapsed = end - start
    while (elapsed < 1):
        time.sleep(0.1)
        end = time.time()
        elapsed = end - start
