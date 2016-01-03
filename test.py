

import MySQLdb
host = 'localhost'
user = 'root'
passwd = 'M2xw3ll'
mydb = MySQLdb.connect(host, user, passwd)
cursor = mydb.cursor()
try:
    mkuser = 'symphony'
    creation = "CREATE USER IF NOT EXISTS '%s'@'%s'" %(mkuser, host)
    print creation
    results = cursor.execute(creation)
    print "User creation returned", results
    mkpass = 'n0n3wp4ss'
    setpass = "SET PASSWORD FOR '%s'@'%s' = PASSWORD('%s')" %(mkuser, host, mkpass)
    results = cursor.execute(setpass)
    print "Setting of password returned", results
    granting = "GRANT ALL ON *.* TO '%s'@'%s'" %(mkuser, host)
    results = cursor.execute(granting)
    print "Granting of privileges returned", results
    granting = "REVOKE ALL PRIVILEGES ON *.* FROM '%s'@'%s'" %(mkuser, host)
    results = cursor.execute(granting)
    print "Revoking of privileges returned", results
except MySQLdb.Error, e:
    print e
