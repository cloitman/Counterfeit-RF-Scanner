#!/usr/bin/env python3

""" This is a script for capturing radiation data using the oscilloscope sensor on 3D printer chasis. """

__author__ = "Charlie Loitman"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

from octorest import OctoRest
import time
import board
import busio
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
def scan_surface(url, apikey, inputcsv, outputcsv):

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

    #Read in coordinates from topography data
    topography = pd.read_csv(inputcsv)
    #Position senser 4 mm above board at all points
    topography.loc['z'] = topography.loc['z'] - topography['z'].iloc[0].squeeze() + 4 
    #create column for new scans
    topography['em'] = 0

    # x/y ranges here to be used for coordinates looped over for scanning
    # and then use them in the for loops
    # all x,y coordinates and step is in mm/10 (10^-4 m)?
    #range is x in [30,310] y in [0,160] for Ender CR-10S
    y_min = 0
    y_max = 160
    y_step = 1
    x_min = 30
    x_max = 310
    x_step = 1

    # Move to initial coordinate for scanning
    initial_command = 'G01 X' +str(x_min-1) + ' Y' + str(y_min)
    c.gcode(initial_command)
    time.sleep(10.0)

    # FIXME define scanner repetitions here
    scanner_rep = 100

    #Define old coordinates so no how for to move relative to old coordinates
    oldX = x_min
    oldY = y_min
    oldZ = 0

    #Loop across coordinates
    for index, row in topography.iterrows():
        #Move to desired coordinates. Move z-axis first so don't bump into anything
        c.jog(z=5)
        c.jog(x=row['x'].squeeze()-oldX,y=row['y'].squeeze()-oldY)
        c.jog(z=row['z'].squeeze()-oldZ-5)
        sumScan = 0
        # Scan height at given location distance_rep times
        # to reduce measurement uncertainty
        # Count number of repetitions
        count = 0
        #Loop across measurments
        while (count < sensor_rep):
            #Add new measurement to existing onces
            sumScan = sumScan + vl53.range
	    #Sleep one quarter second before measuring again
            time.sleep(0.25)
            #Add number of repetitions to count to act as break statement
            count = count + 1
        print(sumScan/count)
        topography['rf'].iloc[index] = sumScan/count

    # Return print head to home position and save data
    c.home()
    topography.to_csv(outputcsv)

    # Finish function
    return

if __name__ == "__main__":
    url = 'http://172.29.34.38'
    apikey = '5615E7330452468C899456B370E68DD4'
    inputcsv = '/home/pi/3d-rf-scanner/data/topographydata.csv'
    outputcsv = '/home/pi/3d-rf-scanner/data/rfdata.csv'
    scan_surface(url, apikey, inputcsv, outputcsv)
