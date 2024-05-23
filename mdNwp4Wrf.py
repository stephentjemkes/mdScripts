import os
import datetime
from maatdafpy.NwpForWrfModule import NwpForWrfClass

# read the configuration file
if __name__ == "__main__":
    """
    This project is about getting ecmwf data for the wrf runs
    the configuration file is in the standard location 
    the get initial conditions flag triggers the retrieval of multiple initial conditions for the date """
    # initialise the specific process
    description = "DESCRIPTION:\n"
    description += "This script prepares collects the global NWP data for the LBC and IC\n"

    project = NwpForWrfClass(valid_options=None,
                             description=description,
                             processing_type="nwp4wrf")

    project.__setup_nwp4wrf__()

    if project.configuration["api"]["nwp"]["ic"]["retrieve"]:
        project.forecast_base_time = datetime.datetime.strptime(
            project.configuration["api"]["nwp"]["ic"]["base time"], "%Y%m%d%H"
        )
        project.forecast_step = project.configuration["api"]["nwp"]["ic"]["step"]
        project.first_ensemble_member = project.configuration["api"]["nwp"]["ic"]["first ensemble member"]
        project.last_ensemble_member = project.configuration["api"]["nwp"]["ic"]["last ensemble member"]

        project.__get_multiple_initial_conditions__(elda=True)

    if project.configuration["api"]["nwp"]["lbc"]["retrieve"]:

        time_period_start = datetime.datetime.strptime(
            project.configuration["api"]["domains"]["temporal"]["start"], "%Y%m%d%H"
        )
        time_period_end = datetime.datetime.strptime(
            project.configuration["api"]["domains"]["temporal"]["end"], "%Y%m%d%H"
        )
        current_date = time_period_start
        while True:
            if current_date < time_period_end:
                print("getting lbc for {}".format(current_date))
                project.date = current_date.strftime("%Y%m%d")
                project.__update_topography_nwp4wrf__()
                project.__atmosphere__()
                project.__surface__()
                current_date += datetime.timedelta(days=1)
            else:
                project.__clean_topography__()
                break

