#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 10:30:42 2020
Parameters for online analysis of voltage imaging data.
@author: @agiovann, @caichangjia, @cynthia
"""

import logging
import numpy as np

class violaparams(object):

    def __init__(self, fnames=None, fr=None, ROIs=None,  border_to_0=0, freq_detrend = 1/3, do_plot_init=True, update_bg=False, num_frames_total=100000, window = 10000, step = 5000, 
                 detrend=True, flip=True, do_scale=False, robust_std=False, freq=15, 
                 thresh_range=[3.5, 5], mfp=0.2, do_plot=False, params_dict={}):
        """Class for setting parameters for voltage imaging. Including parameters for the data, motion correction and
        spike detection. The prefered way to set parameters is by using the set function, where a subclass is determined
        and a dictionary is passed. The whole dictionary can also be initialized at once by passing a dictionary
        params_dict when initializing the CNMFParams object.
        """
        self.data = {
            'fnames': fnames, # name of the movie, only memory map file for spike detection
            'fr': fr, # sample rate of the movie
            'ROIs': ROIs # a 3-d matrix contains all region of interests
        }

        self.mc_nnls = {
            'border_to_0': border_to_0,  # border of the movie will copy signals from the nearby pixels
            'freq_detrend': freq_detrend, # high-pass frequency for removing baseline, used for init of spatial footprint
            'do_plot_init': do_plot_init, # plot the spatial mask result for init of spaital footprint
            'update_bg': update_bg # update background components for spatial footprints
        }

        self.spike = {
            'num_frames_total':num_frames_total, # estimated total number of frames for processing, this is used for generating matrix to store data
            'window': window, # window for updating statistics
            'step': step, # step for updating statistics
            'flip': flip, # whether to flip signal to find spikes    
            'detrend': detrend, # whether to remove photobleaching
            'do_scale': do_scale, # whether to scale the input trace or not
            'robust_std':robust_std, # whether to use robust way to estimate noise
            'freq': freq, # frequency for removing subthreshold activity
            'thresh_range':thresh_range, # Range of threshold factor. Real threshold is threshold factor multiply by the estimated noise level
            'mfp': mfp, #  Maximum estimated false positive. An upper bound for estimated false positive rate based on noise
            'do_plot': do_plot # Whether to plot or not
        }

        self.change_params(params_dict)
#%%
    def set(self, group, val_dict, set_if_not_exists=False, verbose=False):
        """ Add key-value pairs to a group. Existing key-value pairs will be overwritten
            if specified in val_dict, but not deleted.

        Args:
            group: The name of the group.
            val_dict: A dictionary with key-value pairs to be set for the group.
            set_if_not_exists: Whether to set a key-value pair in a group if the key does not currently exist in the group.
        """

        if not hasattr(self, group):
            raise KeyError('No group in CNMFParams named {0}'.format(group))

        d = getattr(self, group)
        for k, v in val_dict.items():
            if k not in d and not set_if_not_exists:
                if verbose:
                    logging.warning(
                        "NOT setting value of key {0} in group {1}, because no prior key existed...".format(k, group))
            else:
                if np.any(d[k] != v):
                    logging.warning(
                        "Changing key {0} in group {1} from {2} to {3}".format(k, group, d[k], v))
                d[k] = v

#%%
    def get(self, group, key):
        """ Get a value for a given group and key. Raises an exception if no such group/key combination exists.

        Args:
            group: The name of the group.
            key: The key for the property in the group of interest.

        Returns: The value for the group/key combination.
        """

        if not hasattr(self, group):
            raise KeyError('No group in CNMFParams named {0}'.format(group))

        d = getattr(self, group)
        if key not in d:
            raise KeyError('No key {0} in group {1}'.format(key, group))

        return d[key]

    def get_group(self, group):
        """ Get the dictionary of key-value pairs for a group.

        Args:
            group: The name of the group.
        """

        if not hasattr(self, group):
            raise KeyError('No group in CNMFParams named {0}'.format(group))

        return getattr(self, group)

    def change_params(self, params_dict, verbose=False):
        for gr in list(self.__dict__.keys()):
            self.set(gr, params_dict, verbose=verbose)
        for k, v in params_dict.items():
            flag = True
            for gr in list(self.__dict__.keys()):
                d = getattr(self, gr)
                if k in d:
                    flag = False
            if flag:
                logging.warning('No parameter {0} found!'.format(k))
        return self
