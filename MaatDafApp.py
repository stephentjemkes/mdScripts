#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a control script which launches the different sub-process modules

import os

from maatdafpy.WrfVarCycleModule import WrfVarCycleClass
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

DESCRIPTION = "DESCRIPTION:\n" + \
                      'This script controls the da process . \n'
DESCRIPTION += "Its function is controlled by a user configuration file and options \n"
DESCRIPTION += "These options are provided in the form -o Option=Value Option2=Value"
DESCRIPTION += "Valid options are \n"
for key in VALID_OPTIONS:
    DESCRIPTION += 'Option: {0:<20s}'.format(key)
    DESCRIPTION += "valid values: {}\n".format(VALID_OPTIONS[key])
DESCRIPTION += "\n" + Cred + exstring + Cend + "\n"
DESCRIPTION += Cred + "Note: " + Cend + "Dual_resolution can only be used in combination with hyb4dvar\n"
DESCRIPTION += "and if dual_resolution is true, then automatically enkfvar will be set\n"
DESCRIPTION += exstring+ "\n"

if __name__ == "__main__":
    #
    # configure this project
    #
    data_assimilation_project = WrfVarCycleClass(description=DESCRIPTION,
                                                 processing_type="assimilation",
                                                 valid_options=VALID_OPTIONS)
    # project has been configured
    # can start with the processing
    # first step is to spin up the system
    # This is only valid for a cold_start

    while True:
        #
        # Not an real indefinate loop:
        # we test this at the beginning such that it works also for a warm start without any change of status
        #
        if data_assimilation_project.AnalysisTime >= data_assimilation_project.string_to_date(
                data_assimilation_project.configuration["api"]["domains"]["temporal"]["end"]):
            msg = Cred + "\n" + exstring
            msg += "\n We came so far, all way untill the end of the experiment date"
            msg += "{}\n".format(
                data_assimilation_project.string_to_date(data_assimilation_project.configuration["api"]["domains"]["temporal"]["end"])
            )
            msg += exstring + Cend
            data_assimilation_project.logger.info(msg)

            # we have cycled through all the period within the experiment so break loop
            break
        if data_assimilation_project.configuration["api"]["assimilation"]["cycle"]["maximum number"] > 0 and \
                data_assimilation_project.cycle_number >= data_assimilation_project.configuration["api"]["assimilation"][data_assimilation_project.temporal_period]["maximum cycles"]:
            # if we have performed N-cycles we break as well
            data_assimilation_project.logger.info(
                Cred + "\n" + exstring + "\n We stop the cycling as we have exceeded the maximum cycles {}\n".format(
                    data_assimilation_project.cycle_number) + exstring + Cend)
            break

        #
        # update the key parameters for the next process cycle
        #
        #
        # logic:
        # 1. the topography needs to initialised
        # 2. Ensemble needs to be generated
        # 3. Genbe generates the error and covariance
        # 3.a Genbe_v2 is used to generate a netcdf file for diagnostic purposes
        # 4. Obsproc generates the little R format
        # 5. Assimilation generates the analysis
        # 6. Update ensures that lbc and analysis are consistent for the next cycle
        # [0.0] we start at project root
        os.chdir(data_assimilation_project.path["maatdaf.main"])
        # [1.0] the topography
        #
        data_assimilation_project.__update_topography__()

        # [1.1] reset the wrf namelist to the default
        #       during the cycling process the namelist especially for the assimilation runs
        #       So we need to reset the namelist to the default values provided by the
        #       configuration file
        data_assimilation_project.__reset_wrf_default_namelist__()
        data_assimilation_project.__wrf_model_initialise_ensemble__()

        # [2.0] The ensemble
        # [2.1] with the understanding that if cycle_number == 1, we link the ensemble results of the non-cycle run
        #          to the first cycle

        if data_assimilation_project.processing["status"]["ensemble"] == "start":
            data_assimilation_project.processing["status"]["ensemble"] = data_assimilation_project.__wrf_model_create_ensemble__()
            data_assimilation_project._save_processing_state_()

        # [3.0] The genbe v3
        # [3.1] is used to generate the background error covariance for the assimilation
        #if data_assimilation_project.processing["status"]["genbe"] == "start":
        #    data_assimilation_project.processing["status"]["genbe"] = data_assimilation_project.__genbe_execute__()
        #    data_assimilation_project.__genbe_save_diagnostics__()
        #    data_assimilation_project._save_processing_state_()

        # [3.0] The genbe v2
        # [3.1] is used to generate the background error covariance in netcdf format for diagnostic purposes
        #if data_assimilation_project.option["genbe_v2"]:
        #    if data_assimilation_project.processing["status"]["genbe_v2"] == "start":
        #        data_assimilation_project.processing["status"]["genbe_v2"] = \
        #            data_assimilation_project.__genbe_execute__(version="v2.1")
        #        data_assimilation_project._save_processing_state_()


        if data_assimilation_project.processing["status"]["obsproc"] == "start":
            data_assimilation_project.processing["status"]["obsproc"] = data_assimilation_project.__obsproc_execute__()
            data_assimilation_project._save_processing_state_()

        # shall we run the hyb4dvar?
        if data_assimilation_project.option["hyb4dvar"]:
            #
            # Determine the background forecast times, and the number of background files needed.
            #
            data_assimilation_project.__wrf_hyb4dvar_preamble__()
            #
            # now we calculate the mean and perturbations for each background forecast time
            #
            if data_assimilation_project.processing["status"]["prepare assimilation"] == "start":
                data_assimilation_project.processing["status"]["prepare assimilation"] = \
                    data_assimilation_project.__wrf_hyb4dvar_prepare_assimilation__()
                data_assimilation_project._save_processing_state_()
            #
            # The main assimilation to get the main analysis and cost function etc
            # results will be stored in the diagnostic output
            #
            if data_assimilation_project.processing["status"]["main assimilation"] == "start":
                data_assimilation_project.processing["status"]["main assimilation"] = \
                    data_assimilation_project.__wrf_hyb4dvar_assimilation_execute__()
                data_assimilation_project._save_processing_state_()

            #
            # if return is False, then the process was successfully completed
            #
            if data_assimilation_project.processing["status"]["main assimilation"] == "completed":
                #
                # first save diagnostic output like omb and cost function from main assimilation
                #
                if data_assimilation_project.processing["status"]["save diagnostic results"] == "start":
                    data_assimilation_project.processing["status"]["save diagnostic results"] = \
                        data_assimilation_project.__wrf_hyb4dvar_save_diagnostic_results__()
                    data_assimilation_project._save_processing_state_()
            #
            # The hyb4DVar system produces a single deterministic analysis.
            # To generate an esemble using multiple initial conditions we can use
            # the randomcv extention to get the multiple analysis
            # or use the EnKF-submodule
            #

        if data_assimilation_project.option["enkfvar"]:
            data_assimilation_project.__wrf_enkfvar_preamble__()
            data_assimilation_project.__wrf_enkfvar_prepare_filtered_observations__()

        if data_assimilation_project.processing["status"]["prepare multiple ic"] == "start":
            data_assimilation_project.processing["status"]["prepare multiple ic"] = \
                data_assimilation_project.__update_randomcv_execute__()
            data_assimilation_project._save_processing_state_()
        #
        # and then we update the initial conditions for the next cycle
        # The module is part of the WrfUpdateInitialConditionModule
        #
        #
        # finally save the updated initial conditions, which includes the multiple ic
        #
        if data_assimilation_project.processing["status"]["save update initial conditions"] == "start":
            data_assimilation_project.processing["status"]["save update initial conditions"] = \
                data_assimilation_project.__wrf_update_save_results__()
            data_assimilation_project._save_processing_state_()

        #
        #  update the state and start a new cycle
        #
        if data_assimilation_project.clean_level > 0:
            data_assimilation_project.__clean__()

        data_assimilation_project._update_processing_state_()

        # we return to the project root
        os.chdir(data_assimilation_project.path["maatdaf.main"])
    # before we leave we save the state at exit
    data_assimilation_project.logger.info(Cred + "\n" + exstring + "\n BYE NOW\n" + exstring + Cend)
