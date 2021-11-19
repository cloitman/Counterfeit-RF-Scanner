import os
import datetime
import argparse
import glob
import struct
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from calc_utilities import *
import re
from heatmap import *
from pylab import *

fontaxes = {
    'family': 'Arial',
        'color':  'black',
        #'weight': 'bold',
        'size': 8,
}
fontaxes_title = {
    'family': 'Arial',
        'color':  'black',
        'weight': 'bold',
        'size': 9,
}

def extractData (FileName):
    with open (FileName, "r") as file:
        lines = file.readlines()
    data = []
    for line in lines:
        if ("slot" not in line):
            #print re.split('/\(', line)
            #print line.split('\t')
            line_dat = []
            for n in line.split('\t'):
                seq_num = n.split()[0]
                if (seq_num != '-1'):
                    line_dat.append(int(seq_num))
                else:
                    break
            if (len(line_dat) >0):
                data.append(line_dat)
    print data, len(data)
    # for i in range(len(data)):
    #     plus = data[i][0]/8*100
    #     for j in range(8):
    #         data[i][j] = data[i][j] + plus
    transmit_data=[]
    for i in range(11):
        transmit_data.append(data[i])
    data = transmit_data
    print data, len(data)
    return data, len(data), 8


def plot_bitmap_16x (FileName):
    slots = ["slot-0", "slot-1", "slot-2", "slot-3", "slot-4", "slot-5", "slot-6", "slot-7"]
    #instanceNum = ["InstanceNum-0", "InstanceNum-1", "InstanceNum-2", "InstanceNum-3", "InstanceNum-4", "InstanceNum-5", "InstanceNum-6", "InstanceNum-7", "InstanceNum-8", "InstanceNum-9", "InstanceNum-10", "InstanceNum-11", "InstanceNum-12", "InstanceNum-13", "InstanceNum-14", "InstanceNum-15", "InstanceNum-16", "InstanceNum-17", "InstanceNum-18", "InstanceNum-19", "InstanceNum-20"]
    instanceNum = ["INST-0","INST-0", "INST-5", "INST-10",  "INST-15", "INST-20"]
    data, length, width = extractData(FileName)
    fig, ax = plt.subplots(figsize=(3.5,3.5), dpi=300, facecolor='w')
    data = np.asarray(data)
    data = np.transpose(data)
    print np.shape(data), np.max(data)+1
    cmap = cm.get_cmap('rainbow', np.max(data)+1)    # discrete colors
    im, cbar = heatmap(data,row_labels=slots, col_labels=instanceNum, cmap=cmap, aspect=2, cbarlabel="FPGA IDs")
    #im, cbar = heatmap_tr(data,row_labels=instanceNum, col_labels=slots, cmap='rainbow', aspect=0.5, cbarlabel="FPGA IDs")
    annotate_heatmap(im)

    #plt.xlabel("Different f1.16xlarge Instances",fontdict = fontaxes)
    #plt.ylabel("8 FPGAs on One Instance",fontdict = fontaxes)
    plt.savefig("bitmap_16x.png", bbox_inches='tight')



def plot_bitmap_16x_tr (FileName):
    slots = ["slot-0", "slot-1", "slot-2", "slot-3", "slot-4", "slot-5", "slot-6", "slot-7"]
    #instanceNum = ["InstanceNum-0", "InstanceNum-1", "InstanceNum-2", "InstanceNum-3", "InstanceNum-4", "InstanceNum-5", "InstanceNum-6", "InstanceNum-7", "InstanceNum-8", "InstanceNum-9", "InstanceNum-10", "InstanceNum-11", "InstanceNum-12", "InstanceNum-13", "InstanceNum-14", "InstanceNum-15", "InstanceNum-16", "InstanceNum-17", "InstanceNum-18", "InstanceNum-19", "InstanceNum-20"]
    instanceNum = ["INST-0","INST-0", "INST-5", "INST-10",  "INST-15", "INST-20"]
    data, length, width = extractData(FileName)
    fig, ax = plt.subplots(figsize=(3,3), dpi=300, facecolor='w')
    data = np.asarray(data)
    #data = np.transpose(data)
    print np.shape(data)
    cmap = cm.get_cmap('rainbow', np.max(data)+1)    # discrete colors
    #im, cbar = heatmap(data,row_labels=slots, col_labels=instanceNum, cmap='rainbow', aspect=2, cbarlabel="FPGA IDs")
    im, cbar = heatmap_tr(data,row_labels=instanceNum, col_labels=slots, cmap=cmap, aspect=0.5, cbarlabel="FPGA IDs")
    annotate_heatmap(im)

    #plt.xlabel("Different f1.16xlarge Instances",fontdict = fontaxes)
    #plt.ylabel("8 FPGAs on One Instance",fontdict = fontaxes)
    plt.savefig("bitmap_16x.png", bbox_inches='tight')

if __name__ == '__main__':
    #Use ../binaryRawData/n_virginia_us-east-1/sequence_spot_4xlarge_20190905/i-0d7ef696b690b7171_2019-09-05_06-12_3.84.91.243_slot1_DRAMPUFonSpotInstance_f1.4xlarge/120s_2019-09-05_06-12/D_2019-09-05_06-14.dat
    parser = argparse.ArgumentParser(description="python plot_bitmap_16xlarge.py -d ../result_20190906/identify16xlargeFPGAs-analyze_16x_sequence_20190902_2019-09-03_20-24_DRAM4.txt", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", "--dir", required=True, type=str, help='Path to the result file, eg: 16xlarge result file')
    args = parser.parse_args()
    

    plot_bitmap_16x_tr(args.dir)


