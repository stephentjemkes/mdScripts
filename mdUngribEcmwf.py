import os
import datetime
from maatdafpy.UngribEcmwfModule import UngribEcmwfClass

if __name__ == "__main__":
    description = "DESCRIPTION:\n"
    description += "This script prepares collects the global NWP data for the LBC and IC\n"

    initial_condition_case = 'ensemble'
    project = UngribEcmwfClass(
                             description=description,
                             processing_type="UngribEcmwf")
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
        # project.__transcribe_available_oper_files__(max_step_value=48)
        #  decode the initial conditions
        project.__transcribe_available_elda_files__()
    pause = -1

