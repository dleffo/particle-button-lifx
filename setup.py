# for setting up the database
import getpass
import lifx
from lifx.color import HSBK
import MySQLdb
import time
import mysqlinit

print "Welcome to the setup."
print "This script will ask you questions to setup the database and determine what lights turn on/off for what button"
print "NOTE!  You need to enter the MySQL root password to be able to set up the database and database user."
user = 'root'
rtpassword = getpass.getpass('Please enter MySQL root password:')
print "---------"
print "What would you like the 'automation' user password to be for MySQL?"
password = getpass.getpass("Please enter MySQL 'automation' user password:")
cnx = MySQLdb.connect(user=user, passwd=rtpassword)
cursor=cnx.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS automation")
cursor.execute("SELECT user FROM mysql.user WHERE user = 'automation'")
ifexists = cursor.fetchone()
if not ifexists:
    creation = "CREATE USER automation identified by '%s'" % password
    cursor.execute(creation)
    cnx.commit()
else:
    print "User 'automation' already exists.  Please make sure the password supplied is the password for the existing 'automation' user"
privileges = "GRANT ALL PRIVILEGES ON automation.* to automation"
cursor.execute(privileges)
cursor.execute("FLUSH PRIVILEGES")
cnx.commit()
cursor.execute("USE automation")
cursor.execute("CREATE TABLE IF NOT EXISTS `error` (\
                `app` text,\
                `error` text,\
                `datetime` datetime DEFAULT CURRENT_TIMESTAMP,\
                `id` int(11) NOT NULL AUTO_INCREMENT,\
                PRIMARY KEY (`id`)\
                )")
cursor.execute("CREATE TABLE IF NOT EXISTS `lights` (\
                `label` text,\
                `power` int(11) DEFAULT NULL,\
                `hue` double DEFAULT NULL,\
                `saturation` double DEFAULT NULL,\
                `brightness` double DEFAULT NULL,\
                `kelvin` int(11) DEFAULT NULL,\
                `datetime` datetime DEFAULT CURRENT_TIMESTAMP,\
                `id` int(11) NOT NULL AUTO_INCREMENT,\
                PRIMARY KEY (`id`)\
                )")
cursor.execute("CREATE TABLE IF NOT EXISTS `mqtt` (\
                `topic` text,\
                `message` text,\
                `datetime` datetime DEFAULT CURRENT_TIMESTAMP,\
                `id` int(11) NOT NULL AUTO_INCREMENT,\
                PRIMARY KEY (`id`)\
                )")
cnx.commit()

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
