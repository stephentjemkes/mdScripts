'''
This is a simple script to "automate" the compilation of the wrf system
It is based on the pexpect module, which spawn the three commands needed to 
- clean
- configure
- compile

'''

import shutil
import os
import datetime
import argparse
import numpy
import json
import subprocess
import Configuration

from pymodules.LoggerModule import WrfLoggerClass

import pexpect

text = {}
text["description"] = "DESCRIPTION: \n" 
text["description"]+='The WRF Control to "automate" the compilation of the wrf system \n'
text["description"]+='It is based on the pexpect module, which spawn the three commands needed to generate makefile and run. \n'
text["description"]+='\tclean, \n \tconfigure, \n \tcompile\n'
text["description"]+='The logfile of compilation is in the "build" subdirectory of the main wrf directory\n'
text["description"]+='The logfile name is an arguement of the script\n'
text["description"]+='Typical use python3 wrf_compile.py -l wrf_added_transret_compilation.log\n'
text["description"]+='It takes about 400 sec to complete\n'

verbosity_levels = ['debug', 'info', 'warning', None]

default_api_configuration_file = "w4repp.json"
default_system_configuration_file = "dell_inspiration.cfg"
default_project_root = os.path.join("/home/stephen/BlackForestWeather/wrfcntrl")
parser = argparse.ArgumentParser(description=text["description"],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--project_root_path", help="The absolution path for runtime base",\
                    default=default_project_root)
parser.add_argument("--sys_config", help="The system configuration file", \
                    default=default_system_configuration_file)
parser.add_argument("--api_config", help="The application configuration file", \
                    default=default_api_configuration_file)
parser.add_argument('-c', '--configure_options', choices=[32,34], 
                    default=32,type=int,
                    help='The different configuration option for linux')

parser.add_argument('-l', '--compilation_logfile', default=None,
                    help='The configuration logfile')

parser.add_argument('-v', '--verbosity', choices=verbosity_levels, default='info',
                    help='The level of verbosity of the software')
args = parser.parse_args()

api_configuration_file = os.path.join(*[args.project_root_path, "configuration", args.api_config])
sys_configuration_file = os.path.join(*[args.project_root_path, "configuration", args.sys_config])

__CONFIGURATION__ = Configuration.BasicConfiguration([sys_configuration_file])

Configuration.BasicSettings(api_configuration_file,)
__SETTINGS__ = Configuration._setting_

if __name__ == '__main__':
    """
    The transret file name  have a generic structure    
    given a date window, all transret files with granula start and end date will be read and put into a single file
    
    """    
    child = pexpect.spawn('date')
    # Read the child output without generating EOF
    child.expect(pexpect.EOF)
    # Store the text that is expected by the string pattern
    output = child.before
    today = output.decode("utf-8")
    # Print the output
    print("Today is : {}".format(today))
    mylogger = WrfLoggerClass()
    myLogger = mylogger._set_logger_ (\
        configuration=__CONFIGURATION__,\
        settings=__SETTINGS__, \
        verbosity=args.verbosity\
    )

    log_file = args.compilation_logfile
    if args.compilation_logfile == None:
        log_file = __SETTINGS__['api']["compilation"]["logging"]["main_log_file"]
    
    build_log_file = os.path.join(__CONFIGURATION__.get('File System', 'logging partition'),"build",log_file)
    
    log_path, log_file = os.path.split(build_log_file)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # change to wrf main directory is important
    wrf_source_code_partition =__CONFIGURATION__.get('File System', 'source code partition')
    os.chdir(wrf_source_code_partition)
    cmd = os.path.join(wrf_source_code_partition,"clean") +" -a"
    child = pexpect.spawnu(cmd)
    child.expect(pexpect.EOF)
    cmd = os.path.join(wrf_source_code_partition,"configure") +" wrfda"
    child = pexpect.spawn(cmd)
    child.expect("[Enter selection]")
    child.sendline(str(args.configure_options))
    child.expect(pexpect.EOF)
    
    fh = open(build_log_file,'wb')
    command = os.path.join(wrf_source_code_partition,"compile")
    command += " all_wrfvar"
    child = pexpect.spawn(command, timeout=600)
    child.logfile = fh
    child.expect(pexpect.EOF)
    output = child.before
    fh.close()
