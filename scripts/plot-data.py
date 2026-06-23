#!/usr/bin/env python3

""" This is a script for plotting RF or topogrpahy data. """

__author__ = "Charlie Loitman"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

import argparse
import sys
import os
# Get path of the script, so the other sripts can be located
script_with_path = os.path.realpath(__file__)
script_path = os.path.dirname(script_with_path)
sys.path.append(os.path.join(script_path,'topography'))

# Import custom scripts
from surfaceplot import plot_topography

script_path_2 = os.path.dirname(script_with_path)
sys.path.append(os.path.join(script_path_2,'oscilloscope'))

from rfplot import plot_rf


# Main script
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='This is main script for plotting RF or topography data.') 
    parser.add_argument("-r", "--rf", action='store_true', help='Plot RF data.')
    parser.add_argument("-t", "--topography", action='store_true', help='Plot topography data.')
    parser.add_argument('-p', '--outputplotfile', default=None, type=str, required=True, help='File name with path of the output plot.')
    parser.add_argument('-i', '--inputcsvfile', default=None, type=str, required=True, help='File name with path of the input CSV file.')

    args = parser.parse_args()

    # Check arguments
    if( args.rf == False and args.topography == False ):
        print('Please specify -r/--rf or -t/--topography option.')
        sys.exit(1)

    # If RF scanner option is selected, make RF plot
    if( args.rf == True ):
        print('Make rf plot here.')
        plot_rf(args.inputcsvfile,args.outputplotfile)

    # If topography scanner option is select, make topography plot
    elif( args.topography == True ):
        print(' make topography plot here.')
        plot_topography(args.inputcsvfile,args.outputplotfile)

    # Some unexpected set of options has occured
    else:
        print('Unexpected options received, exiting')
        sys.exit(1)

