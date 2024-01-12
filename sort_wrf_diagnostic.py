#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import logging
import shutil
import calendar
import datetime



logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)
mylogger.debug('This message should go to the log file')
mylogger.info('So should this')
#logging.warning('And this, too')
mylogger.error('And non-ASCII stuff, too, like Øresund and Malmö')

mylogger.info ("is this working")

if __name__ == '__main__':
    """
    The transret file name  have a generic structure    
    given a date window, all transret files with granula start and end date will be read and put into a single file

    There are two calls: Geogrid and Ungrib

    Geogrid: _geogrid_(mylogger=mylogger, FlgGeoGridReplace=False)

                 if FlgGeoGridReplace = True will replace existing geogrid file geo_em.d01.nc and 
                 generate a new one

                 if FlgGeoGridReplace = False if a geo_em.d01.nc is found in the static directory then
                 no new is generated, if not found a new will be generated
    Ungrib: _ungrib_(mylogger=mylogger, FlgUnGribReplace=False)

                 if FlgUnGribReplace = True will replace existing ungrib files and append any new ones

                 if FlgGeoGridReplace = False will only append any new ungrib files

    """
    assimilation_experiment = os.path.join("/home/stephen","W4ReppProjectData/AUG19/")
    assimilation_experiment = os.path.join("/home/stephen","BlackForestProjectData/AUG19/")
    exgate_repository = os.path.join(assimilation_experiment, "facility","exgate")
    assimilation_experiments = ["CTRL", "NHTR", "NOHL", "NOTR"]
    d0 = datetime.datetime.strptime("201912011200","%Y%m%d%H%M")
    d0 = datetime.datetime.strptime("201908161200", "%Y%m%d%H%M")
    days = 2
    available_analysis: list = [d0 + key*datetime.timedelta(hours=6) for key in range(0, days*4-2)]
    wrfvar_output = "wrfvar_output"
    wrfvar_background = "wrfvar_background"


    top_of_search = os.path.join(assimilation_experiment, "Cycle")
    for experiment in assimilation_experiments:
        for analysis in available_analysis:
            yymmdd = analysis.strftime("%Y%m%d")  # "20190817"
            hh = analysis.strftime("%H%M")  # "1800"
            source_path = os.path.join(top_of_search, experiment, yymmdd, hh, "assimilation", "production")
            target_path = os.path.join(assimilation_experiment, "diagnostic",
                                       experiment, yymmdd, hh)
            if os.path.exists(target_path):
                pass
            else:
                os.makedirs(target_path)
            # first the background
            source_file_name = analysis.strftime("wrfout_d01_%Y-%m-%d_%H:%M:00.mean")
            target_file_name = "_".join([wrfvar_background,analysis.strftime("%Y%m%d%H%M"),experiment+".nc"])
            try:
                if os.path.exists(os.path.join(source_path,source_file_name)):
                    srcfn = os.path.join(source_path,source_file_name)
                    trgfn = os.path.join(target_path,target_file_name)
                    logging.info("copying {} \n to \n {}".format(srcfn, trgfn))
                    shutil.copy(srcfn, trgfn)
            except:
                logging.error("failed to copy {}".format(target_file_name))
                pass
            # second the analysis
            for source_file_name in ["wrfvar_output", "grad_fn",
                        "gts_omb_oma_01", "gts_omb_oma_02", "gts_omb_oma_03",
                        "qcstat_conv_01", "qcstat_conv_02", "qcstat_conv_03",
                        "statistics"]:
                if source_file_name == "wrfvar_output":
                    target_file_name = "_".join([source_file_name,analysis.strftime("%Y%m%d%H%M"),experiment+".nc"])
                else:
                    target_file_name = source_file_name
                try:
                    if os.path.exists(os.path.join(source_path,source_file_name)):
                        srcfn = os.path.join(source_path,source_file_name)
                        trgfn = os.path.join(target_path,target_file_name)
                        logging.info("copying {} \n to \n {}".format(srcfn, trgfn))
                        shutil.copy(srcfn, trgfn)
                except:
                    logging.error("failed to copy {}".format(target_file_name))
                    pass



