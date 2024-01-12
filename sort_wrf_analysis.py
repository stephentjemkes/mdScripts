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
    cases = ["Baseline", "Exp01", "Exp02"]
    exgate_repository = os.path.join("/home/stephen","BlackForestProjectData/AUG19/", "facility","exgate")
    assimilation_experiments = {"Baseline":["CTRL", "NHTR", "NOHL", "NOTR"],
                                "Exp01":["CTRL", "NHTR"],
                                "Exp02":["CTRL", "NHTR"]
                                }
    d0 = datetime.datetime.strptime("201908161200","%Y%m%d%H%M")
    available_analysis: list = [d0 + key*datetime.timedelta(hours=6) for key in range(0,6)]
    nc_file_name_no_ext = "wrfvar_output"
    for case_id in cases:
        top_of_search = os.path.join("/home/stephen", "BlackForestProjectData/AUG19/", "Cycle", case_id)
        for experiment in assimilation_experiments[case_id]:
            for analysis in available_analysis:
                yymmdd = analysis.strftime("%Y%m%d")  # "20190817"
                hh = analysis.strftime("%H%M")  # "1800"

                source_path = os.path.join(top_of_search, experiment, yymmdd, hh, 'assimilation','production')
                target_file_name = "_".join([nc_file_name_no_ext,analysis.strftime("%Y%m%d%H%M"),experiment+".nc"])
                target_path = os.path.join(exgate_repository, case_id)
                if os.path.exists(target_path):
                    pass
                else:
                    os.makedirs(target_path)
                try:
                    source_file = os.path.join(source_path, nc_file_name_no_ext)
                    target_file = os.path.join(target_path, target_file_name)
                    logging.info("copying {} \n to \n {}".format(source_file, target_file))
                    shutil.copy(source_file, target_file)
                except:
                    logging.error("failed to copy {}".format(target_file))
                    pass



