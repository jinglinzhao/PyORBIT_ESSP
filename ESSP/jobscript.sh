#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J PyORBIT_ESSP
### -- ask for number of cores (default: 1) -- 
#BSUB -n 64
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 3GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
### -- specify that we want the job to get killed if it exceeds 5 GB per core/slot -- 
#BSUB -M 10GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 1:00 
### -- set the email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
##BSUB -u jzhao@space.dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
### -- -o and -e mean append, -oo and -eo mean overwrite -- 
#BSUB -o /work2/lbuc/jzhao/PyORBIT_ESSP/logfiles/Output_ESSP.out
#BSUB -e /work2/lbuc/jzhao/PyORBIT_ESSP/logfiles/Error_ESSP.err


# Activate Conda environment
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh  # This path depends on where conda is installed
conda activate pyorbit

# here follow the commands you want to execute with input.in as the input file
./ESSP_gp.source