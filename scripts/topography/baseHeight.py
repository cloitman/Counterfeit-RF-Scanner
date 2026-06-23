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

#Remove scan outliers
def reject_outliers(data,m=2):
    return np.mean(data[abs(data-np.mean(data)) < m * np.std(data)])

# Scan the surface and capture topography data
def baseHeight(url, apikey, outputcsv):

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
    if (c.state()!='Operational'):
        print('[scan_surface] Debugging, exiting.')
        exit()

    # Initialize printer

    # We will be programming in milimeteres
    c.gcode("G21")

    # Coding in absolute coordinates
    c.gcode("G90")

    # Positioning will be rapid
    c.gcode("G0")

    # Home the printer/move to origin
    c.home()
    #c.gcode("G01 X0 Y0")
    #c.gcode("G01 Z0")

    sumHeight = 0
    x_min = 35
    x_max = 315
    x_step = 1
    y_min = 30
    y_max = 320
    y_step = 1

    # Move to initial coordinate for scanning
    initial_command = 'G01 X' + str((x_min+x_max)/2) + ' Y' + str((y_min+y_max)/2)
    c.gcode(initial_command)
    time.sleep(20.0)

    # define distance scanner repetitions here
    # 50 has been shown to be sufficient
    distance_rep = 50

    # Scan height at given location distance_rep times
    # to reduce measurement uncertainty
    # Count number of repetitions
    count = 0
    #Loop across measurments
    while (count < distance_rep):
        #Add new measurement to existing onces
        measurement = vl53.range
        sumHeight = sumHeight + measurement
        #Sleep one second before measuring again
        time.sleep(0.125)
        count = count + 1
    print(sumHeight/count)
    #Append z-height to coordinate array

    #Save data
    baseHeight = pd.DataFrame({'z':[sumHeight/count]})
    baseHeight.to_csv(outputcsv)

    # Finish function
    return

if __name__ == "__main__":
    url = 'http://172.29.34.38'
    apikey = '5615E7330452468C899456B370E68DD4'
    outputcsv = '/home/pi/3d-rf-scanner/data/baseHeight.csv'

    scan_surface(url, apikey, outputcsv)
