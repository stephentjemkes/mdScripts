#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a control script which launches the different sub-process modules

import os
import argparse
import socket

from maatdafpy.WrfDeterministicCycleModule import WrfDeterministicCycleClass
Cred = '\033[91m'
Cgreen = '\033[42m'
Cend = '\033[0m'

exstring = "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" * 2

VALID_OPTIONS = {
            "hyb4dvar": {"type": "true_false", "default": True},
            "dual_resolution": {"type": "true_false", "default": False},
            "enkfvar": {"type": "true_false", "default": False},
            "start": {"type": "warm_cold", "default": "warm"},
            "genbe_v2":{"type": "true_false", "default": False}
        }

description = "DESCRIPTION:\n" + \
                      'This script controls the da process . \n'
description += "Its function is controlled by a user configuration file and options \n"
description += "These options are provided in the form -o Option=Value Option2=Value"
description += "Valid options are \n"
for key in VALID_OPTIONS:
    description += 'Option: {0:<20s}'.format(key)
    description += "valid values: {}\n".format(VALID_OPTIONS[key])
description += "\n" + Cred + exstring + Cend + "\n"
description += Cred + "Note: " + Cend + "Dual_resolution can only be used in combination with hyb4dvar\n"
description += "and if dual_resolution is true, then automatically enkfvar will be set\n"
description += exstring+ "\n"

if __name__ == "__main__":
    #
    # configure this project
    #
    static_background_project = WrfDeterministicCycleClass(valid_options=VALID_OPTIONS,
                               description=description,
                               processing_type="forecast")
    # project has been configured
    # can start with the processing
    # first step is to spin up the system
    # This is only valid for a cold_start

    while True:
        #
        # Not an real indefinate loop:
        # we test this at the beginning such that it works also for a warm start without any change of status
        #
        if static_background_project.AnalysisTime >= static_background_project.string_to_date(
                static_background_project.configuration["api"]["domains"]["temporal"]["end"]):
            msg = Cred + "\n" + exstring
            msg += "\n We came so far, all way untill the end of the experiment date"
            msg += "{}\n".format(
                static_background_project.string_to_date(static_background_project.configuration["api"]["domains"]["temporal"]["end"])
            )
            msg += exstring + Cend
            static_background_project.logger.info(msg)

            # we have cycled through all the period within the experiment so break loop
            break
        if static_background_project.configuration["api"]["deterministic"]["forecast"]["cycle"]["maximum number"] > 0 and \
                static_background_project.cycle_number >= \
                static_background_project.configuration["api"]["deterministic"]["forecast"]["cycle"]["maximum number"]:
            # if we have performed N-cycles we break as well
            static_background_project.logger.info(
                Cred + "\n" + exstring + "\n We stop the cycling as we have exceeded the maximum cycles {}\n".format(
                    static_background_project.cycle_number) + exstring + Cend)
            break

        #
        # update the key parameters for the next process cycle
        #
        #

        os.chdir(static_background_project.path["maatdaf.main"])
        # [1.0] the topography
        #
        static_background_project.__update_topography__()

        # [1.1] reset the wrf namelist to the default
        #       during the cycling process the namelist especially for the assimilation runs
        #       So we need to reset the namelist to the default values provided by the
        #       configuration file
        static_background_project.__reset_wrf_default_namelist__()
        static_background_project.__wrf_model_initialize__()

        # [2.0] The deterministic forecast run

        if static_background_project.processing["status"]["deterministic_forecast"] == "start":
            static_background_project.processing["status"]["deterministic_forecast"] = \
                static_background_project.__wrf_model_run_wrf_model__()
            static_background_project._save_processing_state_()

        if static_background_project.processing["status"]["deterministic_forecast"] == "completed" \
                and \
            static_background_project.processing["status"]["save diagnostic results"] == "start":
            static_background_project.processing["status"]["save diagnostic results"] = \
                static_background_project.__wrf_model_save_forecast__()
            static_background_project._save_processing_state_()


        #
        #  update the state and start a new cycle
        #
        if static_background_project.clean_level > 0:
            static_background_project.__clean__()

        static_background_project._update_processing_state_()

        # we return to the project root
        os.chdir(static_background_project.path["maatdaf.main"])
    # before we leave we save the state at exit
    static_background_project.logger.info(Cred + "\n" + exstring + "\n BYE NOW\n" + exstring + Cend)
