import xarray
import datetime
import os
import shutil
import re
import logging
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger(__name__)
mylogger.debug('This message should go to the log file')
mylogger.info('So should this')
#logging.warning('And this, too')
mylogger.error('And non-ASCII stuff, too, like Øresund and Malmö')

mylogger.info ("is this working")

class NetCDFInterFaceClass():
    def __init__(self, logger=False, analysis=None, path=None):
        self.logger=logger
        self.AnalysisTime= analysis
        self.project_dynamic_data_partition = os.path.join("/home/stephen/","BlackForestProjectData/", "dynamic")
        this_path=os.path.join("/home/stephen/","BlackForestProjectData/AUG19/Cycle/CTRL/20190817/0600/obsproc/production")
        self.path=dict(obsproc=dict(production=this_path))

    def _read_single_file_(self, single_netcdf_file):


        self.logger.debug("opening {}".format(single_netcdf_file))
        self.prof_data = xarray.open_dataset(single_netcdf_file, group='rayleigh_profile_data')
        self.wind_data = xarray.open_dataset(single_netcdf_file, group='rayleigh_wind_data')
        # note the date is since datetime.datetime(2000, 1, 1)
        epoch = datetime.datetime(2000, 1, 1)
        Tstart = []
        Tcog = []
        for key in zip(self.wind_data.rayleigh_wind_result_start_time,
                       self.wind_data.rayleigh_wind_result_COG_time):
            Tstart.append(epoch + datetime.timedelta(seconds=key[0].item(0)))
            Tcog.append(epoch + datetime.timedelta(seconds=key[1].item(0)))

        # make a figure
        figure_name =  self.AnalysisTime.strftime("Start_time_%Y-%m-%d.png")
        fig, ax = plt.subplots(1,1,figsize=(8,8))
        ax.plot(Tstart, label="{}".format('start'))
        ax.plot(Tcog, label="{}".format('COG'))
        plt.legend()

        plt.savefig(figure_name)
        plt.show()
        a=1
    def _combine_daily_aeolus_(self):
        """
        the Aeolus data is available as a daily dataset
        we need to combine this into a dataset for the specific assimilation window
        obsproc
        """

        FILE_MASK = 'L2B_rayleigh_wind_(?P<start>\d{4}-\d{2}-\d{2})-'

        FILE_MASK += '(?P<end>\d{4}-\d{2}-\d{2})\.nc'
        aeolus_repository = os.path.join(self.project_dynamic_data_partition, "satellite/aeolus/netcdf/daily")

        selected_aeolus_files = []
        Analysis_day =  self.AnalysisTime.strftime("%Y-%m-%d")
        Analysis_next_day = (self.AnalysisTime + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        aeolus_file = "L2B_rayleigh_wind_"+Analysis_day+"-"+Analysis_next_day+".nc"

        #for aeolus_file in daily_aeolus_files:
        #    file_matches_mask = re.match(FILE_MASK, aeolus_file)
        #    if file_matches_mask:
        #        data_granula_start = datetime.datetime.strptime(file_matches_mask.group("start"), "%Y-%m-%d")
        #        data_granula_end = datetime.datetime.strptime(file_matches_mask.group("end"), "%Y-%m-%d")
        #        # we pick all files within a window of 24 hours around analysis time
        #        if abs((data_granula_start - self.AnalysisTime).total_seconds()) < 86400 or abs(
        #                (data_granula_end - self.AnalysisTime).total_seconds()) < 86400:
        #            selected_aeolus_files.append(os.path.join(aeolus_repository, 'daily', aeolus_file))

        self.aeolus_data_file = "_".join(['aeolus_data_file', self.AnalysisTime.strftime("%Y%m%d%H%M")]) + ".nc"
        self.full_path_aeolus_data_file = os.path.join(self.path["obsproc"]["production"], self.aeolus_data_file)

        if os.path.exists(self.full_path_aeolus_data_file):
            os.remove(self.full_path_aeolus_data_file)
        src = os.path.join(aeolus_repository, aeolus_file)
        shutil.copyfile(src, self.full_path_aeolus_data_file)

        #if (len(selected_aeolus_files) >= 0):
        #    self.logger.debug("for {} we found {} aeolus files".format(self.AnalysisTime, len(selected_aeolus_files)))
        #    self.logger.debug("{}".format(selected_aeolus_files))
        #    ds_rayleigh = {'rayleigh_profile_data': [], "rayleigh_wind_data": []}
        #    for groupno, group in enumerate(ds_rayleigh):
        #        for aeolus_file_key in selected_aeolus_files:
        #            ds_rayleigh[group].append(xarray.open_dataset(aeolus_file_key, group=group))
        #        ds = xarray.concat(ds_rayleigh[group], dim=group)
        #        if groupno == 0:
        #            ds.to_netcdf(self.full_path_aeolus_data_file, 'w', group=group)
        #        else:
        #            ds.to_netcdf(self.full_path_aeolus_data_file, 'a', group=group)


if __name__ == '__main__':
    """
    Given the assimilation date we combine the Aeolus rayleigh observations around this date into one file
    """

    analysis = datetime.datetime.strptime("201908170600","%Y%m%d%H%M")
    aeolus_data = NetCDFInterFaceClass(analysis=analysis, logger=mylogger)
    aeolus_data_file = "L2B_rayleigh_wind_2019-08-17-2019-08-18.nc"

    # aeolus_data._combine_daily_aeolus_()
    single_netcdf_file = os.path.join(aeolus_data.project_dynamic_data_partition, "satellite/aeolus/netcdf/daily",
                                      aeolus_data_file)
    single_netcdf_file = os.path.join("/home/stephen/BlackForestProjectData/AUG19/Cycle/CTRL/20190817/0600/obsproc/production/aeolus_data_file_201908170600.nc")
    aeolus_data._read_single_file_(single_netcdf_file)




