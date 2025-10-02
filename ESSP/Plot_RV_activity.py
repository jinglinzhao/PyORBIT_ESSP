#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib
import pickle
import collections
import os
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator

# Set up matplotlib for interactive widgets if needed
# %matplotlib widget

class RVPlotter:
    """Class for plotting radial velocity and stellar activity data."""
    
    def __init__(self, base_dir='./', model_dir='HD189567_3p_run7/', filename='HD189567_3p_run7'):
        """Initialize the plotter with directory paths and configuration."""
        self.dir_base = base_dir
        self.dir_mods = model_dir
        self.dir_plot = 'emcee_plot/model_files/'
        self.filename = filename
        
        # Load data
        self._load_data()
        
        # Configuration
        self._setup_configuration()
        
        # Plot settings
        self.font_label = 12
        self.dot_size = 18
        self.figsize = (10, 7)
        self._setup_matplotlib()
    
    def _load_data(self):
        """Load pickle files with parameter summaries."""
        param_path = f"{self.dir_base}{self.dir_mods}emcee_plot/dictionaries/summary_percentiles_parameters.p"
        derived_path = f"{self.dir_base}{self.dir_mods}emcee_plot/dictionaries/summary_percentiles_derived.p"
        
        self.summary_percentiles_parameters = pickle.load(open(param_path, 'rb'))
        self.summary_percentiles_derived = pickle.load(open(derived_path, 'rb'))
    
    def _setup_configuration(self):
        """Set up datasets, activity models, and planet configurations."""
        # Dataset configuration
        # self.datasets_list = ['RVdata']
        self.datasets_list = ['ESSP_HARPSN', 'ESSP_EXPRES', 'ESSP_NEID', 'ESSP_HARPS']
        self.datasets_labels = {'ESSP_HARPSN': 'HARPSN', 'ESSP_EXPRES': 'EXPRES', 'ESSP_NEID': 'NEID', 'ESSP_HARPS': 'HARPS'}
        
        # Activity configuration
        self.activity_model = 'gp_multidimensional'
        self.activity_list = ['BIS']  # Only BIS data is available
        self.activity_labels = {
            'BIS': 'BIS',
        }
        
        # Planet configuration
        self.planet_dict = self._create_planet_dict()
        
        # Activity and full dictionary configuration
        self.activity_dict = {
            'limits_full_x': [-0.25, 1.25],
            'limits_bjd': [59332., 59360],
            'limits_full_y': [-13.5, 13.5],
            'limits_residuals_y': [-11.5, 11.5],
        }
        
        self.full_dict = {
            'reference_planet': 'b',
            'limits_full_x': [-0.25, 1.25],
            'limits_bjd': [59332., 59360],
        }
    
    def _create_planet_dict(self):
        """Create planet configuration dictionary for all available planets."""
        planet_dict = collections.OrderedDict()
        # Instead of hardcoding ['b', 'c'], use all planet keys in the parameter summary
        for planet_name in self.summary_percentiles_parameters.keys():
            # Only add if it has the required keys
            if 'P' in self.summary_percentiles_parameters[planet_name] and 'K' in self.summary_percentiles_parameters[planet_name]:
                planet_dict[planet_name] = {
                    'P': self.summary_percentiles_parameters[planet_name]['P'][3],  # Median value
                    'limits_folded_x': [-0.25, 1.25],
                    'transit_folded': False,
                    'K_error_1sigma': self._calculate_k_error(planet_name, 1),
                    'K_error_2sigma': self._calculate_k_error(planet_name, 2),
                    'K_error_3sigma': self._calculate_k_error(planet_name, 3),
                }
        return planet_dict
    
    def _calculate_k_error(self, planet_name, sigma_level):
        """Calculate K error for given sigma level."""
        k_params = self.summary_percentiles_parameters[planet_name]['K']
        if sigma_level == 1:
            return (k_params[4] - k_params[2]) / 2
        elif sigma_level == 2:
            return (k_params[5] - k_params[1]) / 2
        elif sigma_level == 3:
            return (k_params[6] - k_params[0]) / 2
    
    def _setup_matplotlib(self):
        """Configure matplotlib settings."""
        plt.rcParams['font.family'] = 'DeJavu Serif'
        plt.rcParams['font.serif'] = ['Times New Roman']
        matplotlib.rcParams.update({'font.size': self.font_label})
    
    def _create_grid_plots(self):
        """Create grid layout for plots."""
        gs = gridspec.GridSpec(2, 1, height_ratios=[3.0, 1.0])
        gs.update(left=0.2, right=0.95, bottom=0.08, top=0.93, wspace=0.02, hspace=0.03)
        
        ax_0 = plt.subplot(gs[0])
        ax_1 = plt.subplot(gs[1])
        
        # Add minor ticks
        minor_locator = AutoMinorLocator()
        ax_0.xaxis.set_minor_locator(minor_locator)
        ax_1.xaxis.set_minor_locator(minor_locator)
        
        # Disable offset
        ax_0.ticklabel_format(useOffset=False, style='plain')
        ax_1.ticklabel_format(useOffset=False, style='plain')
        
        return ax_0, ax_1
    
    def _load_rv_data(self, planet_name):
        """Load RV data for a specific planet."""
        kep_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}RV_planet_{planet_name}_kep.dat"
        
        if self.planet_dict[planet_name].get('transit_folded', True):
            phase_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}RV_planet_{planet_name}_Tcf.dat"
        else:
            phase_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}RV_planet_{planet_name}_pha.dat"
        
        rv_kep = np.genfromtxt(kep_file, skip_header=1)
        rv_pha = np.genfromtxt(phase_file, skip_header=1)
        
        return rv_kep, rv_pha
    
    def _plot_error_bands(self, ax, rv_pha, planet_config):
        """Plot error bands for K uncertainty."""
        k_rvs = np.amax(rv_pha[:, 1])
        rv_unitary = rv_pha[:, 1] / k_rvs
        
        for sigma, error_key in [(1, 'K_error_1sigma'), (2, 'K_error_2sigma'), (3, 'K_error_3sigma')]:
            k_error = planet_config[error_key]
            ax.fill_between(rv_pha[:, 0], 
                          rv_unitary * (k_rvs - k_error), 
                          rv_unitary * (k_rvs + k_error), 
                          alpha=0.10, color='black', zorder=0)
    
    def _plot_phase_lines(self, ax_0, ax_1, planet_config):
        """Plot phase reference lines."""
        if planet_config.get('transit_folded', False):
            for ax in [ax_0, ax_1]:
                ax.axvline(-0.500, c='k', zorder=3, alpha=0.5, linestyle='--')
                ax.axvline(0.500, c='k', zorder=3, alpha=0.5, linestyle='--')
        else:
            for ax in [ax_0, ax_1]:
                ax.axvline(0.00, c='k', zorder=3, alpha=0.5, linestyle='--')
                ax.axvline(1.00, c='k', zorder=3, alpha=0.5, linestyle='--')
    
    def plot_folded_rv(self):
        """Create folded RV plots for each planet."""
        n_color = 0
        
        for planet_name, planet_config in self.planet_dict.items():
            print(f"Creating folded plot for planet {planet_name}")
            
            # Load data
            rv_kep, rv_pha = self._load_rv_data(planet_name)
            
            # Create figure
            fig = plt.figure(figsize=self.figsize)
            ax_0, ax_1 = self._create_grid_plots()
            
            # Plot error bands
            self._plot_error_bands(ax_0, rv_pha, planet_config)
            
            # Plot model
            ax_0.plot(rv_pha[:, 0] - 1, rv_pha[:, 1], color='k', linestyle='-', zorder=2, label='RV model')
            ax_0.plot(rv_pha[:, 0] + 1, rv_pha[:, 1], color='k', linestyle='-', zorder=2)
            
            # Plot data for each dataset
            default_color = f'C{n_color}'
            n_color += 1
            
            for n_dataset, dataset in enumerate(self.datasets_list):
                self._plot_dataset_rv(ax_0, ax_1, dataset, planet_name, default_color, n_dataset)
            
            # Plot residual reference line and error bands
            ax_1.axhline(0.000, c='k', zorder=3)
            for error_key in ['K_error_1sigma', 'K_error_2sigma', 'K_error_3sigma']:
                k_error = planet_config[error_key]
                ax_1.fill_between(rv_pha[:, 0], -k_error, k_error, alpha=0.10, color='black', zorder=0)
            
            # Set limits and formatting
            self._format_folded_plot(ax_0, ax_1, planet_config)
            
            # Plot phase lines
            self._plot_phase_lines(ax_0, ax_1, planet_config)
            
            # Save plot
            plot_filename = f"{self.filename}_{planet_name}_folded.png"
            print(f"Folded plot for planet {planet_name} saved to: {plot_filename}")
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_dataset_rv(self, ax_0, ax_1, dataset, planet_name, color, n_dataset):
        """Plot RV data for a specific dataset."""
        rv_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}{dataset}_radial_velocities_{planet_name}.dat"
        rv_mod = np.genfromtxt(rv_file, skip_header=1)
        
        error = np.sqrt(rv_mod[:, 9]**2 + rv_mod[:, 12]**2)
        
        if self.planet_dict[planet_name].get('transit_folded', False):
            rv_phase = rv_mod[:, 1] / self.planet_dict[planet_name]['P']
        else:
            rv_phase = rv_mod[:, 2]
        
        # Plot main data
        ax_0.errorbar(rv_phase, rv_mod[:, 8], yerr=error, color='black', markersize=0, alpha=0.25, fmt='o', zorder=0)
        ax_0.scatter(rv_phase, rv_mod[:, 8], c=color, s=self.dot_size, zorder=20-n_dataset, alpha=1.0, 
                    label=self.datasets_labels[dataset])
        
        # Plot phase-shifted data
        for phase_shift, alpha_val in [(-1, 1.0), (1, 1.0)]:
            ax_0.errorbar(rv_phase + phase_shift, rv_mod[:, 8], yerr=error, color='black', markersize=0, alpha=0.25, fmt='o', zorder=0)
            ax_0.scatter(rv_phase + phase_shift, rv_mod[:, 8], c='gray', s=self.dot_size, zorder=20, alpha=alpha_val)
        
        # Plot residuals
        ax_1.errorbar(rv_phase, rv_mod[:, 10], yerr=error, color='black', markersize=0, alpha=0.25, fmt='o', zorder=1)
        ax_1.scatter(rv_phase, rv_mod[:, 10], c=color, s=self.dot_size, zorder=20-n_dataset, alpha=1.0)
        
        # Plot phase-shifted residuals
        for phase_shift in [-1, 1]:
            ax_1.errorbar(rv_phase + phase_shift, rv_mod[:, 10], yerr=error, color='black', markersize=0, alpha=0.25, fmt='o', zorder=1)
            ax_1.scatter(rv_phase + phase_shift, rv_mod[:, 10], c='gray', s=self.dot_size, zorder=20, alpha=1.0)
    
    def _format_folded_plot(self, ax_0, ax_1, planet_config):
        """Format the folded plot axes."""
        # Set limits
        if planet_config.get('limits_folded_x'):
            ax_0.set_xlim(planet_config['limits_folded_x'])
            ax_1.set_xlim(planet_config['limits_folded_x'])
        if planet_config.get('limits_folded_y'):
            ax_0.set_ylim(planet_config['limits_folded_y'])
        if planet_config.get('limits_residuals_y'):
            ax_1.set_ylim(planet_config['limits_residuals_y'])
        
        # Remove x-axis ticks from top plot
        ax_0.axes.get_xaxis().set_ticks([])
        
        # Set tick formatting
        for ax in [ax_0, ax_1]:
            ax.yaxis.set_major_locator(MultipleLocator(5))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
            ax.yaxis.set_minor_locator(MultipleLocator(1))
        
        # Set labels
        ax_0.set_ylabel('RV [m/s]')
        ax_1.set_xlabel('Orbital Phase')
        ax_1.set_ylabel('Residuals [m/s]')
        
        # Add legend
        ax_0.legend(framealpha=1.0, loc='lower left')
    
    def plot_full_model(self):
        """Create full model plot."""
        print("Creating full model plot")
        
        fig = plt.figure(figsize=self.figsize)
        ax_0, ax_1 = self._create_grid_plots()
        
        # Plot model
        # rv_full_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}RVdata_full.dat"
        rv_full_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}{self.datasets_list[0]}_full.dat"
        rv_full = np.genfromtxt(rv_full_file, skip_header=1)
        ax_0.plot(rv_full[:, 0] - 2450000, rv_full[:, 1], color='k', linestyle='-', zorder=2, label='RV model', lw=0.1)
        
        # Plot datasets
        for n_dataset, dataset in enumerate(self.datasets_list):
            # Plot for all available planets
            for planet_name in self.planet_dict.keys():
                self._plot_dataset_full(ax_0, ax_1, dataset, n_dataset, planet_name)
        
        # Format plot
        self._format_full_plot(ax_0, ax_1)
        
        # Save plot
        plot_filename = f"{self.filename}_full_model.png"
        print(f"Full model plot saved to: {plot_filename}")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_dataset_full(self, ax_0, ax_1, dataset, n_dataset, planet_name):
        """Plot dataset for full model for a given planet."""
        rv_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}{dataset}_radial_velocities_{planet_name}.dat"
        try:
            rv_mod = np.genfromtxt(rv_file, skip_header=1)
        except OSError:
            print(f"Warning: File {rv_file} not found. Skipping planet {planet_name} for dataset {dataset}.")
            return
        if rv_mod.size == 0:
            print(f"Warning: File {rv_file} is empty. Skipping planet {planet_name} for dataset {dataset}.")
            return
        error = np.sqrt(rv_mod[:, 9]**2 + rv_mod[:, 12]**2)
        
        color = f'C{n_dataset}'
        
        # Plot data
        ax_0.errorbar(rv_mod[:, 0] - 2450000, rv_mod[:, 7] - rv_mod[:, 5], yerr=error, 
                     color='black', markersize=0, alpha=0.25, fmt='o', zorder=0)
        ax_0.scatter(rv_mod[:, 0] - 2450000, rv_mod[:, 7] - rv_mod[:, 5], c=color, s=self.dot_size, 
                    zorder=20-n_dataset, alpha=1.0, label=f"{self.datasets_labels[dataset]} ({planet_name})")
        
        # Plot residuals
        ax_1.errorbar(rv_mod[:, 0] - 2450000, rv_mod[:, 10], yerr=error, 
                     color='black', markersize=0, alpha=0.25, fmt='o', zorder=1)
        ax_1.scatter(rv_mod[:, 0] - 2450000, rv_mod[:, 10], c=color, s=self.dot_size, 
                    zorder=20-n_dataset, alpha=1.0)
    
    def _format_full_plot(self, ax_0, ax_1):
        """Format the full model plot."""
        ax_1.axhline(0.000, c='k', zorder=3)
        
        # Set limits
        bjd_limits = [x - 2450000 for x in self.full_dict['limits_bjd']]
        ax_0.set_xlim(bjd_limits)
        ax_1.set_xlim(bjd_limits)
        
        if self.full_dict.get('limits_full_y'):
            ax_0.set_ylim(self.full_dict['limits_full_y'])
        if self.full_dict.get('limits_residuals_y'):
            ax_1.set_ylim(self.full_dict['limits_residuals_y'])
        
        # Format axes
        ax_0.axes.get_xaxis().set_ticks([])
        
        for ax in [ax_0, ax_1]:
            ax.yaxis.set_major_locator(MultipleLocator(5))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
            ax.yaxis.set_minor_locator(MultipleLocator(1))
        
        # Set labels
        ax_0.set_ylabel('RV [m/s]')
        ax_1.set_xlabel('Time [BJD-2450000]')
        ax_1.set_ylabel('Residuals [m/s]')
        
        ax_0.legend(framealpha=1.0, loc='lower left')
    
    def plot_activity_rv(self):
        """Create activity RV model plot."""
        print("Creating activity RV model plot")
        
        fig = plt.figure(figsize=self.figsize)
        ax_0, ax_1 = self._create_grid_plots()
        
        # Plot activity model
        activity_full_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}{self.datasets_list[0]}_{self.activity_model}_full.dat"
        activity_full = np.genfromtxt(activity_full_file, skip_header=1)
        ax_0.plot(activity_full[:, 0] - 2450000.0, activity_full[:, 3], color='k', linestyle='-', 
                 zorder=2, label='Activity model', lw=1)
        
        # Plot datasets
        for n_dataset, dataset in enumerate(self.datasets_list):
            self._plot_activity_dataset(ax_0, ax_1, dataset, n_dataset)
        
        # Format plot
        self._format_activity_plot(ax_0, ax_1, 'RV')
        
        # Save plot
        plot_filename = f"{self.filename}_activity_RV_model.png"
        print(f"Activity RV model plot saved to: {plot_filename}")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_activity_dataset(self, ax_0, ax_1, dataset, n_dataset):
        """Plot activity dataset."""
        activity_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}{dataset}_{self.activity_model}.dat"
        activity_mod = np.genfromtxt(activity_file, skip_header=1)
        error = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)
        
        color = f'C{n_dataset}'
        
        # Plot data
        ax_0.errorbar(activity_mod[:, 0] - 2450000.0, activity_mod[:, 8], yerr=error, 
                     color='black', markersize=0, alpha=0.25, fmt='o', zorder=0)
        ax_0.scatter(activity_mod[:, 0] - 2450000.0, activity_mod[:, 8], c=color, s=self.dot_size, 
                    zorder=20-n_dataset, alpha=1.0, label=self.datasets_labels[dataset])
        
        # Plot residuals
        ax_1.errorbar(activity_mod[:, 0] - 2450000.0, activity_mod[:, 10], yerr=error, 
                     color='black', markersize=0, alpha=0.25, fmt='o', zorder=1)
        ax_1.scatter(activity_mod[:, 0] - 2450000.0, activity_mod[:, 10], c=color, s=self.dot_size, 
                    zorder=20-n_dataset, alpha=1.0)
    
    def plot_individual_activity(self):
        """Create individual activity plots."""
        for n_dataset, dataset in enumerate(self.activity_list):
            print(f"Creating activity plot for {dataset}")
            
            # Check if we have activity data for any of the datasets
            activity_data_found = False
            for instrument in ['HARPSN', 'EXPRES', 'NEID', 'HARPS']:
                activity_full_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}ESSP_{dataset}_{instrument}_{self.activity_model}_full.dat"
                activity_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}ESSP_{dataset}_{instrument}_{self.activity_model}.dat"
                
                if os.path.exists(activity_full_file) and os.path.exists(activity_file):
                    activity_data_found = True
                    break
            
            if not activity_data_found:
                print(f"Warning: No activity data files found for {dataset}. Skipping...")
                continue
            
            fig = plt.figure(figsize=self.figsize)
            ax_0, ax_1 = self._create_grid_plots()
            
            # Plot data for each instrument that has activity data
            for n_instrument, instrument in enumerate(['HARPSN', 'EXPRES', 'NEID', 'HARPS']):
                activity_full_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}ESSP_{dataset}_{instrument}_{self.activity_model}_full.dat"
                activity_file = f"{self.dir_base}{self.dir_mods}{self.dir_plot}ESSP_{dataset}_{instrument}_{self.activity_model}.dat"
                
                if not (os.path.exists(activity_full_file) and os.path.exists(activity_file)):
                    continue
                
                try:
                    # Plot activity model
                    activity_full = np.genfromtxt(activity_full_file, skip_header=1)
                    ax_0.plot(activity_full[:, 0], activity_full[:, 3], color='k', linestyle='-', 
                             zorder=2, label='Activity model' if n_instrument == 0 else '', lw=0.1)
                    
                    # Plot data
                    activity_mod = np.genfromtxt(activity_file, skip_header=1)
                    if activity_mod.size == 0:
                        continue
                        
                    error = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)
                    color = f'C{n_instrument}'
                    
                    ax_0.errorbar(activity_mod[:, 0], activity_mod[:, 8], yerr=error, 
                                 color='black', markersize=0, alpha=0.25, fmt='o', zorder=0)
                    ax_0.scatter(activity_mod[:, 0], activity_mod[:, 8], c=color, s=self.dot_size, 
                                zorder=20-n_instrument, alpha=1.0, label=instrument)
                    
                    # Plot residuals
                    ax_1.errorbar(activity_mod[:, 0], activity_mod[:, 10], yerr=error, 
                                 color='black', markersize=0, alpha=0.25, fmt='o', zorder=1)
                    ax_1.scatter(activity_mod[:, 0], activity_mod[:, 10], c=color, s=self.dot_size, 
                                zorder=20-n_instrument, alpha=1.0)
                    
                except (OSError, ValueError) as e:
                    print(f"Warning: Error reading {dataset} data for {instrument}: {e}")
                    continue
            
            ax_1.axhline(0.000, c='k', zorder=3)
            
            # Set dynamic limits based on all plotted data
            all_data = []
            all_residuals = []
            for ax in ax_0.collections + ax_0.lines:
                if hasattr(ax, 'get_offsets'):
                    data = ax.get_offsets()
                    if len(data) > 0:
                        all_data.extend(data[:, 1])
            for ax in ax_1.collections + ax_1.lines:
                if hasattr(ax, 'get_offsets'):
                    data = ax.get_offsets()
                    if len(data) > 0:
                        all_residuals.extend(data[:, 1])
            
            if all_data:
                val_min, val_max = min(all_data), max(all_data)
                ax_0.set_ylim(val_min - np.abs(val_min) * 0.05, val_max + np.abs(val_max) * 0.05)
            
            if all_residuals:
                res_min, res_max = min(all_residuals), max(all_residuals)
                ax_1.set_ylim(res_min - np.abs(res_min) * 0.05, res_max + np.abs(res_max) * 0.05)
            
            ax_0.set_xlim(self.activity_dict['limits_bjd'])
            ax_1.set_xlim(self.activity_dict['limits_bjd'])
            
            # Format plot
            ax_0.axes.get_xaxis().set_ticks([])
            ax_0.set_ylabel('Activity index')
            ax_1.set_xlabel('Time [BJD-2450000]')
            ax_1.set_ylabel('Residuals')
            
            ax_0.legend(framealpha=1.0, loc='lower left')
            
            # Save plot
            plot_filename = f"{self.filename}_activity_{dataset}.png"
            print(f"Activity plot for {dataset} saved to: {plot_filename}")
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _format_activity_plot(self, ax_0, ax_1, plot_type):
        """Format activity plots."""
        ax_1.axhline(0.000, c='k', zorder=3)
        
        # Set limits
        bjd_limits = [x - 2450000 for x in self.activity_dict['limits_bjd']]
        ax_0.set_xlim(bjd_limits)
        ax_1.set_xlim(bjd_limits)
        
        if self.activity_dict.get('limits_full_y'):
            ax_0.set_ylim(self.activity_dict['limits_full_y'])
        if self.activity_dict.get('limits_residuals_y'):
            ax_1.set_ylim(self.activity_dict['limits_residuals_y'])
        
        # Format axes
        ax_0.axes.get_xaxis().set_ticks([])
        
        for ax in [ax_0, ax_1]:
            ax.yaxis.set_major_locator(MultipleLocator(5))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
            ax.yaxis.set_minor_locator(MultipleLocator(1))
        
        # Set labels
        ylabel = 'RV [m/s]' if plot_type == 'RV' else 'Activity index'
        ax_0.set_ylabel(ylabel)
        ax_1.set_xlabel('Time [BJD-2450000]')
        ax_1.set_ylabel('Residuals [m/s]')
        
        ax_0.legend(framealpha=1.0, loc='lower left')
    
    def create_all_plots(self):
        """Create all plots."""
        print("Creating all plots...")
        self.plot_folded_rv()
        self.plot_full_model()
        self.plot_activity_rv()
        self.plot_individual_activity()
        print("All plots completed!")


# Usage example:
if __name__ == "__main__":
    # Initialize the plotter
    plotter = RVPlotter(
        base_dir='./',
        model_dir='ESSP_gp_HARPSN_EXPRES_NEID_HARPS_poly_cpu/',
        filename='ESSP_gp_HARPSN_EXPRES_NEID_HARPS_poly_cpu'
    )
    
    # Create all plots
    plotter.create_all_plots()
    
    # Or create individual plot types:
    # plotter.plot_folded_rv()
    # plotter.plot_full_model()
    # plotter.plot_activity_rv()
    # plotter.plot_individual_activity()
