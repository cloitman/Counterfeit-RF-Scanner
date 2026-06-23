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
import csv
import math
import time
import pyvisa as visa

def b2s(enable):
    return 'ON' if enable else 'OFF'

class MDO3054(object):
    def __init__(self, timeout=10):
        self.rm = visa.ResourceManager()
        res = self.rm.list_resources()[0]
        self.inst = self.rm.open_resource(res)
        self.inst.timeout = timeout*1000 # seconds to milliseconds

    def __del__(self):
        self.inst.close()

    def _read(self, cmd, converter='f'):
        return self.inst.query_ascii_values(cmd, converter=converter)

    def _write(self, cmd):
        self.inst.write(cmd)

    def turn_rf_on(self, enable=True):
        self.select_rf(enable)
        self.turn_spectrogram_on(enable)
        self.set_marker_enable(enable)

    def select_rf(self, enable=True):
        self._write('SELect:RF_NORMal %s' % b2s(enable))

    def turn_spectrogram_on(self, enable=True):
        self._write('RF:SPECTRogram:STATE %s' % b2s(enable))

    def select_channel(self, ch, enable=True):
        self._write('SELect:CH%d %s' % (ch, b2s(enable)))

    def turn_afg_on(self, enable=True):
        self._write('AFG:OUTPut:LOAd:IMPEDance FIFty')
        self._write('AFG:OUTPut:STATE %s' % b2s(enable))

    def set_frequency(self, freq):
        self._write('RF:FREQuency %e' % freq)

    def set_span(self, freq):
        self._write('RF:SPAN %e' % freq)

    def set_marker(self, freq, id=1):
        self._write('MARKER:M%d:FREQuency:ABSolute %e' % (id, freq))

    def get_marker_amp(self, id=1):
        return self._read('MARKER:M%d:AMPLitude:ABSolute?' % id)[0]

    def set_marker_enable(self, enable):
        self._write('MARKER:MANUAL %s' % b2s(enable))

    def reset(self):
        self._write('*RST')
        self.select_channel(1, False)
        # self._read("*OPC?")

    def save_image(self, temp_path, local_path=None):
        self._write("SAVe:IMAGe:FILEFormat PNG")
        self._write("SAVe:IMAGe \"%s\"" % temp_path)
        self._read("*OPC?")
        self.copy_file(temp_path, local_path)

    def copy_file(self, remote_path, local_path=None, delete=True):
        self._write("FILESystem:READFile \"%s\"" % remote_path)
        # timeout = self.inst.timeout
        # self.inst.timeout = 60000 # 1 minute
        data = self.inst.read_raw()
        # self.inst.timeout = timeout
        if not local_path:
            local_path = remote_path
        with open(local_path, 'wb') as f:
            f.write(data)
        if delete:
            self._write("FILESystem:DELEte \"%s\"" % remote_path)


    def get_rf_data(self, n=1, points=10000, binary=True):
        time.sleep(1)
        self._write('DATa:SOUrce RF_NORMal')
        time.sleep(1)
        # print(self._read('DATA:SOurce?', 's'))
        # self._write('DATa:STARt 1')
        # self._write('DATa:STOP %d' % points)
        enc = 'BINary' if binary else 'ASCii'
        self._write('WFMOutpre:ENCdg %s' % (enc))
        self._write('WFMOutpre:BYT_Nr 4')
        self._write('HEADer 0')
        xinc = self._read('WFMOutpre:XINcr?')[0]
        xstart = self._read('WFMOutpre:XZEro?')[0]
        points = int(self._read('WFMOutpre:NR_Pt?')[0])
        freqs = [xstart + xinc*i for i in range(points)]
        ymult = self._read('WFMOutpre:YMUlt?')[0]
        curves = [0]*n
        tstart = time.time()
        for i in range(n):
            if binary:
                curves[i] = self.inst.query_binary_values('CURVE?', datatype='f', is_big_endian=True)
            else:
                curves[i] = self._read('CURVE?')
        tend = time.time()
        print ("RF RAW", enc, tend-tstart)
        self._write('WFMOutpre:ENCdg ASCii')
        for i in range(n):
            curves[i] = [30 + 10*math.log10(ymult*c) for c in curves[i]]
        return (freqs, curves)
        return list(zip(freqs, curve))

    def get_rf_data_max(self, n=1, points=10000, binary=True):
        time.sleep(1)
        self._write('DATa:SOUrce RF_NORMal')
        time.sleep(1)
        # print(self._read('DATA:SOurce?', 's'))
        # self._write('DATa:STARt 1')
        # self._write('DATa:STOP %d' % points)
        enc = 'BINary' if binary else 'ASCii'
        self._write('WFMOutpre:ENCdg %s' % (enc))
        self._write('WFMOutpre:BYT_Nr 4')
        self._write('HEADer 0')
        xinc = self._read('WFMOutpre:XINcr?')[0]
        xstart = self._read('WFMOutpre:XZEro?')[0]
        points = int(self._read('WFMOutpre:NR_Pt?')[0])
        freqs = [xstart + xinc*i for i in range(points)]
        ymult = self._read('WFMOutpre:YMUlt?')[0]
        curves = [0]*n
        tstart = time.time()
        for i in range(n):
            if binary:
                curves[i] = self.inst.query_binary_values('CURVE?', datatype='f', is_big_endian=True)
            else:
                curves[i] = self._read('CURVE?')
        tend = time.time()
        print ("RF RAW", enc, tend-tstart)
        self._write('WFMOutpre:ENCdg ASCii')
        for i in range(n):
            curves[i] = [30 + 10*math.log10(ymult*c) for c in curves[i]]
        return max(curves[0])
        #return list(zip(freqs, curve))

    def set_afg_ampl(self, volt): # peak to peak
        self._write('AFG:AMPLitude %.3f' % volt)

    def set_afg_freq(self, freq):
        self._write('AFG:FREQuency %.1f' % freq)

    def set_afg_offset(self, dc):
        self._write('AFG:OFFSet %.2f' % dc)

    def set_afg_func(self, func):
        # {SINE|SQUare|PULSe|RAMP|NOISe|DC|SINC|GAUSsian|LORENtz|ERISe|EDECAy|HAVERSINe|CARDIac|ARBitrary}
        self._write('AFG:FUNCtion %s' % func)

    def set_afg_phase(self, phase):
        self._write('AFG:PHASe %.1f' % phase)

    def set_analog_horizontal_scale(self, seconds):
        # self._write('WFMInpre:XINcr %e' % seconds)
        self._write('HORizontal:SCAle %e' % seconds)

    def set_analog_vertical_scale(self, ch, volts):
        self._write('CH%d:SCAle %e' % (ch, volts))

    def get_analog_data(self, ch=1, points=10000, binary=True):
        self._write('DATa:SOUrce CH%d' % ch)
        self._write('DATa:START 1')
        self._write('DATa:STOP %d' % points)
        # self._write('WFMInpre:DOMain TIMe')
        enc = 'BINary' if binary else 'ASCii'
        self._write('WFMOutpre:ENCdg %s' % enc)
        self._write('WFMOutpre:BYT_Nr 1')
        self._write('HEADer 0')
        xinc = self._read('WFMOutpre:XINcr?')[0]
        xstart = self._read('WFMOutpre:XZEro?')[0]
        times = [xstart + xinc*i for i in range(points)]
        ymult = self._read('WFMOutpre:YMUlt?')[0]
        ystart = self._read('WFMOutpre:YZEro?')[0]
        self._write('ACQuire:STATE STOP')
        tstart = time.time()
        if binary:
            curve = self.inst.query_binary_values('CURVE?', datatype='b', is_big_endian=True)
        else:
            curve = self._read('CURVE?')
        tend = time.time()
        print('CH RAW', enc, tend-tstart)
        self._write('ACQuire:STATE RUN')
        self._write('WFMOutpre:ENCdg ASCii')
        curve = [ystart + ymult*c for c in curve]
        return (times, [curve])

    def save_to_csv(self, temp_path, local_path=None):
        self._write('SAVe:WAVEform:FILEFormat SPREADSheet')
        self._write('SAVE:WAVEFORM ALL,"%s"' % temp_path)
        self._read("*OPC?")
        self.copy_file(temp_path, local_path)

    def save_multiple(self, basename, n, local_dir='.', spreadsheet=True):
        if spreadsheet:
            formatting = 'SPREADSheet'
            ext = 'csv'
        else:
            formatting = 'INTERNal'
            ext = 'isf'
        self._write('SAVe:WAVEform:FILEFormat %s' % formatting)
        tstart = time.time()
        for i in range(n):
            self._write('SAVE:WAVEFORM ALL,"%s_%d.%s"' % (basename, i, ext))
            self._read("*OPC?")
        tend = time.time()
        print (ext, tend-tstart)
        for i in range(n):
            local_fname = "%s_%d.%s" % (basename, i, ext)
            if spreadsheet:
                remote_fname = local_fname
            else:
                remote_fname = "%s_%d.isf_RF_NORMal.%s" % (basename, i, ext)

            self.copy_file(remote_fname, "%s/%s" % (local_dir, local_fname))


def write_file(outfile, data):
    header, rows = data
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

# Create client for connections to OctoRest server
def make_octorest_client(url, apikey):
    try:
        client = OctoRest(url=url, apikey=apikey)
        return client
    except Exception as e:
        print(e)
        return

# Scan the surface and capture topography data
def scan_rf(url, apikey, inputcsv, outputcsv,baseHeightcsv):

    # Setup oscilloscope

    mdo = MDO3054()

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
    time.sleep(3.0)
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
    time.sleep(10.0)

    #Read in coordinates from topography data
    topography = pd.read_csv(inputcsv)

    #Position senser 4 mm above board at all points
    topography['zNew'] = pd.read_csv(baseHeightcsv)['z'].loc[0].squeeze() - topography['z'] + 4 
    topography = topography[['x','y','zNew']].rename(columns={'zNew':'z'})
     #create column for new scans
    topography['em'] = 0

    # x/y ranges here to be used for coordinates looped over for scanning
    # and then use them in the for loops
    # all x,y coordinates and step is in mm/10 (10^-4 m)?
    #range is x in [35,315] y in [30,320] for Ender CR-10S
    y_min = np.min(topography['y'])#30
    y_max = np.max(topography['y'])#320
    y_step = 1
    x_min = np.min(topography['x'])#35
    x_max = np.max(topography['x'])#315
    x_step = 1

    # Move to initial coordinate for scanning
    c.gcode('G01 Z50')
    initial_command = 'G01 X' +str(x_min-1) + ' Y' + str(y_min-1)
    c.gcode(initial_command)
    time.sleep(5.0)

    # Prepare oscilloscope settings
#    mdo.turn_rf_on()
#    time.sleep(10.0)
#    mdo.set_frequency(50e6)
#    mdo.set_span(100e6)

    # define scanner repetitions here
    nseries = 100

    #Define old coordinates so no how for to move relative to old coordinates
    oldX = x_min-1
    oldY = y_min-1
    oldZ = 0

    # Define how much to raise z before moving in x- and y-planes
    z_clearance = 20

    #Loop across coordinates
    for index, row in topography.iterrows():
        #Move to desired coordinates. Move z-axis first so don't bump into anything
        c.jog(z=z_clearance)
        c.jog(x=int(row['x'].squeeze()-oldX),y=int(row['y'].squeeze()-oldY))
        c.jog(z=int(row['z'].squeeze()-oldZ-z_clearance))

        # Scan height at given location distance_rep times
        # to reduce measurement uncertainty

        # Have cumulative sum of all measurements
        rf = 0

        #Loop across measurments
        rf = mdo.get_rf_data_max(nseries)
        #Sleep before measuring again
        time.sleep(10.0)
        print(rf)

        xOld = row['x'].squeeze()
        yOld = row['y'].squeeze()
        zOld = row['z'].squeeze()

        #Add measured value to data frame
        topography['rf'].iloc[index] = rf


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
    baseHeightcsv = '/home/pi/3d-rf-scanner/data/baseHeight.csv'
    scan_rf(url, apikey, inputcsv, outputcsv,baseHeightcsv)
