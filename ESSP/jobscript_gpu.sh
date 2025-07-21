#!/bin/sh
### General options
### -- specify GPU queue --
#BSUB -q gpua100
### -- set the job Name --
#BSUB -J PyORBIT_ESSP_GPU_FIXED
### -- ask for fewer cores (GPU mode needs less CPU parallelism) --
#BSUB -n 4
### -- Select the resources: 1 GPU in exclusive process mode --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- specify that the cores must be on the same host --
#BSUB -R "span[hosts=1]"
### -- request memory --
#BSUB -R "rusage[mem=32GB]"
### -- set memory limit --
#BSUB -M 32GB
### -- set walltime limit --
#BSUB -W 2:00
### -- set the email address --
#BSUB -u jzhao@space.dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion --
#BSUB -N
### -- Specify the output and error file --
#BSUB -o /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Output_ESSP_poly_GPU_FIXED_%J.out
#BSUB -e /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Error_ESSP_poly_GPU_FIXED_%J.err

# -- end of LSF options --

cd /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP
mkdir -p logfiles

echo "=== GPU Job Information ==="
echo "Job ID: $LSB_JOBID"
echo "Queue: $LSB_QUEUE"
echo "Host: $LSB_HOSTS"
echo "Cores: $LSB_DJOB_NUMPROC"
echo "Start time: $(date)"

# Check GPU availability
echo "=== GPU Status ==="
nvidia-smi
echo ""

# Load CUDA 11.6
module purge
module load cuda/11.6
module load cudnn/v8.4.1.50-prod-cuda-11.X
echo "CUDA loaded: $(which nvcc)"
nvcc --version

# 🔥 CRITICAL FIX: DISABLE MULTIPROCESSING FOR GPU 🔥
echo "=== Setting Single-Process GPU Environment ==="
export JAX_PLATFORM_NAME=gpu
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.9
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export JAX_ENABLE_X64=true
export XLA_FLAGS="--xla_gpu_cuda_data_dir=/appl/cuda/11.6.0 --xla_gpu_force_compilation_parallelism=4"
export CUDA_VISIBLE_DEVICES=0

# 🎯 KEY FIX: FORCE SINGLE THREADING
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Activate Conda environment
echo "=== Activating PyORBIT Environment ==="
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit_gpu

echo "Active environment: $CONDA_DEFAULT_ENV"
echo "Python version: $(python --version)"

# Test GPU setup
echo "=== JAX GPU Test ==="
python -c "
import jax
import jax.numpy as jnp
print(f'JAX platform: {jax.default_backend()}')
print(f'GPU devices: {jax.devices()}')

# Test GPU computation
A = jnp.array([[1.0, 2.0], [3.0, 4.0]])
result = jnp.linalg.solve(A, jnp.array([1.0, 2.0]))
print('✅ GPU linear algebra test passed')
print(f'Result: {result}')
print(f'Device: {result.device()}')
"

# 🎯 MODIFY PYORBIT CONFIG FOR SINGLE-PROCESS GPU
instrument="HARPSN_EXPRES_NEID_HARPS_poly"
NAME="ESSP_gp_${instrument}"


echo "=== Starting PyORBIT GPU Analysis ==="
echo "Analysis name: ${NAME}"
echo "Working directory: $(pwd)"
echo "GPU memory fraction: $XLA_PYTHON_CLIENT_MEM_FRACTION"
echo "Threading: Single-process mode"
echo ""

# Create output directory
mkdir -p ${NAME}

# Run MCMC with GPU (single-process)
echo "Step 1: Running MCMC sampling on GPU (single-process)..."
echo "Started at: $(date)"

# Use the GPU-optimized config
pyorbit_run emcee ${NAME}.yaml > ./${NAME}/${NAME}.log 2>&1

# Check if first run was successful
if [ $? -eq 0 ]; then
  echo "✅ First MCMC run completed successfully"
  # Continue with second run
  pyorbit_run emcee ${NAME}.yaml >> ./${NAME}/${NAME}.log 2>&1
  
  if [ $? -eq 0 ]; then
      echo "✅ Second MCMC run completed successfully"
  else
      echo "❌ Second MCMC run failed"
  fi
else
  echo "❌ First MCMC run failed - checking log..."
  echo "Last 20 lines of log:"
  tail -20 ./${NAME}/${NAME}.log
fi

echo "MCMC completed at: $(date)"
echo ""

echo "Step 2: Generating results..."
pyorbit_results emcee ${NAME}.yaml -all >> ./${NAME}/${NAME}.log 2>&1

if [ $? -eq 0 ]; then
  echo "✅ Results generation completed successfully"
else
  echo "❌ Results generation failed"
fi

echo "Step 3: Copying configuration..."
cp ${NAME}.yaml ./${NAME}/

echo ""
echo "=== PyORBIT GPU Analysis Completed ==="
echo "End time: $(date)"

# Final GPU status
echo "=== Final GPU Status ==="
nvidia-smi

echo ""
echo "=== Resource Usage Summary ==="
echo "Job ID: $LSB_JOBID"
echo "Queue: $LSB_QUEUE"
echo "Cores used: $LSB_DJOB_NUMPROC"
echo "Host: $LSB_HOSTS"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)"
echo "Mode: Single-process GPU"