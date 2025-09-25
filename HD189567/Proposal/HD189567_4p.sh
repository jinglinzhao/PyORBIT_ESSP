#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J HD189567_4p
### -- ask for number of cores (default: 1) -- 
#BSUB -n 48
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=0.5GB]"
### -- specify that we want the job to get killed if it exceeds 5GB per core/slot -- 
#BSUB -M 1GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 10:00
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o HD189567_4p.out

export PATH="/zhome/9d/b/207249/anaconda3/bin:$PATH"
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh

# Activate Conda environment
conda activate pyorbit

# Add font fix
export MPLBACKEND=Agg
# Suppress font warnings
export PYTHONWARNINGS="ignore::UserWarning:matplotlib"

NAME="HD189567_4p"

# Create output directory FIRST
mkdir -p ${NAME}

echo "Starting PyORBIT emcee run..."
pyorbit_run emcee ${NAME}.yaml

# Check if the first command succeeded before running results
if [ $? -eq 0 ]; then
    echo "PyORBIT run completed successfully, generating results..."
    pyorbit_results emcee ${NAME}.yaml -all > ./${NAME}/${NAME}.log
    cp ${NAME}.yaml ./${NAME}/
    echo "Job completed successfully"
else
    echo "ERROR: PyORBIT run failed"
    exit 1
fi