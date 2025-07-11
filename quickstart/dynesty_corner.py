import pickle
import corner
import numpy as np
import matplotlib.pyplot as plt
import os

# Create output directory if it doesn't exist
os.makedirs('plots', exist_ok=True)

# Load the results
with open('HD189567_HARPS/dynesty/results.p', 'rb') as f:
    results = pickle.load(f)

# Load the model container
with open('HD189567_HARPS/dynesty/model_container.p', 'rb') as f:
    mc = pickle.load(f)

# Print available attributes in results
print("Available attributes in results:", dir(results))

# Extract samples from dynesty results
samples = results.samples

# Calculate weights from logwt
logwt = results.logwt
weights = np.exp(logwt - logwt.max())
weights /= weights.sum()

# Try to get parameter names from model container
try:
    param_names = mc.pam_names
    print(f"Found {len(param_names)} parameters from model container: {param_names}")
except:
    print("Could not get parameter names from model container")
    param_names = []

# If parameter names are empty, create generic names
if not param_names:
    param_names = [f"param_{i}" for i in range(samples.shape[1])]
    print(f"Created generic parameter names: {param_names}")

print(f"Using {len(param_names)} parameters: {param_names}")
print(f"Samples shape: {samples.shape}")

# Create weighted corner plot
fig = corner.corner(
    samples,
    weights=weights,
    labels=param_names,
    quantiles=[0.16, 0.5, 0.84],
    show_titles=True,
    title_fmt=".3f"
)

plt.savefig('plots/HD189567_dynesty_corner.png', dpi=300, bbox_inches='tight')
print("Corner plot saved as plots/HD189567_dynesty_corner.png")

# Function to calculate weighted quantiles
def weighted_quantile(values, quantiles, weights=None):
    """
    Compute weighted quantiles.
    
    Parameters:
    -----------
    values : array-like
        Data array
    quantiles : array-like
        Quantiles to compute (0.0 to 1.0)
    weights : array-like, optional
        Array of weights. If None, uniform weights are used.
        
    Returns:
    --------
    quantiles : array
        Computed quantiles
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    
    if weights is None:
        weights = np.ones(len(values))
    weights = np.array(weights)
    
    # Sort the data
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    
    # Compute the cumulative sum of weights
    cum_weights = np.cumsum(weights)
    
    # Normalize the weights
    cum_weights = cum_weights / cum_weights[-1]
    
    # Find the quantiles
    result = np.interp(quantiles, cum_weights, values)
    
    return result

# Also create individual parameter histograms for better visibility
os.makedirs('plots/histograms', exist_ok=True)

for i, name in enumerate(param_names):
    plt.figure(figsize=(8, 6))
    plt.hist(samples[:, i], weights=weights, bins=50, alpha=0.7)
    plt.xlabel(name)
    plt.ylabel('Probability')
    
    # Calculate weighted percentiles
    q16, q50, q84 = weighted_quantile(samples[:, i], [0.16, 0.5, 0.84], weights=weights)
    
    plt.axvline(q50, color='r', linestyle='-', label=f'Median: {q50:.4f}')
    plt.axvline(q16, color='r', linestyle='--', label=f'16%: {q16:.4f}')
    plt.axvline(q84, color='r', linestyle='--', label=f'84%: {q84:.4f}')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'plots/histograms/{name}_histogram.png', dpi=200)
    plt.close()

print("Individual parameter histograms saved in plots/histograms/")

# Let's also try to inspect the model container to understand its structure
print("\nExploring model container structure:")
print("Model container attributes:", dir(mc))

# Try to access some common attributes that might contain parameter information
try:
    print("\nModel container type:", type(mc))
    
    if hasattr(mc, 'models'):
        print("Models:", mc.models)
    
    if hasattr(mc, 'planets'):
        print("Planets:", mc.planets)
    
    if hasattr(mc, 'dataset_dict'):
        print("Datasets:", list(mc.dataset_dict.keys()))
    
    # Try to find parameter names by exploring the model structure
    if hasattr(mc, 'bounds'):
        print("Bounds:", mc.bounds)
        
    if hasattr(mc, 'variables'):
        print("Variables:", mc.variables)
        
except Exception as e:
    print(f"Error exploring model container: {e}")
