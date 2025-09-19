#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J HD189567_2p
### -- ask for number of cores (default: 1) -- 
#BSUB -n 16
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
### -- specify that we want the job to get killed if it exceeds 5GB per core/slot -- 
#BSUB -M 5GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 24:00
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o HD189567_2p.out

export PATH="/zhome/9d/b/207249/anaconda3/bin:$PATH"
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh

# Activate Conda environment
conda activate pyorbit

pyorbit_run emcee HD189567_2p.yaml > HD189567_2p.log
pyorbit_results emcee HD189567_2p.yaml -all > HD189567_2p.log