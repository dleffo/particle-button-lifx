# for setting up the database
import lifx
from lifx.color import HSBK
import sqlite3
import time

sqlite_file = "/home/david/lifx/automation.db"


conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

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
    c.execute('''DROP TABLE IF EXISTS lightsettings''')
    c.execute('''CREATE TABLE "lightsettings" (lightID TEXT, `label` TEXT,`IsGroup` INTEGER, 'Grouplabel' TEXT, `Button` INTEGER,`Hue` REAL,`Saturation` REAL,`Brightness` REAL,`Kelvin` REAL,`ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE)''')
    conn.commit()
    for g in lights.get_groups():
        groupanswer = (raw_input("For group " + str(g.label) + " which button would you like:") or 0)
        c.execute('''INSERT INTO lightsettings (label, IsGroup, Grouplabel, Button, Hue, Saturation, Brightness, Kelvin) VALUES (?,?,?,?,?,?,?,?)''',(g.label,1,g.label,groupanswer,0,0,0.75,3500))
        for l in g:
            c.execute('''INSERT INTO lightsettings (lightID, label, IsGroup, Grouplabel, Button, Hue, Saturation, Brightness, Kelvin) VALUES (?,?,?,?,?,?,?,?,?)''',(l.id,l.label,0,g.label,groupanswer,0,0,0.75,3500))
        conn.commit()
        answer = (raw_input("Do you want to adjust this group's lights individually?") or 'Y')
        if answer == 'Y' or answer == 'y':
            for l in g:
                lightanswer = (raw_input("For light " + str(l.label) + " which button would you like:") or 0)
                c.execute('''UPDATE lightsettings SET Button = ? WHERE label = ? AND IsGroup = 0''', (lightanswer, l.label))
else:
    print "Exiting..."
print "All done."
