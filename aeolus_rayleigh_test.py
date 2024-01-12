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

import pexpect

class NcInterfaceClass(object):
    def __init__(self, ncfile=None, meta_product_file=None, logger=False):
        self.logger=logger
        self.ncfile=ncfile
        self._dimensions_()
        self.data = {}
    def _dimensions_(self, ):
        ncfile = Dataset(self.ncfile,'r')
        self.nc_group = list(ncfile.groups)
        for grp in self.nc_group:
            nc_variable_list = list(ncfile[grp].variables)
            nc_dimensions_list = list(ncfile[grp].dimensions)
            for key in nc_dimensions_list:
                self.logger.info("key {}".format(key))
                self.__dict__[key]=ncfile[grp].dimensions[key].size
                self.logger.info("size {}".format(ncfile[grp].dimensions[key].size))
        ncfile.close()


    def _read_(self, ):
        ncfile = Dataset(self.ncfile,'r')
        self.nc_group = list(ncfile.groups)
        data = {}
        for grp in self.nc_group:
            self.logger.info("grp {}".format(grp))
            nc_variable_list = list(ncfile[grp].variables)
            for key in nc_variable_list:
                self.logger.info("variable {}".format(key))
                data[key] = np.array(ncfile[grp].variables[key][:])       
        ncfile.close()
        return data

def reshape_to_profile(data, mtype="rayleigh"):
    """
    Input:   data      xarray.Dataset containing Aeolus L2B wind data.
                       It needs to contain the parameters wind_result_id and wind_profile_wind_result_id
             mtype     Measurement type (Rayleigh or Mie)

    Output:  data_2D   xarray.Dataset containing all variables from data resampled into 2D (profile vs. range-bin)
    """
    # get data shape of (new) 2D array
    data_shape = data[mtype + "_wind_profile_wind_result_id"].shape
    # get wind ids from 1D dataset
    wind_result_id = data[mtype + "_wind_result_id"].astype(np.int32)
    # get wind ids per profile and reshape to 1D
    new_wind_result_id = data[mtype + "_wind_profile_wind_result_id"].flatten()
    mask = new_wind_result_id == 0

    # increment all ambigious wind ids (necessary if multiple L2B files were concatenated by the request)
    while (np.diff(wind_result_id) < 0).sum() > 0:
        i = np.where(np.diff(wind_result_id) < 0)[0][0]
        increment = -np.diff(wind_result_id)[i] + 1
        ip = np.where(new_wind_result_id == wind_result_id[i])[0][0]
        wind_result_id[i + 1 :] += increment
        new_wind_result_id[ip + 1 :] += increment
    new_wind_result_id[mask] = 0

    # populate wind ids with incremented values and reindex all 1D DataArrays to 2D (still on 1D)
    data[mtype + "_wind_result_id"] = wind_result_id
    data_1D = (
        data.drop_dims(mtype + "_profile_data")
        .set_index({mtype + "_wind_data": "rayleigh_wind_result_id"})
        .reindex({mtype + "_wind_data": new_wind_result_id})
    )

    # reshape to 2D and reinclude all original 2D DataArrays
    midx = pd.MultiIndex.from_product(
        [range(1, data_shape[0] + 1), range(1, data_shape[1] + 1)],
        names=("rayleigh_profile_data", "array_24"),
    )
    data_1D[mtype + "_wind_data"] = midx
    data_2D = xr.merge(
        [data.drop_dims(mtype + "_wind_data"), data_1D.unstack(dim=mtype + "_wind_data")]
    )
    return data_2D
if __name__ == '__main__':
    """
    The transret file name  have a generic structure    
    given a date window, all transret files with granula start and end date will be read and put into a single file
    
    """    
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
    
    ncfile = os.path.join("/home/stephen/BlackForestProjectData/dynamic/satellite/aeolus/netcdf","L2B_rayleigh_wind_2019-11-15-2019-12-01.nc")
    ncdata = NcInterfaceClass(ncfile=ncfile, logger=myLogger)
    L2B_rayleigh=ncdata._read_()
    for iprof in np.linspace(0,9,10,dtype=int):
        print("{}".format(L2B_rayleigh["rayleigh_wind_profile_wind_result_id"][iprof,:]))
    nobs = L2B_rayleigh["rayleigh_wind_profile_wind_result_id"].shape[0]
    hlos_wind = np.zeros(L2B_rayleigh["rayleigh_wind_profile_wind_result_id"].shape)
    hlos_err = np.zeros(L2B_rayleigh["rayleigh_wind_profile_wind_result_id"].shape)
    hlos_alt = np.zeros(L2B_rayleigh["rayleigh_wind_profile_wind_result_id"].shape)
    for obsid in np.linspace(0,nobs-1,nobs, dtype=int):
        for vecin, key in enumerate(L2B_rayleigh["rayleigh_wind_profile_wind_result_id"][obsid,:]):
            if key > 0:
                hlos_wind[obsid,vecin]=L2B_rayleigh["rayleigh_wind_result_wind_velocity"][key]
                hlos_err[obsid,vecin]=L2B_rayleigh["rayleigh_wind_result_HLOS_error"][key]
                hlos_alt[obsid,vecin]=L2B_rayleigh["rayleigh_profile_alt_of_DEM_intersection"][key]
    
    pause=-1
