# module for accessing mysql database
import os
import socket

if os.name != "nt":
    import fcntl
    import struct


def user():
    user = 'automation'
    return user

def password():
    password = 'BJgYbM4un5G1a8OQTk41'
    return password

def ipaddress():
    ipaddress = '192.168.1.24'
    return ipaddress


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                            ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

def get_token():
    token = "cf48af89c15018b54b2bd4d6fbc63be8b6bd31726c24885359b77c5577f79be8"
    return token
