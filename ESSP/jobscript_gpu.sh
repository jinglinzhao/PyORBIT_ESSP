#!/bin/sh
### General options
### -- specify GPU queue (choose based on your needs) --
#BSUB -q gpuv100
### -- set the job Name --
#BSUB -J PyORBIT_ESSP_GPU
### -- ask for number of cores (4 cores per GPU is recommended) --
#BSUB -n 10
### -- Select the resources: 1 GPU in exclusive process mode --
#BSUB -gpu "num=1:mode=exclusive_process"
### -- specify that the cores must be on the same host --
#BSUB -R "span[hosts=1]"
### -- request memory (5GB is recommended for GPU jobs) --
#BSUB -R "rusage[mem=5GB]"
### -- set memory limit --
#BSUB -M 5GB
### -- set walltime limit (max 24 hours for GPU queues) --
#BSUB -W 1:30
### -- set the email address --
#BSUB -u jzhao@space.dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion --
#BSUB -N
### -- Specify the output and error file --
#BSUB -o /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Output_ESSP_poly_GPU_%J.out
#BSUB -e /work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/logfiles/Error_ESSP_poly_GPU_%J.err

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

# Load CUDA module (if needed)
echo "=== Loading CUDA Module ==="
module load cuda/12.1
module load cudnn/v8.9.7.29-prod-cuda-12.X
echo "CUDA loaded: $(which nvcc)"
echo ""

# Activate Conda environment
echo "=== Activating PyORBIT Environment ==="
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit_gpu

echo "Active environment: $CONDA_DEFAULT_ENV"
echo "Python version: $(python --version)"

# Check JAX GPU setup
echo "=== JAX GPU Check ==="
python -c "
try:
    import jax
    print(f'JAX version: {jax.__version__}')
    print(f'JAX backend: {jax.default_backend()}')
    devices = jax.devices()
    print(f'Available devices: {len(devices)}')
    for i, device in enumerate(devices):
        print(f'  Device {i}: {device}')
    
    # Test GPU computation
    if jax.default_backend() == 'gpu':
        import jax.numpy as jnp
        x = jnp.ones((1000, 1000))
        y = jnp.dot(x, x)
        print(f'✅ GPU test successful: computed {y.shape} matrix')
    else:
        print('⚠️  Running on CPU backend')
        
except Exception as e:
    print(f'❌ JAX error: {e}')
"
echo ""

# Set JAX GPU memory allocation (prevent OOM)
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.8
export XLA_PYTHON_CLIENT_PREALLOCATE=false

# Run PyORBIT analysis
instrument="HARPSN_EXPRES_NEID_HARPS_poly"
NAME="ESSP_gp_${instrument}"

echo "=== Starting PyORBIT GPU Analysis ==="
echo "Analysis name: ${NAME}"
echo "Working directory: $(pwd)"
echo "GPU memory fraction: $XLA_PYTHON_CLIENT_MEM_FRACTION"
echo ""

# Create output directory
mkdir -p ${NAME}

# Run MCMC with GPU acceleration
echo "Step 1: Running MCMC sampling on GPU..."
echo "Started at: $(date)"
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
    echo "❌ First MCMC run failed"
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