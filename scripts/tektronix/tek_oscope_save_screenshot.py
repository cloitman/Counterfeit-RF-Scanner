#
# Write script to capture screenshot here.  Use TekMDO3104 class from tek_oscope.py
#

from tek_oscope import TekMDO3104
import sys
import time

if __name__ == '__main__':

    # Check that file name and path is provided
    if sys.argv[1] == None:
        print("Please specify the path where the image should be saved")
        sys.exit(1)

    # Connect to the scope
    mdo = TekMDO3104(instr='USB0::1689::1032::C013559::0::INSTR')

    # Small delay to let connection happen
    time.sleep (1)

    # Save screenshot
    # temp_path = "C:/Temp.png"
    temp_path = "temp.png"
    local_path = sys.argv[1]
    mdo.save_image(temp_path, local_path)

