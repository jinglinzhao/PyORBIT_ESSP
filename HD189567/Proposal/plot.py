import numpy as np
%matplotlib widget
import matplotlib.pyplot as plt
import collections
import matplotlib.gridspec as gridspec # GRIDSPEC !
import collections
import matplotlib
import pickle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def plots_in_grid():
    # Partially taken from here:
    # http://www.sc.eso.org/~bdias/pycoffee/codes/20160407/gridspec_demo.html
    
    gs = gridspec.GridSpec(2,1, height_ratios=[3.0,1.0])
    # Also make sure the margins and spacing are apropriate
    gs.update(left=0.2, right=0.95, bottom=0.08, top=0.93, wspace=0.02, hspace=0.03)
    
    
    ax_0 = plt.subplot(gs[0])
    ax_1 = plt.subplot(gs[1])

    # Adding minor ticks only to x axis
    from matplotlib.ticker import AutoMinorLocator
    minorLocator = AutoMinorLocator()
    ax_0.xaxis.set_minor_locator(minorLocator)
    ax_1.xaxis.set_minor_locator(minorLocator)

    # Disabling the offset on top of the plot
    ax_0.ticklabel_format(useOffset=False, style='plain')
    ax_1.ticklabel_format(useOffset=False, style='plain')
    return ax_0, ax_1

    
dir_base = './'
dir_mods = 'HD189567_2p_1/'
dir_plot = 'plot'
filename = 'HD189567_2p_1'

summary_percentiles_parameters = pickle.load(open(dir_base + dir_mods + 'emcee_plot/dictionaries/summary_percentiles_parameters.p', 'rb'))
summary_percentiles_derived = pickle.load(open(dir_base + dir_mods + 'emcee_plot/dictionaries/summary_percentiles_derived.p', 'rb'))


# Comment/uncomment according to the number of datasets and their names
#datasets_list = ['RVdata_dataset1', 'RVdata_dataset2'] 
datasets_list = ['RV_data_1', 'RV_data_2', 'RV_data_3']
datasets_labels = {'RV_data_1':'HARPS-N_1', 'RV_data_2':'HARPS-N_2', 'RV_data_3':'ESPRESSO'}

# Comment/uncomment according to the models listed in your configuration files
activity_model = 'gp_multidimensional'

activity_list = ['BIS', 'FWHM']
activity_labels = {'BIS':'BIS',
                  'FWHM':'FWHM',
                  }

# Comment/uncomment and change according to the parameters of the best fit 
# from the RV analysis
planet_dict = collections.OrderedDict()
planet_name = 'b'
planet_dict['b'] =  {
    'P': summary_percentiles_parameters['b']['P'][3],
    'Tc': summary_percentiles_parameters['b']['Tc'][3],
    'limits_folded_x': [-0.75, 0.75],
    #'limits_folded_y': [-18.5, 18.5],
    #'limits_residuals_y': [-11.5, 11.5],
    'transit_folded': True,
    'K_error_1sigma': (summary_percentiles_parameters[planet_name]['K'][4] - summary_percentiles_parameters[planet_name]['K'][2])/2,
    'K_error_2sigma': (summary_percentiles_parameters[planet_name]['K'][5] - summary_percentiles_parameters[planet_name]['K'][1])/2,
    'K_error_3sigma': (summary_percentiles_parameters[planet_name]['K'][6] - summary_percentiles_parameters[planet_name]['K'][0])/2,
}

planet_name = 'c'
planet_dict[planet_name] =  {
    'P': summary_percentiles_parameters[planet_name]['P'][3],
    'Tc': summary_percentiles_derived[planet_name]['Tc'][3],
    'limits_folded_x': [-0.25, 1.25],
    #'limits_folded_y': [-496.5, 496.5],
    #'limits_residuals_y': [-11.5, 11.5],
    'transit_folded': False,
    'K_error_1sigma': (summary_percentiles_parameters[planet_name]['K'][4] - summary_percentiles_parameters[planet_name]['K'][2])/2,
    'K_error_2sigma': (summary_percentiles_parameters[planet_name]['K'][5] - summary_percentiles_parameters[planet_name]['K'][1])/2,
    'K_error_3sigma': (summary_percentiles_parameters[planet_name]['K'][6] - summary_percentiles_parameters[planet_name]['K'][0])/2,}

planet_name = 'd'
planet_dict[planet_name] =  {
    'P': summary_percentiles_parameters[planet_name]['P'][3],
    'Tc': summary_percentiles_derived[planet_name]['Tc'][3],
    'limits_folded_x': [-0.25, 1.25],
    #'limits_folded_y': [-496.5, 496.5],
    #'limits_residuals_y': [-11.5, 11.5],
    'transit_folded': False,
    'K_error_1sigma': (summary_percentiles_parameters[planet_name]['K'][4] - summary_percentiles_parameters[planet_name]['K'][2])/2,
    'K_error_2sigma': (summary_percentiles_parameters[planet_name]['K'][5] - summary_percentiles_parameters[planet_name]['K'][1])/2,
    'K_error_3sigma': (summary_percentiles_parameters[planet_name]['K'][6] - summary_percentiles_parameters[planet_name]['K'][0])/2,}

planet_name = 'e'
planet_dict[planet_name] =  {
    'P': summary_percentiles_parameters[planet_name]['P'][3],
    'Tc': summary_percentiles_derived[planet_name]['Tc'][3],
    'limits_folded_x': [-0.25, 1.25],
    #'limits_folded_y': [-496.5, 496.5],
    #'limits_residuals_y': [-11.5, 11.5],
    'transit_folded': False,
    'K_error_1sigma': (summary_percentiles_parameters[planet_name]['K'][4] - summary_percentiles_parameters[planet_name]['K'][2])/2,
    'K_error_2sigma': (summary_percentiles_parameters[planet_name]['K'][5] - summary_percentiles_parameters[planet_name]['K'][1])/2,
    'K_error_3sigma': (summary_percentiles_parameters[planet_name]['K'][6] - summary_percentiles_parameters[planet_name]['K'][0])/2,}

activity_dict = {
    'limits_full_x': [-0.25, 1.25],
    'limits_bjd': [2459200., 2460000.0],
    'limits_full_y': [-13.5, 13.5],
    'limits_residuals_y': [-11.5, 11.5],
    }
full_dict = {
    'reference_planet': 'b',
    #'limits_full_x': [-0.75, 0.75],
    'limits_full_x': [-0.25, 1.25],
    'limits_bjd': [2459200., 2460000.0],
    #'limits_full_y': [-506.5, 506.5],
    #'limits_residuals_y': [-11.5, 11.5],
}                                   