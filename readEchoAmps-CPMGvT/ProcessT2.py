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

foldername='/home/dion/Documents/Experimental Data/BloodflowTesting/170705/Bloodbag 1/processed/'

phasedData = None
echoCentreTime = None
measureTime = None
phasedDataFT = None
numMeasures = None
numEchoes = None
numPoints = None
xaxisFT = None
integratedEchoes = None
filename = ''

T2s = np.zeros(numMeasures)
T2spm = np.zeros(numMeasures)
E0s = np.zeros(numMeasures)
E0spm = np.zeros(numMeasures)
Cs = np.zeros(numMeasures)


#try:
#    phasedData
#except NameError:
def loadFile(loadfilename):
    
    global phasedData, echoCentreTime, measureTime, phasedDataFT, numMeasures, numEchoes, numPoints, xaxisFT
    global filename
    filename  = loadfilename
    fname = foldername + filename
    infile = sio.loadmat(fname)
    phasedData=infile['phasedEchoData']
    echoCentreTime=infile['echoCentreTime'] [0]
    measureTime=infile['measureTime'] [0]
    del(infile)
    phasedDataFT=fft.fftshift(fft.fft(fft.fftshift(phasedData,axes=2),axis=2),axes=2)

    numMeasures=phasedData.shape[0]
    numEchoes=phasedData.shape[1]
    numPoints=int(phasedData.shape[2])
    print(phasedData.shape)
    xaxisFT=fft.fftshift(fft.fftfreq(numPoints,1e-6))

    fig,ax=plt.subplots(1,2)
    ax[0].matshow(phasedData[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',extent=[0,numPoints,numEchoes,0],aspect='auto')
    ax[0].set_xlabel('Acquisition time (us)')
    ax[0].set_ylabel('Echo Index')
    ax[1].matshow(phasedDataFT[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',aspect='auto')#,extent=[xaxisFT[0]*1e-3,xaxisFT[255]*1e-3,numEchoes,0])
    ax[1].set_xlabel('Frequency index')
    ax[1].set_ylabel('Echo Index')


#Define the edges of the peak to integrate the echoes over
def integrate(leftLimit=0, rightLimit=-1, useTD=True):
    global phasedData, echoCentreTime, measureTime, phasedDataFT, numMeasures, numEchoes, numPoints, xaxisFT
    global integratedEchoes    
#    ax[1].plot((leftLimit,leftLimit),(0,phasedDataFT.shape[1]),'-k')
#    ax[1].plot((rightLimit,rightLimit),(0,phasedDataFT.shape[1]),'-k')
#    ax[1].set_xlim(0,phasedDataFT.shape[2])
#    ax[1].set_ylim(phasedDataFT.shape[1],0)
    
    if useTD:
        integratedEchoes=np.sum(phasedData[:,:,leftLimit:rightLimit],axis=2).real
    else:
        integratedEchoes=np.sum(phasedDataFT[:,:,leftLimit:rightLimit],axis=2).real

    plt.matshow(integratedEchoes.T,cmap=plt.cm.inferno,interpolation='none',aspect='auto')
    plt.xlabel('Experiment index')
    plt.ylabel('Echo #')

def t2FitFn(x,a,b,c):
    return (a*np.exp(-x/b))+c

#T2 fitting for different measurements
def fitT2(useOffset = False):
    global phasedData, echoCentreTime, measureTime, phasedDataFT, numMeasures, numEchoes, numPoints, xaxisFT
    global integratedEchoes
    global filename
    global E0s, E0spm, T2s, T2spm, Cs

    T2s=np.zeros(numMeasures)
    T2spm=np.zeros(numMeasures)
    E0s=np.zeros(numMeasures)
    E0spm=np.zeros(numMeasures)
    Cs=np.zeros(numMeasures)

    ignorefrom=-1
           
    t2FitFnNoOffset = lambda x,a,b: t2FitFn(x,a,b,0)
    
    for i in range(numMeasures):
        if useOffset:
            fitI,pcov = opt.curve_fit(t2FitFn, echoCentreTime, integratedEchoes[i,:], p0 = [700,200,0])
            Cs[i] = fitI[2]
        else:
            fitI,pcov = opt.curve_fit(t2FitFnNoOffset,echoCentreTime,integratedEchoes[i,:],p0=[700,200])
       
        E0s[i]=fitI[0]
        E0spm[i] = np.abs(pcov[0][0]**0.5)
        T2s[i] = fitI[1]
        T2spm[i] = np.abs(pcov[1][1]**0.5)

        if E0spm[i]>E0s[i]:
            E0s[i] = 0
            E0spm[i] = 0   
            T2s[i] = 0
            T2spm[i] = 0
    plotT2s()

def plotT2s():
    global measureTime, T2s, T2spm, filename
    plt.figure()
    #plt.plot(measureTime/60,T2s,label='T2 (ms)')
    plt.errorbar(measureTime/60,T2s,T2spm,None,ecolor='red')
    plt.xlabel('Experiment Time (mins)')
    plt.ylabel('T2 (ms)')
    plt.title('{0} T2'.format(filename))
#    plt.ylim(0,300)
    

def plotAs():
    global phasedData, echoCentreTime, measureTime, phasedDataFT, numMeasures, numEchoes, numPoints, xaxisFT
    global integratedEchoes
    global E0s, E0spm, T2s, T2spm, Cs

    plt.figure()
    plt.plot(measureTime/60,E0s,label='Amplitude')
    plt.plot(measureTime/60,E0s+E0spm,'r')
    plt.plot(measureTime/60,E0s-E0spm,'r')
    plt.errorbar(measureTime/60,E0s,E0spm,None,ecolor='r')
    plt.ylabel('Amplitude')
    plt.xlabel('Experiment time(mins)')
    plt.ylim(0,500)


def fitCheck(i):
    plt.plot(echoCentreTime,t2FitFn(echoCentreTime,E0s[i],T2s[i],Cs[i]),echoCentreTime,integratedEchoes[i,:],label='T2= %.0fms, t=%ds' %(T2s[i],measureTime[i]))    

#fitcheck(numMeasures/10)
#fitcheck(numMeasures/5)
#fitcheck(numMeasures/3)
#fitcheck(numMeasures/2)
#fitcheck(4*numMeasures/5)
#plt.legend()
#plt.plot((ignorefrom,ignorefrom),(0,E0s.max()),'-k')


def closePlots():
    for a in plt.get_fignums(): plt.close(a)

def process(name):
    loadFile(name)
    integrate()
    fitT2()
#RMS=np.sqrt(np.mean(integratedEchoes**2,axis=1))
#
##plt.plot(measureTime/60,RMS)
##plt.xlabel('Experiment Time (mins)')
##plt.ylabel('Signal RMS')
 