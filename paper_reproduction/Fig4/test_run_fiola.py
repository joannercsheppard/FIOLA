#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:01:46 2020
fiola simulation
@author: @caichangjia
"""
import caiman as cm
import glob
import h5py
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
from tensorflow.python.client import device_lib
from time import time, sleep
from threading import Thread
from fiola.fiolaparams import fiolaparams
from fiola.fiola import FIOLA
from fiola.utilities import match_spikes_greedy, normalize, compute_F1, movie_iterator, load, to_2D
import scipy.io
from skimage.io import imread


logging.basicConfig(format=
                    "%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s]"\
                    "[%(process)d] %(message)s",
                    level=logging.INFO)
    
logging.info(device_lib.list_local_devices()) # if GPU is not detected, try to reinstall tensorflow with pip install tensorflow==2.4.1


#%%
def run_fiola(fnames, path_ROIs, fr=400, options=None, save_name=None):
    #%%
    file_dir = os.path.split(fnames)[0]
    num_frames_init = options['num_frames_init']
    num_frames_total = options['num_frames_total']
    mode = options['mode']
    logging.info('Loading Movie')
    mov = cm.load(fnames, subindices=range(num_frames_init))
    mask = load(path_ROIs)
    template = np.median(mov, 0)

    #%% Run FIOLA
    #example motion correction
    motion_correct = True
    #example source separation
    do_nnls = True
    #%% Mot corr only
    if motion_correct:
        params = fiolaparams(params_dict=options)
        fio = FIOLA(params=params)
        # run motion correction on GPU on the initialization movie
        mc_nn_mov, shifts_fiola, _ = fio.fit_gpu_motion_correction(mov, template, fio.params.mc_nnls['offline_batch_size'], min_mov=mov.min())             
        plt.plot(shifts_fiola)
    else:    
        mc_nn_mov = mov
    
    #%% NNLS only
    if do_nnls:
        params = fiolaparams(params_dict=options)
        fio = FIOLA(params=params)
        if mode == 'voltage':
            A = scipy.sparse.coo_matrix(to_2D(mask, order='F')).T
            fio.fit_hals(mc_nn_mov, A)
            Ab = fio.Ab # Ab includes spatial masks of all neurons and background
        else:
            Ab = np.hstack((estimates.A.toarray(), estimates.b))
            
        trace_fiola, _ = fio.fit_gpu_nnls(mc_nn_mov, Ab, batch_size=fio.params.mc_nnls['offline_batch_size']) 
        #plt.plot(trace_fiola.T)
        
    #%% Set up online pipeline
    params = fiolaparams(params_dict=options)
    fio = FIOLA(params=params)
    if mode == 'voltage': # not thoroughly tested and computationally intensive for large files, it will estimate the baseline
        fio.fit_hals(mc_nn_mov, A)
        Ab = fio.Ab
    else:
        Ab = np.hstack((estimates.A.toarray(), estimates.b))
    Ab = Ab.astype(np.float32)
        

    fio = fio.create_pipeline(mc_nn_mov, trace_fiola, template, Ab, min_mov=mov.min())
    #%% run online
    time_per_step = np.zeros(num_frames_total-num_frames_init)
    trace = np.zeros((num_frames_total-num_frames_init,fio.Ab.shape[-1]), dtype=np.float32)
    trace_deconvolved = np.zeros((num_frames_total-num_frames_init, fio.Ab.shape[-1]-1), dtype=np.float32)
    lag = 10
    start = time()
        
    for idx, memmap_image in movie_iterator(fnames, num_frames_init, num_frames_total, batch_size=1):
        if idx % 1000 == 0:
            print(idx)        
        fio.fit_online_frame(memmap_image)   # fio.pipeline.saoz.trace[:, i] contains trace at timepoint i        
        trace[idx-num_frames_init] = fio.pipeline.saoz.trace[:,idx-1]
        trace_deconvolved[idx-num_frames_init] = fio.pipeline.saoz.trace_deconvolved[:,idx-1-lag]
        time_per_step[idx-num_frames_init] = (time()-start)
    
    logging.info(f'total time online: {time()-start}')
    logging.info(f'time per frame online: {(time()-start)/(num_frames_total-num_frames_init)}')
    plt.plot(np.diff(time_per_step),'.')
    #%% Visualize result
    fio.compute_estimates()
    fio.view_components(template)
    fio.estimates.timing_online=time_per_step
    fio.estimates.online_trace = trace.T
    fio.estimates.online_trace_deconvolved = trace_deconvolved.T
    
    # import pdb
    # pdb.set_trace()
    
    #%% save some interesting data
    # if True:
    #     np.savez(fnames[:-4]+'_fiola_result_v3.0.npz', time_per_step=time_per_step, trace=trace, 
    #          caiman_file = caiman_file, 
    #          fnames_exp = fnames, 
    #          estimates = fio.estimates)
    #save_name = f'fiola_result_test_v3.3'
    np.save(os.path.join(file_dir, 'viola', save_name), fio.estimates)
    plt.close('all')
    
    #%% save
    log_files = glob.glob('*_LOG_*')
    for log_file in log_files:
        os.remove(log_file)
    
