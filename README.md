# particle-button-lifx
Use particle button to turn lifx lights on and off

These scrips use:  
Python LifX SDK https://github.com/smarthall/python-lifx-sdk  
mysql https://www.mysql.com/
Particle Internet Button https://www.particle.io/button  
paho python MQTT broker https://pypi.python.org/pypi/paho-mqtt/1.1  

On an Ubuntu 15.04 Server, the scripts lightstatus, lifxinternetbutton and sensors are run on startup using systemd

You will need to create a file mysqlinit.py in the same directory as these scripts for the user and password for mysql.  These will need to be the same username/password combination you have setup in mysql.

e.g.:

def user():
    user = 'automation'
    return user

def password():
    password = 'mypassword'
    return password
