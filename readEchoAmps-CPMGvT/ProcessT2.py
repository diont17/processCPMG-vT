# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:56:56 2016

@author: dion
"""

## Monoexponential fitting to find changing T2 values
## Uses Fourier transform to get a better value for echo amplitude when there are many complex data points per echo

import numpy as np
import scipy as sci
import matplotlib.pyplot as plt

import scipy.fftpack as fft
import scipy.optimize as opt
import scipy.io as sio

import gc

fname='/home/dion/Experimental Data/BRU20161212/Data Processing/3Fresh 4Avg.mat'

try:
    phasedData
except NameError:
   infile = sio.loadmat(fname)
   phasedData=infile['phasedEchoData']
   echoCentreTime=infile['echoCentreTime'] [0]
   measureTime=infile['measureTime'] [0]
   del(infile)
   phasedDataFT=fft.fftshift(fft.fft(fft.fftshift(phasedData,axes=2),axis=2),axes=2)

numMeasures=phasedData.shape[0]
numEchoes=phasedData.shape[1]
numPoints=int(phasedData.shape[2])


xaxisFT=fft.fftshift(fft.fftfreq(numPoints,1e-6))

fig,ax=plt.subplots(1,2)
ax[0].matshow(phasedData[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',extent=[0,numPoints,numEchoes,0],aspect='auto')
ax[0].set_xlabel('Acquisition time (us)')
ax[0].set_ylabel('Echo Index')
ax[1].matshow(phasedDataFT[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',aspect='auto')#,extent=[xaxisFT[0]*1e-3,xaxisFT[255]*1e-3,numEchoes,0])
ax[1].set_xlabel('Frequency index')
ax[1].set_ylabel('Echo Index')

gc.collect()

#Define the edges of the peak to integrate the echoes over
peakLeft=122
peakRight=132
ax[1].plot((peakLeft,peakLeft),(0,phasedDataFT.shape[1]),'-k')
ax[1].plot((peakRight,peakRight),(0,phasedDataFT.shape[1]),'-k')
ax[1].set_xlim(0,phasedDataFT.shape[2])
ax[1].set_ylim(phasedDataFT.shape[1],0)

clipData=numMeasures
integratedEchoes=np.sum(phasedDataFT[:clipData,:,peakLeft:peakRight],axis=2).real
plt.matshow(integratedEchoes.T,cmap=plt.cm.inferno,interpolation='none',aspect='auto')
plt.xlabel('Experiment index')
plt.ylabel('Echo #')

#T2 fitting for different measurements    
T2s=np.zeros(numMeasures)
T2spm=np.zeros(numMeasures)
E0s=np.zeros(numMeasures)
E0spm=np.zeros(numMeasures)
Cs=np.zeros(numMeasures)

ignorefrom=400

def t2Fit(x,a,b,c):
    return (a*np.exp(-x/b))+c
   
for i in range(numMeasures):
    fitI,pcov=opt.curve_fit(t2Fit,echoCentreTime[0:ignorefrom],integratedEchoes[i,0:ignorefrom],p0=[200,80,5])
    E0s[i]=fitI[0]
    E0spm[i]=np.abs(pcov[0][0]**0.5)
    T2s[i]=fitI[1]
    T2spm[i]=np.abs(pcov[1][1]**0.5)
    Cs[i]=fitI[2]
    if E0spm[i]>E0s[i]:
        E0s[i]=0
        E0spm[i]=0    
        T2s[i]=0
        T2spm[i]=0

plt.figure()
#plt.plot(measureTime/60,E0s,label='Amplitude')
#plt.plot(measureTime/60,E0s+E0spm,'r')
#plt.plot(measureTime/60,E0s-E0spm,'r')
plt.errorbar(measureTime/60,E0s,E0spm,None,ecolor='r')
plt.ylabel('Amplitude')
plt.xlabel('Experiment time(mins)')
plt.ylim(0,500)


plt.figure()
#plt.plot(measureTime/60,T2s,label='T2 (ms)')
plt.errorbar(measureTime/60,T2s,T2spm,None,ecolor='red')
plt.xlabel('Experiment Time (mins)')
plt.ylabel('T2 (ms)')
plt.ylim(0,120)
plt.figure()

#plt.plot(echoCentreTime,t2Fit(echoCentreTime,E0s[10],T2s[10],Cs[10]),echoCentreTime,integratedEchoes[10])
#plt.plot(echoCentreTime,t2Fit(echoCentreTime,E0s[2],T2s[2],Cs[2]),echoCentreTime,integratedEchoes[2])

def fitcheck(i):
    plt.plot(echoCentreTime,t2Fit(echoCentreTime,E0s[i],T2s[i],Cs[i]),echoCentreTime,integratedEchoes[i,:],label='T2= %.0fms, t=%ds' %(T2s[i],measureTime[i]))    

fitcheck(numMeasures/10)
fitcheck(numMeasures/5)
fitcheck(numMeasures/3)
fitcheck(numMeasures/2)
fitcheck(4*numMeasures/5)
plt.legend()
plt.plot((ignorefrom,ignorefrom),(0,E0s.max()),'-k')


def closeplots():
    for a in plt.get_fignums(): plt.close(a)

#RMS=np.sqrt(np.mean(integratedEchoes**2,axis=1))
#
##plt.plot(measureTime/60,RMS)
##plt.xlabel('Experiment Time (mins)')
##plt.ylabel('Signal RMS')
