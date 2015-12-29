#!/usr/bin/python

import lifx
from lifx.color import HSBK
import time
import colorsys
import sys
import argparse
import socket
import mysqlinit

ipaddress = mysqlinit.get_lan_ip()

parser = argparse.ArgumentParser(description='Control your lifx lights')
parser.add_argument('-l', '--light', nargs='*', help='the light(s) to control.  e.g. -l Study Bedroom1')
parser.add_argument('-g', '--group', nargs='*', help='the group(s) to control. e.g. -g Bedroom')
parser.add_argument('--on', action = 'store_true', help='turn the lights or groups on.  eg. -l Study Bedroom1 --on')
parser.add_argument('--off', action = 'store_true', help='turn the lights or groups off.  eg -l Study Bedroom1 -g Lounge Kitchen --off')
parser.add_argument('--getgroups', action = 'store_true', help='shows all groups and lights in those groups')
parser.add_argument('--hue', help='number between 0 and 360 on the colour wheel.  0/360 is pure red, 120 green and 240 blue')
parser.add_argument('-s', '--saturation', help='number between 0 and 1.  0 is white, 1 is pure colour (up to brightness is 0.5)')
parser.add_argument('-b', '--brightness',help='number between 0 and 1.  0 is dark, 1 is full brighness')
parser.add_argument('-k', '--kelvin',help='number between 2500 and 9000.  If kelvin is specified, hue and saturation are ignored')
parser.add_argument('-d', '--delay', default=0, help='Time to transition from one colour to another.  For power see --fade')
parser.add_argument('-f', '--fade', default=0, help='Time to fade on or off.  For colour transition see --delay')
args = parser.parse_args()

def validate_input():
    if args.hue is not None:
        try:
            float(args.hue)
        except:
            print "Entry for hue is not a number, try again sucker."
            exit()
        if float(args.hue) < 0 or float(args.hue) >360:
            print "Hue is out of range, setting to 0"
            args.hue = 0

    if args.saturation is not None:
        try:
            float(args.saturation)
        except:
            print "Entry for saturation is not a number, try again sucker."
            exit()
        if float(args.saturation) < 0 or float(args.saturation) >1:
            print "Saturation is out of range, setting to 0"
            args.saturation = 0

    if args.brightness is not None:
        try:
            float(args.brightness)
        except:
            print "Entry for brightness is not a number, try again sucker."
            exit()
        if float(args.brightness) < 0 or float(args.brightness) >1:
            print "Brightness is out of range, setting to 1"
            args.brightness = 1

    if args.kelvin is not None:
        try:
            float(args.kelvin)
        except:
            print "Entry for kelvin is not a number, try again sucker."
            exit()

        if float(args.kelvin) < 2500:
            print "Temperature less than 2500, setting to 2500"
            args.kelvin = 2500
        if float(args.kelvin) > 9000:
            print "Temperature greater than 9000, setting to 9000"
            args.kevlin = 9000

    if args.delay is not None:
        try:
            float(args.delay)
        except:
            print "Entry for delay is not a number, try again sucker."
            exit()

        if float(args.delay) < 0:
            print "Delay is negative, setting to 0"
            args.delay = 0

    if args.fade is not None:
        try:
            float(args.fade)
        except:
            print "Entry for fade is not a number, try again sucker."
            exit()

        if float(args.fade) < 0:
            print "Fade is negative, setting to 0"
            args.fade = 0



def colour(light):
    color = light.color
    hue = color.hue
    saturation = color.saturation
    brightness = color.brightness
    kelvin = color.kelvin
    if args.hue:
        hue = float(args.hue)
    if args.saturation:
        saturation = float(args.saturation)
    if args.brightness:
        brightness = float(args.brightness)
    if args.kelvin:
        kelvin = float(args.kelvin)
        hue = 0
        saturation = 0
    newcolor = HSBK(hue, saturation, brightness, kelvin)
    light.fade_color(newcolor, duration = int(float(args.delay)*1000))


def getgroups(lights):
        groups = lights.get_groups()
        for g in groups:
            print "-----------"
            print "-----------"
            print "-----------"
            print g
            for l in g:
                print l.label
                print l.color
        print "-----------"
        print "-----------"
        print "-----------"

def light(lights,light):
    obj = None
    retries = 0
    while not obj:
        obj = lights.by_label(light)
        if obj:
            for l in obj:
                if args.hue > 0 or args.saturation > 0  or args.brightness > 0 or args.kelvin > 0:
                    colour(l)
                if args.on:
                    l.fade_power(True, duration = int(float(args.fade)*1000))
                if args.off:
                    l.fade_power(False, duration = int(float(args.fade)*1000))
        else:
            print "Did not find light.  Retrying..."
            retries = retries + 1
            lights = lifx.Client()
            time.sleep(1)
            if retries > 10:
                print "Tried too many times.  Exiting..."
                obj = " "

def group(lights,group):
    obj = None
    retries = 0
    while not obj:
        obj = lights.group_by_label(group)
        if obj:
            for g in obj:
                for l in g:
                    if args.hue > 0 or args.saturation > 0  or args.brightness > 0 or args.kelvin > 0:
                        colour(l)
                    if args.on:
                        print int(args.fade)
                        l.fade_power(True, duration = int(float(args.fade)*1000))
                    if args.off:
                        print int(args.fade)
                        l.fade_power(False, duration = int(float(args.fade)*1000))
        else:
            print "Did not find light.  Retrying..."
            retries = retries + 1
            lights = lifx.Client()
            time.sleep(1)
            if retries > 10:
                print "Tried too many times.  Exiting..."
                obj = " "


validate_input()
lights = lifx.Client(address=ipaddress)
time.sleep(0.5)


if args.getgroups:
    getgroups(lights)

if args.light:
    for n in args.light:
        light(lights,n)

if args.group:
    for n in args.group:
        group(lights,n)
