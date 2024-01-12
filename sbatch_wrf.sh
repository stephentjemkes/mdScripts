#!/bin/bash
set -xv

#-------------------------------
# setting options for SLURM
#-------------------------------
# source: ecmwf user support

#SBATCH --job-name=wrfda         # Job name

# Assigns the specified name to the request


# Specifies the name and location of STDERR where %N is the
# node where the job runs and %j the job-id. The file will be
# written in the workdir directory if it is a relative path.
# If not specified, STDERR will be written to the output file
# defined above, or otherwise to slurm-%j.out in the workdir.
# it is also used for the log output

##SBATCH --nodes=4
##SBATCH --ntasks-per-node=8

#SBATCH --ntasks=6
#SBATCH --cpus-per-task=8

# Define, how many nodes you need. Here, we ask for 1 node.
# in theory you can ask for more but it is not recommended
# note that slurm is configured that it can run only one job on a node
# and each node has 8 CPU

#SBATCH --distribution=cyclic

#SBATCH --partition normal

# Define the partition on which the job shall run.
# there is only one partition, but this could change (e.g. priority, normal)

#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=stephen.tjemkes@hotmail.com     # Where to send mail (does not work)

#SBATCH --time=01:59:00               # Time limit hrs:min:sec
#-------------------------------
# setting environment variables
#-------------------------------
while [[ "$1" != "" ]]; do
    case "$1" in
	-s | --skeb )
	    shift
	    skeb=$1
	    ;;
	-p| --physpack )
	    shift
	    physpack=$1
	    ;;
	-w | --workdir )
	shift
	WRKDIR=$1
	;;
	-v | --verbose )
	    shift
            verbose=$1
            ;;
    esac
    shift
done
export PATH=$PATH:.

# The next is to capture the options when the
# script is activated

. /home/stephen/.muprc

cd ${WRKDIR}

time mpiexec.hydra -bootstrap slurm -n 8 ./real.exe

time mpiexec.hydra -bootstrap slurm -n 8 ./wrf.exe