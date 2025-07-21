#!/bin/sh
### General options
### -- specify queue --
#BSUB -q hpc
### -- set the job Name --
#BSUB -J PyORBIT_ESSP
### -- ask for number of cores --
#BSUB -n 32
### -- specify that the cores must be on the same host --
#BSUB -R "span[hosts=1]"
### -- OPTIMIZED: reduce memory per core from 4GB to 1GB --
#BSUB -R "rusage[mem=1GB]"
### -- OPTIMIZED: reduce memory limit from 5GB to 2GB per core --
#BSUB -M 2GB
### -- OPTIMIZED: increase walltime from 1:00 to 3:00 hours --
#BSUB -W 1:00
### -- set the email address --
#BSUB -u jzhao@space.dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion --
#BSUB -N
### -- Specify the output and error file --
#BSUB -o /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Output_ESSP_%J.out
#BSUB -e /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Error_ESSP_%J.err


cd /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP
mkdir -p logfiles

# Activate Conda environment
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
instrument="HARPS_EXPRES_NEID_HARPSN"
# instrument="HARPSN_EXPRES_NEID_HARPS"
NAME="ESSP_gp_${instrument}"

echo "Starting PyORBIT analysis for ${NAME} at $(date)"
echo "Working directory: $(pwd)"
echo "Available cores: $LSB_DJOB_NUMPROC"

# Create output directory
mkdir -p ${NAME}

# Add progress monitoring
echo "Step 1: Running MCMC sampling..."
pyorbit_run emcee ${NAME}.yaml

echo "Step 2: Generating results at $(date)..."
pyorbit_results emcee ${NAME}.yaml -all > ./${NAME}/${NAME}.log

echo "Step 3: Copying configuration..."
cp ${NAME}.yaml ./${NAME}/

echo "PyORBIT analysis completed at $(date)"

# Optional: Print resource usage
echo "=== Resource Usage Summary ==="
echo "Job ID: $LSB_JOBID"
echo "Cores used: $LSB_DJOB_NUMPROC"
echo "Host: $LSB_HOSTS"