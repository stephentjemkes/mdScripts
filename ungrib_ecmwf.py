import os
import datetime
from maatdafpy.UngribEcmwfModule import UngribEcmwfClass
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

default_maat_daf_top = os.path.join(os.environ["HOME"], "maatdaf")
default_maat_daf_source = os.path.join(default_maat_daf_top, "Source")
default_maat_daf_support = os.path.join(default_maat_daf_top, "Support")
default_maat_daf_data = os.path.join(default_maat_daf_top, "Data")
default_maat_daf_user = os.path.join(default_maat_daf_top, "User")
default_maat_daf_system = os.path.join(default_maat_daf_top, "System")

verbosity_levels = ['debug', 'info', 'warning', None]

parser = argparse.ArgumentParser(description="method to retrieve ecmwf data for wrf",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-c',
                    action="count",
                    default=0,
                    help='Cleans the directory after an assimilation cycle and results are stored in the diagnostic partition,'
                         'the level of cleaning depends on the number of "c", -c replace geogrid -cc replace ungrib -ccc replace ungrib and geogrid')
#
# the hardware configuration

# the hardware configuration
parser.add_argument("--hardware_configuration_path",
                    default=default_maat_daf_system,
                    help="Where the target hardware configuration file can be found")
parser.add_argument("--hardware",
                    default=default_hardware_configuration_file,
                    help="The hardware configuration file")
#
# The application configuration data
parser.add_argument("--api_configuration", help="The application configuration file",
                    default=None)
parser.add_argument("--api_configuration_path", help="The application configuration file",
                    default=None)
# the basic directory structure
parser.add_argument("--MaatDafSource", help="The absolution path for maat daf source partition",
                    default=default_maat_daf_source)

parser.add_argument("--MaatDafData", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_data)

parser.add_argument("--MaatDafSupport", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_support)
#
# final verbosity
parser.add_argument('--verbosity', choices=verbosity_levels,
                    default='debug',
                    help='The level of verbosity of the software')


if __name__ == "__main__":
    initial_condition_case = 'deterministic'
    project = UngribEcmwfClass(parser=parser)
    # define the logger
    project.__init_topography_geogrid__()
    # we do a wrfda processing
    project.__init_topography_ungrib__()

    experimental_period_start = datetime.datetime.strptime(
        project.configuration["api"]["domains"]["temporal"]["start"], "%Y%m%d%H"
    )
    experimental_period_end = datetime.datetime.strptime(
        project.configuration["api"]["domains"]["temporal"]["end"], "%Y%m%d%H"
    )
    # we need to consider that we have multiple initial conditions, which are
    # generated from ecmwf same valid time, but with different basetime and forecast step
    # options for the initial conditions are ensemble forecast or multiple deterministic
    # for the ensemble forecast the search parth is different and also there is only
    # one basetime-step-validity time
    # for the deterministic forecast this is different
    project.__geogrid__()
    if initial_condition_case == "deterministic":
        project.__transcribe_available_oper_files__(max_step_value=12)
        pass
    else:
        project.__transcribe_available_oper_files__(max_step_value=48)
        #  decode the initial conditions
        project.__transcribe_available_elda_files__()
    pause = -1

