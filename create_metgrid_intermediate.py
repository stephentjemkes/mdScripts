import numpy
import os
import pywinter.winter as pyw
from netCDF4 import Dataset
import argparse

data_path = "."

parser = argparse.ArgumentParser(description="My parser")
parser.add_argument("-a", "--atmosphere", default=None)
parser.add_argument("-d", "--date")
args = parser.parse_args()

ec_atmos_data = Dataset(os.path.join(data_path, args.atmosphere), 'r')
print("{}".format(list(ec_atmos_data.variables)))
print("{}".format(numpy.shape(ec_atmos_data.variables['t'])))

lat = ec_atmos_data.variables['latitude'][:] # degrees north
lon = ec_atmos_data.variables['longitude'][:] # degrees east
dlat = numpy.abs(lat[1] - lat[0])
dlon = numpy.abs(lon[1] - lon[0])
nlats = 400
# create winter Geo-information for cylindrical equidistant projection
winter_geo = pyw.Geo4(lat[0],lon[0],nlats, dlon, False)

winter_u = pyw.V3d('UU',ec_atmos_data.variables['u'][0,::-1,:,:])
winter_v = pyw.V3d('VV',ec_atmos_data.variables['v'][0,::-1,:,:])
winter_t = pyw.V3d('TT',ec_atmos_data.variables['t'][0,::-1,:,:])
winter_q = pyw.V3d('SPECHUMD',ec_atmos_data.variables['q'][0,::-1,:,:])
print ("Shape info u {}".format(ec_atmos_data.variables['u'].shape))
print ("Shape info v {}".format(ec_atmos_data.variables['v'].shape))
print ("Shape info t {}".format(ec_atmos_data.variables['t'].shape))
print ("Shape info q {}".format(ec_atmos_data.variables['q'].shape))

total_fields = [winter_t,
                winter_q,
                winter_u,
                winter_v]

# Write intermediate file
pyw.cinter('FILE_ML', args.date, winter_geo, total_fields, data_path)




