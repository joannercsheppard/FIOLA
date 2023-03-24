#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 17:02:16 2020
This file is for timing of spike detection algorithm
@author: caichangjia
"""

#%%
import sys
sys.path.append('/home/nel/CODE/VIOLA')
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams.update({'pdf.fonttype' : 42, 
                     'ps.fonttype' : 42, 
                     'legend.frameon' : False, 
                     'axes.spines.right' :  False, 
                     'axes.spines.top' : False})
import numpy as np
import pyximport
pyximport.install()
from fiola.signal_analysis_online import SignalAnalysisOnlineZ
from fiola.utilities import signal_filter

path = '/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/result/test_debug_spike_detection'



#%%
def run(num, seed=0, Tinit=20000):
    print(num)
    frate = 400
    img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
    img = np.hstack([img[:20000] for _ in range(5)])
    trace_all = np.stack([img for i in range(num)])
    #trace_all = trace_all[:60000]
        
    saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
    saoz.fit(trace_all[:,:Tinit], len(img))
    for n in range(Tinit, 100000):
        saoz.fit_next(trace_all[:, n:n+1], n)
    return np.array(saoz.t_detect)[Tinit:] * 1000

tt = run(num=100)
np.save(path+f'/timing_{app}.npy', tt)

plt.figure()
plt.plot(tt)
plt.savefig(path+f'/timing_{app}.pdf')
#%%
# app = 5
# frate=400
# saoz_all = {}
# for num_neurons in [500]:#, 500]:
#     img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
#     img = np.hstack([img[:20000] for _ in range(5)])
#     trace_all = np.stack([img for i in range(num_neurons)])
#     saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
#     saoz.fit(trace_all[:,:20000], len(img))
#     # for n in range(20000, trace_all.shape[1]):
#     #     saoz.fit_next(trace_all[:, n:n+1], n)
#     for n in range(20000, 100000):
#         saoz.fit_next(trace_all[:, n:n+1], n)
#     saoz_all[num_neurons] = saoz
   
# np.save(path+f'/timing_{app}.npy', saoz.t_detect)
    


# plt.figure()
# plt.plot(np.array(saoz_all[500].t_detect[20000:]) * 1000)
# plt.savefig(path+f'/timing_{app}.pdf')






#%%
# app = 4
# def run(num, seed=0, Tinit=20000):
#     print(num)
#     #print(seed)
#     #np.random.seed(seed)
#     frate = 400
#     img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
#     img = np.hstack([img[:20000] for _ in range(5)])
#     trace_all = np.stack([img for i in range(num)])
#     #trace_all = trace_all[:60000]
        
#     saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
#     saoz.fit(trace_all[:,:Tinit], len(img))
#     for n in range(Tinit, 100000):
#         saoz.fit_next(trace_all[:, n:n+1], n)
#     return np.array(saoz.t_detect)[Tinit:] * 1000

# tt = run(num=500)
# np.save(path+f'/timing_{app}.npy', tt)

# plt.figure()
# plt.plot(tt)
# plt.savefig(path+f'/timing_{app}.pdf')



#%%
# app = 3
# def run(num, seed=0, Tinit=20000):
#     print(num)
#     #print(seed)
#     #np.random.seed(seed)
#     frate = 400
#     img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
#     img = np.hstack([img[:20000] for _ in range(5)])
#     trace_all = np.stack([img for i in range(num)])
#     #trace_all = trace_all[:60000]
        
#     saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
#     saoz.fit(trace_all[:,:Tinit], len(img))
#     for n in range(Tinit, 100000):
#         saoz.fit_next(trace_all[:, n:n+1], n)
#     return np.array(saoz.t_detect)[Tinit:] * 1000

# tt = run(num=100)
# np.save(path+f'/timing_{app}.npy', tt)

# plt.figure()
# plt.plot(tt)
# plt.savefig(path+f'/timing_{app}.pdf')

# #%%
# app = 0

# frate=400
# saoz_all = {}
# for num_neurons in [100]:#, 500]:
#     img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
#     img = np.hstack([img[:20000] for _ in range(5)])
#     trace_all = np.stack([img for i in range(num_neurons)])
#     saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
#     saoz.fit(trace_all[:,:20000], len(img))
#     # for n in range(20000, trace_all.shape[1]):
#     #     saoz.fit_next(trace_all[:, n:n+1], n)
#     for n in range(20000, 100000):
#         saoz.fit_next(trace_all[:, n:n+1], n)
#     saoz_all[num_neurons] = saoz
    
# np.save(path+f'/timing_{app}.npy', saoz.t_detect)
    

# #%%
# plt.figure()
# plt.plot(np.array(saoz_all[100].t_detect[20000:]) * 1000)
# plt.savefig(path+f'/timing_{app}.pdf')

# #%%
# app = 1

# frate=400
# saoz_all = {}
# num_neurons=100
# img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
# img = np.hstack([img[:20000] for _ in range(5)])
# trace_all = np.stack([img for i in range(num_neurons)])
# saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
# saoz.fit(trace_all[:,:20000], len(img))
# # for n in range(20000, trace_all.shape[1]):
# #     saoz.fit_next(trace_all[:, n:n+1], n)
# for n in range(20000, 100000):
#     saoz.fit_next(trace_all[:, n:n+1], n)
# saoz_all[num_neurons] = saoz
    
# np.save(path+f'/timing_{app}.npy', saoz.t_detect)
    

# #%%
# plt.figure()
# plt.plot(np.array(saoz_all[100].t_detect[20000:]) * 1000)
# plt.savefig(path+f'/timing_{app}.pdf')

#%%
# frate = 400
# num = 100
# img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
# img = np.hstack([img[:20000] for _ in range(5)])
# trace_all = np.stack([img for i in range(num)])
# #trace_all = trace_all[:60000]
    
# saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
# saoz.fit(trace_all[:,:Tinit], len(img))
# for n in range(Tinit, 100000):
#     saoz.fit_next(trace_all[:, n:n+1], n)

#%%
# frate=400
# saoz_all = []
# for _ in range(3):
#     for num_neurons in [100]:#, 500]:
#         img = np.load('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/one_neuron/test_timing.npy')
#         img = np.hstack([img[:20000] for _ in range(5)])
#         trace_all = np.stack([img for i in range(num_neurons)])
#         saoz = SignalAnalysisOnlineZ(fr=frate, flip=False, robust_std=False, do_scale=False, detrend=False)
#         saoz.fit(trace_all[:,:20000], len(img))
#         # for n in range(20000, trace_all.shape[1]):
#         #     saoz.fit_next(trace_all[:, n:n+1], n)
#         for n in range(20000, 100000):
#             saoz.fit_next(trace_all[:, n:n+1], n)
#         saoz_all.append(saoz)
        

# #%%
# ii = []
# for jj in range(3):
#     ii.append(np.array(saoz_all[jj].t_detect[20000:]) * 1000)
# ii = np.array(ii)

# plt.plot(ii.mean(0))




#%%
# plt.figure()
# #plt.plot(saoz.t_detect)
# plt.plot(np.array(saoz_all[500].t_detect)[20000:]*1000, label='500 neurons', color='orange')
# plt.plot(np.array(saoz_all[100].t_detect)[20000:]*1000, label='100 neurons', color='blue')
# plt.ylabel('Timing (ms)')
# plt.legend()
# plt.savefig('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/figures/v3.0/supp/Fig_supp_detection_timing_v3.7.pdf')

# #%%
# t1 = np.array(saoz_all[100].t_detect[20000:]) * 1000
# t2 = np.array(saoz_all[200].t_detect[20000:]) * 1000
# t3 = np.array(saoz_all[500].t_detect[20000:]) * 1000

# plt.figure()
# plt.bar([0, 1, 2], [t1.mean(), t2.mean(), t3.mean()], yerr=[t1.std(), t2.std(), t3.std()])
# plt.ylabel('Timing (ms)')
# #plt.xlabel('Number of neurons')
# plt.xticks([0, 1, 2], ['100 neurons', '200 neurons', '500 neurons'])
# plt.savefig('/media/nel/storage/NEL-LAB Dropbox/NEL/Papers/VolPy_online/figures/v3.0/supp/Fig_supp_detection_timing_mean_v3.7.pdf.pdf')


#%%
"""
from nmf_support import normalize
plt.plot(dict1['v_t'], saoz.t_detect)
plt.plot(dict1['e_t'], dict1['e_sg']/100000)
"""
