import os
import numpy as np
import pandas as pd
#!/usr/bin/env python3

""" This is a script for plotting topography and rf data in a heatmap. """

__author__ = "Charlie Loitman"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

import importlib
importlib.import_module('mpl_toolkits').__path__
import matplotlib.pyplot as plt
import seaborn as sns


def plot_rf(inputcsv,outputplotfile):
    data = pd.read_csv(inputcsv)[['x','y','rf']]
    fig = plt.figure()
    sns.heatmap(data.pivot_table(index='y', columns='x', values='rf'), cbar_kws={'label': 'RF measurement Intensity'},square=True)
    plt.xlabel('x-coordinate (mm)')
    plt.ylabel('y-coordinate (mm)')
    plt.title('Topographic map of part')
    plt.savefig(outputplotfile)
    return

if __name__ == "__main__":
    inputcsv = '/home/pi/3d-rf-scanner/data/rfdata.csv'
    outputplotfile= '/home/pi/3d-rf-scanner/figures/rfplot.png'
    plot_rf(inputcsv, outputplotfile)
