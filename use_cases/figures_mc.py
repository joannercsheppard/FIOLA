#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 17:53:43 2021

@author: nel
"""

#%% imports!
import numpy as np
import pylab as plt
import os
import tensorflow as tf
# tf.compat.v1.disable_eager_execution()
import tensorflow.keras as keras
import tensorflow_addons as tfa
from queue import Queue
from threading import Thread
from past.utils import old_div
from skimage import io
from skimage.transform import resize
import cv2
import timeit
import multiprocessing as mp
from tensorflow.python.keras import backend as K
from viola.caiman_functions import to_3D, to_2D
import scipy
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.keras.backend.set_floatx("float32")

#%% set folders
cal = True
if cal: 
    base_folder = "../../NEL-LAB Dropbox/NEL/Papers/VolPy_online/CalciumData/DATA_PAPER_ELIFE"
    dataset = "/N.01.01"
    slurm_data = base_folder + dataset + "/results_analysis_online_sensitive_SLURM_01.npz"
    # get ground truth data
    with np.load(slurm_data, allow_pickle=True) as ld:
        print(list(ld.keys()))
        locals().update(ld)
        Ab_gt = Ab[()].toarray()
        num_bckg = f.shape[0]
        b_gt, A_gt = Ab_gt[:,:num_bckg], Ab_gt[:,num_bckg:]
        num_comps = Ab_gt.shape[-1]
        f_gt, C_gt = Cf[:num_bckg], Cf[num_bckg:num_comps]
        noisyC = noisyC[num_bckg:num_comps]
    
    dirname = base_folder + dataset + "/images_"+dataset[1:]
    a2 = []
    dims = 512
    #for fname in os.listdir(dirname):r
    for i in range(noisyC.shape[1]//2):
        fname = "image" + str(i).zfill(5) + ".tif"
        im = io.imread(os.path.join(dirname, fname))
        #print(fname)
        # a2.append(resize(im, (233, 249)))
        a2.append(resize(im, (512, 512)))
        # a2.append(im)
        # a2.append(im[0:125, 125:256])
        
    # image normalization for movie
    img_norm = np.std(a2, axis=0)
    img_norm += np.median(img_norm)
    mov = a2/img_norm[None, :, :]
    template = np.median(mov[:len(mov)//2], axis=0)
    
else:
    import glob
    motcorr = True
    if motcorr:
        names = glob.glob('/home/nel/NEL-LAB Dropbox/NEL/Papers/VolPy_online/CalciumData/MotCorr/*.tif')
        names.append('/home/nel/NEL-LAB Dropbox/NEL/Papers/VolPy_online/CalciumData/MotCorr/mesoscope.hdf5')
        names+=glob.glob('/home/nel/NEL-LAB Dropbox/NEL/Papers/VolPy_online/data/voltage_data/*/*.hdf5')
    j=2
    movie = names[j]
    # movie='/home/nellab/NEL-LAB Dropbox/NEL/Papers/VolPy_online/test_data/one_neuron/Mouse_Session_1/Mouse_Session_1.tif'
    mov = io.imread(movie)
    full = False
    template = np.load(movie[:-4]+"_template_on.npy")
#%%
full = True
# from viola.motion_correction_gpu import MotionCorrectTest, MotionCorrect
from mc_batch import MotionCorrect
# mask = np.ones_like(template)

mov  = mov.astype(np.float32)
# plt.imshow(template)
# template = np.median(mov[:2000], axis=0)
if full:
    mc_layer = MotionCorrect(template[:,:,None,None])
else:
    mc_layer = MotionCorrect(template, template.shape)
#  motion correction
tempout = []
new_mov = []
start = timeit.default_timer()
print(tf.executing_eagerly())
for i in range(500):
    fr = mc_layer(mov[i:i+5, :, :, None][None, :].astype(np.float32))
    # fr = mc_layer(mov[i])
    tempout.append(fr[1]) #traces
    new_mov.append(timeit.default_timer()-start) #movie
    break
# print(np.mean(fr[0]))   
# #%%
# new_mov_t = []
# for fr in new_mov:
#     new_mov_t.append(np.reshape(fr.numpy(), (548, 496), order="F"))
# plt.imshow(new_mov_t[0])
# rearrange traces into saveable format
tempx1, tempy1 = [], []
for i in range(len(tempout)):
    tempx1.append(tempout[i][0].numpy())
    tempy1.append(tempout[i][1].numpy())
tempx1 = np.array(tempx1).squeeze()
tempy1 = np.array(tempy1).squeeze()
#%%
out = []
def generator():
    for fr in  mov:
        yield{"m":fr[None,:,:,None]}
             
def get_frs():
    dataset = tf.data.Dataset.from_generator(generator, output_types={'m':tf.float32}, output_shapes={"m":(1,512,512,1)})
    return dataset
#%%   
from FFT_MOTION import get_mc_model
import timeit
import tensorflow.keras as keras
model = get_mc_model(template[:,:,None,None])
model.compile(optimizer='rmsprop', loss='mse')
estimator = tf.keras.estimator.model_to_estimator(model)
times = []
start = timeit.default_timer()
for i in estimator.predict(input_fn=get_frs, yield_single_examples=False):
    out.append(i)
    times.append(timeit.default_timer()-start)
    # break
print(timeit.default_timer()-start)
x=[]
y=[]
for val in  out:
    x.append(np.squeeze(val["motion_correct_1"]))
    y.append(np.squeeze(val["motion_correct_2"]))
np.save("/home/nel/NEL-LAB Dropbox/NEL/Papers/VolPy_online/FastResults/MC/k37_times", np.diff(times[1:-1]))
#%%
times = [0]*500
out = []
start = timeit.default_timer()
for i in range(500):
    out.append(model(mov[i, :, :, None][None, :])[1])
    times[i] = timeit.default_timer()-start
plt.plot(np.diff(times))
print(np.mean(np.diff(times)))
#%%
from FFT_MOTION import get_nnls_model
import timeit
import time
import tensorflow.keras as keras
from multiprocessing import Queue
#%%
out = []
q = Queue()
q.put((x0[None],x0[None]))
def generator():
    # print('hi')
    k=[[0.0]]
    for fr in  mov:
        # print("stuck?")
        (y,x) = q.get()
        # print("unstuck")
        yield{"m":fr[None,:,:,None], "y":y, "x":x, "k":k}
             
def get_frs():
    dataset = tf.data.Dataset.from_generator(generator, output_types={'m':tf.float32, 'y':tf.float32, 'x':tf.float32, 'k':tf.float32}, 
                                             output_shapes={"m":(1,512,512,1), "y":(1, neurs, 1),"x":(1, neurs, 1), "k":(1, 1)})
    return dataset

model = get_nnls_model(template, Ab_gt_start.astype(np.float32), 30)
model.compile(optimizer='rmsprop', loss='mse')
estimator  = tf.keras.estimator.model_to_estimator(model)
times = []
#%%
start = time.time()
for i in estimator.predict(input_fn=get_frs, yield_single_examples=False):
    q.put((i["nnls"], i["nnls_1"]))
    times.append(time.time()-start)
plt.plot(np.diff(times[1:-1]))
#%%
into = [mov[0, :, :, None][None, :], x0, x0, [[0.0]]]
start0 = timeit.default_timer()

for i in range(1, 500):
    start = timeit.default_timer()
    out = model(into)[0]
    times[i] = timeit.default_timer()-start
    into = [mov[i+1, :, :, None][None, :], out[0], out[1], out[2]]
    # time.sleep(0.01)
    
    # break
print(timeit.default_timer()-start)
plt.plot(np.diff(times))
print(np.mean(np.diff(times)))
#%% LOOK HERE
from FFT_MOTION import Pipeline
mc0 = np.expand_dims(mov[0:1, :, :], axis=3)
trace_extractor = Pipeline(model,mc0, mov)
#%%
out = trace_extractor.get_traces(10)