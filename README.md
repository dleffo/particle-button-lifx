# particle-button-lifx
Use particle button to turn lifx lights on and off

These scrips use:  
Python LifX SDK https://github.com/smarthall/python-lifx-sdk  
sqlite https://www.sqlite.org/  
Particle Internet Button https://www.particle.io/button  
paho python MQTT broker https://pypi.python.org/pypi/paho-mqtt/1.1  

The following lines are added to crontab to start them on bootup. 
@reboot sleep 20 && python ~/lifx/mqttlifx.py > ~/logs/mqttlifx.log 2>&1
@reboot python ~/lifx/sqlite.py > ~/logs/sqlite.py 2>&1
