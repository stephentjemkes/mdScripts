#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a control script which launches the different sub-process modules

import os
import argparse
import socket

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
text = {}
text["description"] = "DESCRIPTION:\n" + \
                      'This script controls the da process . \n'
text["description"] += "Its function is controlled by a user configuration file and options \n"
text["description"] += "These options are provided in the form -o Option=Value Option2=Value"
text["description"] += "Valid options are \n"
for key in VALID_OPTIONS:
    text["description"] += 'Option: {0:<20s}'.format(key)
    text["description"] += "valid values: {}\n".format(VALID_OPTIONS[key])
text["description"] += "\n" + Cred + exstring + Cend + "\n"
text["description"] += Cred + "Note: " + Cend + "Dual_resolution can only be used in combination with hyb4dvar\n"
text["description"] += "and if dual_resolution is true, then automatically enkfvar will be set\n"
text["description"] += exstring+ "\n"

verbosity_levels = ['debug', 'info', 'warning', None]

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
default_maat_daf_top = os.path.join(os.environ["HOME"],"maatdaf")
default_maat_daf_source = os.path.join(default_maat_daf_top,"Source")
default_maat_daf_support = os.path.join(default_maat_daf_top,"Support")
default_maat_daf_data = os.path.join(default_maat_daf_top,"Data")
default_maat_daf_user = os.path.join(default_maat_daf_top,"User")
default_maat_daf_system = os.path.join(default_maat_daf_top,"System")


parser = argparse.ArgumentParser(
    description=text["description"],
    formatter_class=argparse.RawDescriptionHelpFormatter
)

class StoreDictKeyPair(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKeyPair, self).__init__(option_strings, dest, nargs=nargs, **kwargs)
    def __validate__(self,key, value):
        true = ["true", "1", "t"]
        false = ["false", "f", "0"]
        warm = ["warm", "w", "1"]
        cold = ["cold", "c", "0"]
        regular = []
        valid_options = VALID_OPTIONS

        consolidated_value = None
        if key in valid_options.keys():
            if  valid_options[key]["type"] == "true_false":
                if value.lower() in true:
                    consolidated_value = True
                elif value.lower() in false:
                    consolidated_value = False
                else:
                    print ("Unkown Value {} for key {}, a type or mistake?".format(value, key))
                    print ("Valid options are {} or {}".format(true, false))
                    raise SystemExit(1)
            if valid_options[key]["type"] == "warm_cold":
                if  value.lower() in warm:
                    consolidated_value = "warm"
                elif value.lower() in cold:
                    consolidated_value = "cold"
                else:
                    print ("Unkown Value {} for key {}, a type or mistake?".format(value, key))
                    print ("Valid options are {} or {}".format(warm, cold))
                    raise SystemExit(1)
        else:
            print ("Unkown option {} {}, a type or mistake?".format(key, value))
            print ("Valid options and default settings")
            for optkey in valid_options:
                 print ("key, {} value {}".format(optkey, valid_options[optkey]))
            print ("Correct and start again")
            raise SystemExit(1)
        return consolidated_value
    def __call__(self, parser, namespace, values, option_string=None):
        my_dict = {}
        for kv in values:
            k, v = kv.split("=")
            self.__validate__(k,v)
            my_dict[k] = self.__validate__(k,v)
        setattr(namespace, self.dest, my_dict)
# configuration files

parser.add_argument('-c',
                    action="count",
                    default=0,
                    help='Cleans the directory after an assimilation cycle and results are stored in the diagnostic partition,'
                         'the level of cleaning depends on the number of "c", -c only limited -cc more cleaning -ccc rigorous')

parser.add_argument('-y',
                    action="count",
                    default=0,
                    help='To bypass the user confirmation')

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

parser.add_argument('-o', '--option', nargs='*',
                    action=StoreDictKeyPair,
                    help='run time options')

args = parser.parse_args()
print ("{}".format(args.option))

if __name__ == "__main__":
    #
    # configure this project
    #
    data_assimilation_project = WrfVarCycleClass(parser=parser, valid_options=VALID_OPTIONS)
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
        if data_assimilation_project.processing["status"]["genbe"] == "start":
            data_assimilation_project.processing["status"]["genbe"] = data_assimilation_project.__genbe_execute__()
            data_assimilation_project.__genbe_save_diagnostics__()
            data_assimilation_project._save_processing_state_()

        # [3.0] The genbe v2
        # [3.1] is used to generate the background error covariance in netcdf format for diagnostic purposes
        if data_assimilation_project.option["genbe_v2"]:
            if data_assimilation_project.processing["status"]["genbe_v2"] == "start":
                data_assimilation_project.processing["status"]["genbe_v2"] = \
                    data_assimilation_project.__genbe_execute__(version="v2.1")
                data_assimilation_project._save_processing_state_()


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
