# particle-button-lifx
Use particle button to turn lifx lights on and off

These scrips use:  
Python LifX SDK https://github.com/smarthall/python-lifx-sdk  
mysql https://www.mysql.com/
Particle Internet Button https://www.particle.io/button  
paho python MQTT broker https://pypi.python.org/pypi/paho-mqtt/1.1  

On an Ubuntu 15.04 Server, the scripts lightstatus, lifxinternetbutton and sensors are run on startup using systemd

You will need to edit mysqlinit.py for the user and password for your mysql setup.  
