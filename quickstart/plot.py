import pickle
import corner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Define paths for the model
model_path = "HD189567_HARPS/emcee/"

# Function to create corner plots
def create_corner_plot(model_path, burnin=11683, thin=200, output_name="corner_plot.png"):
    # Load the sampler chain
    with open(f"{model_path}sampler_chain.p", "rb") as f:
        chain = pickle.load(f)
    
    # Load parameter names
    with open(f"{model_path}theta_dict.p", "rb") as f:
        theta_dict = pickle.load(f)
    
    # Get parameter names
    param_names = list(theta_dict.keys())
    
    # Print chain shape to debug
    print(f"Original chain shape: {chain.shape}")
    
    # Apply burnin and thinning
    chain_burned = chain[:, burnin:, :]
    print(f"After burnin, chain shape: {chain_burned.shape}")
    
    # Properly reshape the chain - flatten walkers and steps
    samples = chain_burned.reshape(-1, chain_burned.shape[2])
    print(f"Reshaped samples shape: {samples.shape}")
    
    # Make sure we have more samples than dimensions
    if samples.shape[0] <= samples.shape[1]:
        raise ValueError(f"Not enough samples ({samples.shape[0]}) compared to dimensions ({samples.shape[1]})")
    
    # Create corner plot
    fig = corner.corner(
        samples,
        labels=param_names,
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        title_fmt=".3f"
    )
    
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return samples, param_names

# Alternative approach using posteriors file
def create_corner_from_posteriors(model_path, output_name="corner_from_posteriors.png"):
    # Load the posteriors
    try:
        with open(f"{model_path}sampler_posteriors.p", "rb") as f:
            posteriors = pickle.load(f)
        
        # Load parameter names
        with open(f"{model_path}theta_dict.p", "rb") as f:
            theta_dict = pickle.load(f)
        
        param_names = list(theta_dict.keys())
        
        # Extract samples from posteriors
        samples = np.array([posteriors[param] for param in param_names]).T
        print(f"Posteriors samples shape: {samples.shape}")
        
        # Create corner plot
        fig = corner.corner(
            samples,
            labels=param_names,
            quantiles=[0.16, 0.5, 0.84],
            show_titles=True,
            title_fmt=".3f"
        )
        
        plt.savefig(output_name, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return samples, param_names
    except FileNotFoundError:
        print(f"Could not find posteriors file at {model_path}sampler_posteriors.p")
        return None, None

# Try both methods
try:
    samples1, params1 = create_corner_plot(model_path, burnin=11683, output_name="corner_from_chain.png")
    print("Successfully created corner plot from chain")
except Exception as e:
    print(f"Error creating corner plot from chain: {e}")

try:
    samples2, params2 = create_corner_from_posteriors(model_path, output_name="corner_from_posteriors.png")
    print("Successfully created corner plot from posteriors")
except Exception as e:
    print(f"Error creating corner plot from posteriors: {e}")

# If both methods fail, try a more direct approach with explicit thinning
def create_simple_corner(model_path, burnin=11683, thin=10, output_name="simple_corner.png"):
    # Load the sampler chain
    with open(f"{model_path}sampler_chain.p", "rb") as f:
        chain = pickle.load(f)
    
    # Load parameter names
    with open(f"{model_path}theta_dict.p", "rb") as f:
        theta_dict = pickle.load(f)
    
    param_names = list(theta_dict.keys())
    
    # Get chain dimensions
    nwalkers, nsteps, ndim = chain.shape
    print(f"Chain dimensions: {nwalkers} walkers, {nsteps} steps, {ndim} parameters")
    
    # Apply burnin
    if burnin >= nsteps:
        burnin = int(nsteps * 0.5)  # Use 50% as burnin if specified burnin is too large
        print(f"Burnin too large, using {burnin} instead")
    
    # Apply explicit thinning to ensure we have manageable number of samples
    flat_samples = []
    for i in range(nwalkers):
        for j in range(burnin, nsteps, thin):
            flat_samples.append(chain[i, j, :])
    
    flat_samples = np.array(flat_samples)
    print(f"Final samples shape: {flat_samples.shape}")
    
    # Create corner plot
    fig = corner.corner(
        flat_samples,
        labels=param_names,
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        title_fmt=".3f"
    )
    
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return flat_samples, param_names

# Try the simple approach as a fallback
try:
    samples3, params3 = create_simple_corner(model_path, burnin=11683, thin=10, output_name="simple_corner.png")
    print("Successfully created simple corner plot")
except Exception as e:
    print(f"Error creating simple corner plot: {e}")
