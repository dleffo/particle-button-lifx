import lifx
import paho.mqtt.client as mqtt
from lifx.color import HSBK

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("particle/#")
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print "Topic: ", msg.topic+'\nMessage: '+str(msg.payload)
    if str(msg.payload) == "button for Bedroom clicked":
        print("message for Bedroom detected")
        for l in lights.get_devices():
            if l.label == "Davids":
                print("Turning Davids off or on")
                l.power_toggle()
            elif l.label == "Robe":
                print("Turning Robe off or on")
                l.power_toggle()
            elif l.label == "Shitter":
                print("Turning Shitter off or on")
                l.power_toggle()
                client.publish(msg.topic, "Tried toggling Bedroom lights")
    if str(msg.payload) == "Set default colour":
        print("setting colour")
        colour = HSBK(0,0,0.75,3200)
        for l in lights.get_devices():
            l.fade_color(colour)
        client.publish(msg.topic, "Set lights to standard colour")
    if str(msg.payload) == "button for Study clicked":
        print("message for Study detected")
        for l in lights.get_devices():
            if l.label == "Study":
                print("Turning Study off or on")
                l.power_toggle()
                client.publish(msg.topic, "Tried toggling Study lights")

    if str(msg.payload) == "button for Lounge clicked":
        print("message for Lounge detected")
        for l in lights.get_devices():
            label = l.label
            if label.startswith('Lounge'):
                print("Turning Lounge lights off or on")
                l.power_toggle()
        client.publish(msg.topic, "Tried toggling Lounge lights")

lights = lifx.Client()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.home.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
