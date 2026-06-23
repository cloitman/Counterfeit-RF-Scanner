#!/usr/bin/env python3

""" This is a script for calibrating grid on printer bed. """

__author__ = "Charlie Loitman"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

from octorest import OctoRest
import json

#Connects to server
#Connects to the printer, if there is error, exit
#Home the printer head
#Make zig zag pattern across FPGA
def make_client(url,apikey):
	try:
		client = OctoRest(url=url, apikey=apikey)
		return client
	except Exception as e:
		print(e)
		return

def moveTo(url,apikey):
	c = make_client(url,apikey)

	try:
		c.connect()
	except:
		print("Connection Failed")
		return
	print(c.state())
	c.gcode("G21")
	c.gcode("G90")
	c.gcode("G0")
	c.home()
	c.gcode("G28 X0 Y0")
	c.gcode("G28 Z0")
	x=1
	y=1
	xOld = 0
	yOld = 0
	zOld = 0
	print('Enter coordinates to move to that position.\nIf either the x- or y-coordinate is negative, program stops.')
	while True:
		print('Enter the desired x-coordinate: ')
		x=int(input())
		if (x<0):
			break
		print('Enter the desired y-coordinate: ')
		y=int(input())
		if (y<0):
			break
		print('Enter the desired z-coordinate')
		z=int(input())
		c.jog(x=(x-xOld),y=(y-yOld),z=(z-zOld))
		xOld = x
		yOld = y
		zOld = z
	return

if __name__ == "__main__":
	_settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'settings.json')
	with open(_settings_path) as _f:
		_settings = json.load(_f)
	url = _settings['url']
	apikey = _settings['apikey']
	moveTo()
