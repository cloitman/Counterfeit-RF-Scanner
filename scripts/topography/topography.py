#!/usr/bin/env python3

""" This is a script for capturing topography data using the depth sensor on 3D printer chasis. """

__author__ = "Charlie Loitman"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

from octorest import OctoRest
import time
import board
import busio
import adafruit_vl53l0x
import pandas as pd
import numpy as np

# Create client for connections to OctoRest server
def make_octorest_client(url, apikey):
    try:
        client = OctoRest(url=url, apikey=apikey)
        return client
    except Exception as e:
        print(e)
        return

# Scan the surface and capture topography data
def scan_surface(url, apikey, outputcsv):

    # Setup I2C bus to the distance sensor
    print('[scan_surface] Setting up I2C bus to the distance sensor...')
    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)

    # Create OctoRest client
    print('[scan_surface] Creating OctoRest client...')
    c = make_octorest_client(url, apikey)

    # Try to connect to the printer
    print('[scan_surface] Connecting to printer...')
    try:
        c.connect()
    except:
        print('[scan_surface] Connection failed.')
        return

    # Get state of the printer
    print('[scan_surface] Printer status is: ' + c.state())

    # Debugging
    print('[scan_surface] Debugging, exiting.')
    exit()

    # FIXME add comment about what this code does
    c.gcode("G21")
    c.gcode("G90")
    c.gcode("G0")
    c.home()
    c.gcode("G28 X0 Y0")
    c.gcode("G28 Z0")

    time.sleep(15.0)
    
    z = np.array(0)
    xArr = []
    yArr = [] 
    xOld = 0
    yOld = 0
    zArr = []
    
    # FIXME suggest to define x/y ranges here
    # and then use them in the for loops
    # all x,y coordinates and step is in mm?
    x_min = 0
    x_max = 0
    x_step = 0
    x_min = 0
    x_max = 0
    x_step = 0

    # FIXME define distance scanner repetitions here
    distance_rep = 12

    #range is x in [30,310] y in [0,160]
    for i in range(60):
        #,310):
        for j in range(30,160):
            #60):
            # FIXME add comment about what this code does
            xArr.append(j) # FIXME i think you mean i not j here?
            yArr.append(j)
            if (i%2==0):
                c.jog(x=1)
            else:
                c.jog(x=-1)
            sumHeight = 0
            time.sleep(2.0)

            # FIXME add comment about what this code does
            count = 0
            while (count < distance_rep):
                sumHeight = sumHeight + vl53.range
                time.sleep(1.0)
                count = count + 1 
            zArr.append(sumHeight/count)
        
        # FIXME add comment about what this code does
        c.jog(y=1)

    # Return print head to home position and save data
    c.home()
    topography = pd.DataFrame({'x':xArr,'y':yArr,'z':zArr})
    topography.to_csv(outputcsv)

    # Finish function
    return

if __name__ == "__main__":
    url = 'http://172.29.34.38'
    apikey = '5615E7330452468C899456B370E68DD4'
    outputcsv = '/home/pi/3d-rf-scanner/data/topography.csv'

    scan_surface(url, apikey, outputcsv)
