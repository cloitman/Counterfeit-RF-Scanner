#!/usr/bin/env python3

""" This is main script for running 3D RF scanner and 3D topography scanner. """

__author__ = "Jakub Szefer"
__copyright__ = "Copyright 2021"
__license__ = "GPLv3"

import argparse
import json
import os
import sys
from octorest import OctoRest

# Get path of the script, so the other sripts can be located
script_with_path = os.path.realpath(__file__)
script_path = os.path.dirname(script_with_path)
sys.path.append(os.path.join(script_path,'topography'))

# Import custom scripts
from topography import scan_surface

# Main script
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='This is main script for running 3D RF scanner and topography scanner.') 
    parser.add_argument('-j', '--json', default=None, type=str, required=True, help='JSON settings file with url and apikey for OctoPI')
    parser.add_argument("-r", "--rf", action='store_true', help='Run the scanner in RF mode')
    parser.add_argument("-t", "--topography", action='store_true', help='Run the scanner in topography mode')
    parser.add_argument('-o', '--outputcsvfile', default=None, type=str, required=False, help='File name with path of the output CSV file.')
    parser.add_argument('-i', '--inputcsvfile', default=None, type=str, required=False, help='File name with path of the input CSV file.')

    args = parser.parse_args()

    # Check arguments
    if( args.rf == False and args.topography == False ):
        print('Please specify -r/--rf or -t/--topography option.')
        sys.exit(1)

    if( args.rf == True and args.topography == True ):
        print('Cannot specify both -r/--rf and -t/--topography options as the same time.')
        sys.exit(1)

    if( args.topography == True and args.outputcsvfile == None ):
        print('Need to specify file name and path of the output CSV file.')
        sys.exit(1)

    if( args.rf == True and ( args.outputcsvfile == None or args.inputcsvfile == None) ):
        print('Need to specify file name and path of both the output and input CSV files.')
        sys.exit(1)

    # Read url and apikey from settings.json file provided by user
    with open(args.json, "r") as read_file:
        data = json.load(read_file)

    url    = data['url']
    apikey = data['apikey']

    # If RF scanner option is selected, call appropriate script
    if( args.rf == True ):
        print('FIXME call rf scanner script')
        # FIXME real function name to be specified
        # scan_rf(url, apikey, args.inputcsvfile, args.outputcsvfile)

    # If topography scanner option is select, call appropriate script 
    elif( args.topography == True ):
        print('Calling topography scanner script')
        scan_surface(url, apikey, args.outputcsvfile)

    # Some unexpected set of options has occured
    else:
        print('Unexpected options received, exiting')
        sys.exit(1)

