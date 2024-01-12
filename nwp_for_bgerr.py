import os
import datetime
from maatdafpy.NwpForWrfModule import NwpForWrfClass
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
else:
    system = "docker"
    default_hardware_configuration_file = "docker.json"
    use_slurm = False

# default settings
maat_dat_top = os.path.join(os.environ["HOME"],"maatdaf")
default_maat_daf_source = os.path.join(maat_dat_top, "Source")
default_maat_daf_support = os.path.join(maat_dat_top, "Support")
default_hardware_configuration_path = os.path.join(maat_dat_top, "System")
default_maat_daf_data = os.path.join(maat_dat_top, "Data")

verbosity_levels = ['debug', 'info', 'warning', None]

parser = argparse.ArgumentParser(description="method to retrieve ecmwf data for wrf",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-c',
                    action="count",
                    default=0,
                    help='Cleans the directory after an assimilation cycle and results are stored in the diagnostic partition,'
                         'the level of cleaning depends on the number of "c", -c replace geogrid -cc replace ungrib -ccc replace ungrib and geogrid')

parser.add_argument("--api_configuration", help="The application configuration file",
                    default=None)
parser.add_argument("--api_configuration_path", help="The application configuration file",
                    default=None)

parser.add_argument("--MaatDafSource", help="The absolution path for maat daf source partition",
                    default=default_maat_daf_source)

parser.add_argument("--MaatDafData", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_data)

parser.add_argument("--MaatDafSupport", help="The absolution path for maat daf data partition",
                    default=default_maat_daf_support)

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


# read the configuration file
if __name__ == "__main__":
    """
    This project is about getting ecmwf data for the wrf runs
    the configuration file is in the standard location 
    the get initial conditions flag triggers the retrieval of multiple initial conditions for the date """
    # initialise the specific process

    project = NwpForWrfClass(parser=parser)

    project.__setup_nwp4wrf__(truncation=1279)
    project.configuration["api"]["nwp"]["bgerr"] = {"retrieve":True}
    project.configuration["api"]["bgerr"] = {"temporal":{"start": "2019081400",
                                                         "end":"2019082100"
                                                         }
                                             }


    if project.configuration["api"]["nwp"]["bgerr"]["retrieve"]:

        time_period_start = datetime.datetime.strptime(
            project.configuration["api"]["bgerr"]["temporal"]["start"] , "%Y%m%d%H"
        )
        time_period_end = datetime.datetime.strptime(
            project.configuration["api"]["bgerr"]["temporal"]["end"], "%Y%m%d%H"
        )
        current_date = time_period_start
        while True:
            if current_date < time_period_end:
                print("getting lbc for {}".format(current_date))
                project.date = current_date.strftime("%Y%m%d")
                project.__update_topography_nwp4wrf__()
                for time in ["00", "12"]:
                    for step in ["12", "24", "36", "48"]:
                        project.__atmosphere_for_bgerr_file__(date=current_date.strftime("%Y%m%d"), time=time, step=step)
                # project.__surface__()
                current_date += datetime.timedelta(days=1)
            else:
                project.__clean_topography__()
                break

