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
    time.sleep(10.0)

    #Define all array used to create topographic map and necessary values for looping
    z = np.array(0)
    xArr = []
    yArr = []
    xOld = 0
    yOld = 0
    zArr = []

    # x/y ranges here to be used for coordinates looped over for scanning
    # and then use them in the for loops
    # all x,y coordinates and step is in mm/10 (10^-4 m)?
    #range is x in [35,315] y in [30,3200] for Ender CR-10S
    y_min = 200#30
    y_max = 250#320
    y_step = 1
    x_min = 145#35
    x_max = 195#315
    x_step = 1

    # Move to initial coordinate for scanning
    initial_command = 'G01 X' +str(x_min) + ' Y' + str(y_min)
    c.gcode(initial_command)
    time.sleep(5.0)

    # define distance scanner repetitions here
    # 50 was found to be sufficient resolution
    distance_rep = 50

    #range is x in [30,310] y in [0,160]
    for i in range(y_min,y_max+1,y_step):
        #,310):
        for j in range(x_min,x_max+1,x_step):
            #60):
            #Now we add x, y, and z coordinates at each location of scan
	    #y-axis is the i-coordinates. There are fewer of these coordinates
	    #and it is easier for the motion of the printer to scan them first
            yArr.append(i) #Add y-coordinate to array

            sumHeight = 0

            # Scan height at given location distance_rep times
	    # to reduce measurement uncertainty
	    # Count number of repetitions
            count = 0
	    #Loop across measurments
            while (count < distance_rep):
		#Add new measurement to existing onces
                measurement = vl53.range
                sumHeight = sumHeight + measurement

		#Sleep before measuring again
                time.sleep(0.1)
		#Add number of repetitions to count to act as break statement
                count = count + 1
            print(sumHeight/count)
	    #Append z-height to coordinate array
            zArr.append(sumHeight/count)
            if (i%2==0):
                if (j!=x_max):
                    c.jog(x=1)
                #Add x-coordinate to array
                xArr.append(j)
                print('(' + str(j) + ',' + str(i) + ')')
            else:
                xArr.append(x_max-(j-x_min)-1)
                print('(' + str(x_max-(j-x_min)) + ',' + str(i) + ')')
                if (j!=x_max):
                    c.jog(x=-1)
            time.sleep(0.25)
        # Move y-axis one milimeter forward to scan new row
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
    outputcsv = '/home/pi/3d-rf-scanner/data/topographydata.csv'

    scan_surface(url, apikey, outputcsv)
