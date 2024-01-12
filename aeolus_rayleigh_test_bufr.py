import numpy as np
from scipy.stats import linregress, median_abs_deviation
import netCDF4 as nc
from netCDF4 import Dataset
import xarray as xr
import pandas as pd
from datetime import datetime, timezone
import os
import dask
import matplotlib.pyplot as plt
from base64 import b64decode
from matplotlib.collections import PolyCollection
import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as colors

from pymodules.LoggerModule import WrfLoggerClass
import eccodes

import traceback
import sys
from eccodes import *


INPUT = os.path.join("/home/stephen/BlackForestProjectData/dynamic/satellite/aeolus/bufr/ALD_B_N_2B","AE_OPER_ALD_B_N_2B_20151001T001124_20151001T014212_0001.BUFR")

VERBOSE = 1  # verbose error reporting


import pexpect
class AeolusDataClass(object):
        def __init__(self, bufr_file=None, logger=None):
                self.testfile = bufr_file
                self.logger = logger
                
        def _read_(self):
                """Metadata is read correctly from BufrMessage."""
                eccodes.codes_get
                with eccodes.BufrFile(self.testfile) as bufr_file:
                        msg = BufrMessage(bufr_file)
                        msg.unpack()
                        msg_keys = msg.keys()
                        self.assertEqual(len(msg_keys), 140)
                        for key in KNOWN_BUFR_KEYS:
                                assert key in msg_keys
                                # Size of message in bytes
                        self.assertEqual(msg.size(), 220)
                        self.assertEqual(len(msg.keys()), len(msg))
 
 
 
# Copyright 2005- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

#
# Python implementation: bufr_attributes
#
# Description: how to read attributes of keys in BUFR messages.
#
#



def example():
        # open bufr file
        f = open(INPUT, 'rb')

        keys = [
            'dataCategory',
            'dataSubCategory',
            'typicalDate',
            'bufrHeaderCentre',
            'bufrHeaderSubCentre',
            'masterTablesVersionNumber',
            'localTablesVersionNumber',
            'numberOfSubsets',
        ]
     
        cnt = 0
     
        # loop for the messages in the file
        while 1:
                # get handle for message
                bufr = codes_bufr_new_from_file(f)
                if bufr is None:
                        break
     
                print("message: %s" % cnt)
     
                # print the values for the selected keys from the message
                for key in keys:
                        try:
                                print('  %s: %s' % (key, codes_get(bufr, key)))
                        except CodesInternalError as err:
                                print('Error with key="%s" : %s' % (key, err.msg))
     
                cnt += 1
     
                # delete handle
                codes_release(bufr)
     
                # close the file
        f.close()       
def example_subset():
        # open BUFR file
        f = open(INPUT, 'rb')

        cnt = 0

        # loop for the messages in the file
        while 1:
                # get handle for message
                bufr = codes_bufr_new_from_file(f)
                if bufr is None:
                        break

                print("message: %s" % cnt)

                # we need to instruct ecCodes to expand all the descriptors
                # i.e. unpack the data values
                codes_set(bufr, 'unpack', 1)
                SatId = codes_get_array(bufr, "satelliteIdentifier")
                print ("Sat ID {}".format(SatId))
                # find out the number of subsets
                key = 'numberOfSubsets'
                numberOfSubsets = codes_get(bufr, 'numberOfSubsets')
                print(' %s: %d' % (key, numberOfSubsets))
                key = "receiverChannel"
                print(' %s: %d' % (key, codes_get_array(bufr, key)))

                lat = codes_get_array(bufr, "latitude")
                lon = codes_get_array(bufr, "longitude")
                elev = codes_get_array(bufr, "receiverChannel")
                #for i in range(numberOfSubsets):
                 #       print("%3d %.2f %.2f  " % (i + 1, lat[i], lon[i]))
                cnt += 1

                # delete handle
                codes_release(bufr)

        # close the file
        f.close()

        
def example_3():
        # open bufr file
        f = open(INPUT, 'rb')

        cnt = 0

        # loop for the messages in the file
        while 1:
                # get handle for message
                bufr = codes_bufr_new_from_file(f)
                if bufr is None:
                        break

                print("message: %s" % cnt)

                # we need to instruct ecCodes to expand all the descriptors
                # i.e. unpack the data values
                codes_set(bufr, 'unpack', 1)

                # ----------------------------------
                # get all the expanded data values
                # ----------------------------------
                key = 'numericValues'

                # get size
                num = codes_get_size(bufr, key)
                print('  size of %s is: %s' % (key, num))

                # get values
                values = codes_get_array(bufr, key)
                for i in range(len(values)):
                        print("   %d %.10e" % (i + 1, values[i]))

                cnt += 1
                break
        
                # delete handle
                codes_release(bufr)

        # close the file
        f.close()


def main():
        try:
                example_subset()
        except CodesInternalError as err:
                if VERBOSE:
                        traceback.print_exc(file=sys.stderr)
                else:
                        sys.stderr.write(err.msg + '\n')

                return 1


                     
if __name__ == '__main__':
        child = pexpect.spawn('date')
        # Read the child output without generating EOF
        child.expect(pexpect.EOF)
        # Store the text that is expected by the string pattern
        output = child.before
        today = output.decode("utf-8")
        # Print the output
        print("Today is : {}".format(today))
        mylogger = WrfLoggerClass()
        myLogger = mylogger._set_logger_ ()
        sys.exit(main())           
        pause=-1
