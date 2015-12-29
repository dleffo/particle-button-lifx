# for setting up the database
import lifx
from lifx.color import HSBK
import MySQLdb
import time
import mysqlinit

user = mysqlinit.user()
password = mysqlinit.password()
cnx = MySQLdb.connect(user=user, passwd=password, host='127.0.0.1', db='automation')
cursor=cnx.cursor()

print "Welcome to the setup."
print "This script will ask you questions to setup what lights turn on/off for what button"
response = 'N'
while(response == 'N'):
    print "These lights have been detected:"
    lights = lifx.Client()
    time.sleep(1)
    n = 0
    for g in lights.get_groups():
        print "Group :" + str(g.label)
        for l in g:
            print "    " + str(l.label)
            n = n + 1
    print "Total lights detected: " + str(n)
    answer = raw_input("Is this correct? (Y/N): ")
    if answer == 'Y' or answer == 'y':
        response = 'Y'
    else:
        print "The script will now retry to detect the lights.  If it continues to not find them all, have you tried turning it off and on again?"
print "We will now setup the button behaviour.  For each light you will be asked what button you would like to turn it on or off with."
print "Button 1 is where the USB connector is, then clockwise 2, 3 and 4.  Enter 0 if you do not want any button to control the light."
answer = (raw_input("Note this will clear out the current button behaviour.  Do you want to proceed? Y/N") or 'Y')

if answer == 'Y' or answer == 'y':
    cursor.execute("DROP TABLE IF EXISTS lightsettings")
    cursor.execute("""CREATE TABLE lightsettings(lightID TEXT, label TEXT,IsGroup INTEGER, Grouplabel TEXT, Button INTEGER, Power INTEGER, Hue FLOAT, Saturation FLOAT, Brightness FLOAT, Kelvin FLOAT, ID INTEGER PRIMARY KEY AUTO_INCREMENT UNIQUE)""")
    cnx.commit()
    for g in lights.get_groups():
        print "------------------"
        groupanswer = (raw_input("For group " + str(g.label) + " which button would you like:") or 0)
        cursor.execute("""INSERT INTO lightsettings(label, IsGroup, Grouplabel, Button, Hue, Saturation, Brightness, Kelvin) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')""" % (g.label,1,g.label,groupanswer,0,0,0.75,3500))
        cnx.commit()
        for l in g:
            if str(l.power) == "True":
                power = 1
            else:
                power = 0
            cursor.execute("""INSERT INTO lightsettings(lightID, label, IsGroup, Grouplabel, Button, Power, Hue, Saturation, Brightness, Kelvin) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (hex(l.id),l.label,0,g.label,groupanswer,power,0,0,0.75,3500))
            cnx.commit()
        answer = (raw_input("Do you want to adjust this group's lights individually?") or 'Y')
        if answer == 'Y' or answer == 'y':
            for l in g:
                lightanswer = (raw_input("For light " + str(l.label) + " which button would you like:") or 0)
                cursor.execute("""UPDATE lightsettings SET Button = '%s' WHERE label = '%s' AND IsGroup = 0""" % (lightanswer, l.label))
else:
    print "Exiting..."
print "All done."
