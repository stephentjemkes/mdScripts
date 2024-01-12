import os
import datetime
from MaatDafpy.Wps4GdasModule import Wps4GdasClass
# from pymodules.WrfProcessConfigurationClass import WrfProcessConfigurationClass
import argparse
import socket
import json

if "inspiron" in socket.gethostname().lower():
    system = "dell"
    default_hardware_configuration_file = "dell_inspiron.json"
elif "precision" in socket.gethostname().lower():
    system = "dell"
    default_hardware_configuration_file = "dell_precision.json"
    use_slurm = False
elif "srv-w4repp" in socket.gethostname().lower():
    system = "unknown"
    default_hardware_configuration_file = "hermess.json"
    use_slurm = True
elif "lex-saturn" in socket.gethostname().lower():
    system = "unknown"
    default_hardware_configuration_file = "saturn.json"
    use_slurm = False
else:
    system = "docker"
    default_hardware_configuration_file = "docker.json"
    use_slurm = False

# default settings

default_maat_daf_source = os.path.join(os.environ["HOME"],"MaatDafSource")
default_maat_daf_support = os.path.join(os.environ["HOME"],"MaatDafSupport")
if system == "docker":
    default_hardware_configuration_path = os.path.join(os.environ["HOME"], "configuration","system")
else:
    default_hardware_configuration_path = os.path.join(os.environ["HOME"],"MaatDafSource",
                                                       "docker", "MaatDafApp", "configuration","system")
default_maat_daf_data = os.path.join(os.environ["HOME"],"MaatDafData")

verbosity_levels = ['debug', 'info', 'warning', None]

parser = argparse.ArgumentParser(description="method to convert bufr2 gdas data for wrf",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-c',
                    action="count",
                    default=0,
                    help='Cleans the directory after an assimilation cycle and results are stored in the diagnostic partition,'
                         'the level of cleaning depends on the number of "c", -c replace geogrid -cc replace ungrib -ccc replace ungrib and geogrid')


parser.add_argument("--MaatDafSource", help="The absolution path for maat daf source partition",
                    default=default_maat_daf_source)

parser.add_argument("--MaatDafData", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_data)

parser.add_argument("--MaatDafSupport", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_support)
parser.add_argument("--wrf_configuration",
                    default="wrf",
                    help="The wrf configuration file")
parser.add_argument("--project", help="The project name", default="GdasWfre")
parser.add_argument("--case", help="The case name", default="Aug19")
parser.add_argument("--experiment", help="The experiment name", default="grib2netcdf_gdas")
# with the above variables, the configuration files can be loaded

parser.add_argument("--hardware_configuration_path",
                    default=default_hardware_configuration_path,
                    help="Where the target hardware configuration file can be found")

parser.add_argument("--hardware",
                    default=default_hardware_configuration_file,
                    help="The hardware configuration file")

parser.add_argument('--verbosity', choices=verbosity_levels,
                    default='debug',
                    help='The level of verbosity of the software')


if __name__ == "__main__":

    project = Wps4GdasClass(parser=parser)
    # define the logger
    project.__init_topography_geogrid__()
    # define topography for ungrib and metgrid
    project.__init_topography_ungrib__()
    #

    experimental_period_start = datetime.datetime.strptime(
        project.configuration["api"]["domains"]["temporal"]["start"], "%Y%m%d%H"
    )
    experimental_period_end = datetime.datetime.strptime(
        project.configuration["api"]["domains"]["temporal"]["end"], "%Y%m%d%H"
    )

    # as the geogrid is static for the entire project this can be generated once
    project.__geogrid__()
    #
    # do we have grib2files
    #
    project.__scan_available_grib2_files__()

    # we need to consider that we have multiple initial conditions, which are
    # generated for same valid time, but with different basetime and forecast step
    # maximum is a 6 hour forecast

    # hence lets convert first for the initial condition


    current_day = experimental_period_start - datetime.timedelta(hours=6)
    project.__determine_available_ic_files__(experimental_period_start)
    current_day = experimental_period_start
    lateral_boundary_conditions = [current_day]
    while True:
        if current_day > experimental_period_end:
            break
        current_day += datetime.timedelta(hours=3)
        lateral_boundary_conditions.append(current_day)

    project.__determine_available_lbc_files__(lateral_boundary_conditions)

    for fc_time in project.currently_available_lbc_files:

        [root, grib2_file, base_time, step] = project.currently_available_lbc_files[fc_time]
        project.__grib2netcdf__(source_directory=root,
                                grib2_file=grib2_file,
                                base_time=base_time,
                                step=step)

    for fc_time in project.currently_available_ic_files:
        for x in project.currently_available_ic_files[fc_time]:
            [root, grib2_file, base_time, step] = x
            project.__grib2netcdf__(source_directory=root,
                                    grib2_file=grib2_file,
                                    base_time=base_time,
                                    step=step)

    project.__clean_topography__()
