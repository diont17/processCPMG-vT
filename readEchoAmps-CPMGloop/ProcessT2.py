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
    
class PT2():
    def __init__(self, foldername):
        self.foldername = foldername
    
        self.phasedData = None
        self.echoCentreTime = None
        self.measureTime = None
        self.phasedDataFT = None
        self.numMeasures = None
        self.numEchoes = None
        self.numPoints = None
        self.xaxisFT = None
        self.integratedEchoes = None
        self.filename = ''
    
#        self.T2s = np.zeros(numMeasures)
#        self.T2spm = np.zeros(numMeasures)
#        self.E0s = np.zeros(numMeasures)
#        self.E0spm = np.zeros(numMeasures)
#        self.Cs = np.zeros(numMeasures)
    
    #try:
    #    phasedData
    #except NameError:
    def loadFile(self, loadfilename, show = False):
        
        filename  = loadfilename
        fname = self.foldername + filename
        infile = sio.loadmat(fname)
        self.phasedData=infile['phasedEchoData']
        self.echoCentreTime=infile['echoCentreTime'] [0]
        self.measureTime=infile['measureTime'] [0]
        del(infile)
        self.phasedDataFT=fft.fftshift(fft.fft(fft.fftshift(self.phasedData,axes=2),axis=2),axes=2)
    
        self.numMeasures=self.phasedData.shape[0]
        self.numEchoes=self.phasedData.shape[1]
        self.numPoints=int(self.phasedData.shape[2])
        print(self.phasedData.shape)
        self.xaxisFT=fft.fftshift(fft.fftfreq(self.numPoints,1e-6))
        
        if show:
            fig,ax=plt.subplots(1,2)
            ax[0].matshow(self.phasedData[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',extent=[0,self.numPoints,self.numEchoes,0],aspect='auto')
            ax[0].set_xlabel('Acquisition time (us)')
            ax[0].set_ylabel('Echo Index')
            ax[1].matshow(self.phasedDataFT[0,:,:].real,cmap=plt.cm.inferno,interpolation='none',aspect='auto')#,extent=[xaxisFT[0]*1e-3,xaxisFT[255]*1e-3,numEchoes,0])
            ax[1].set_xlabel('Frequency index')
            ax[1].set_ylabel('Echo Index')
    
    
    #Define the edges of the peak to integrate the echoes over
    def integrate(self, leftLimit=0, rightLimit=-1, useTD=True):
        
    #    ax[1].plot((leftLimit,leftLimit),(0,phasedDataFT.shape[1]),'-k')
    #    ax[1].plot((rightLimit,rightLimit),(0,phasedDataFT.shape[1]),'-k')
    #    ax[1].set_xlim(0,phasedDataFT.shape[2])
    #    ax[1].set_ylim(phasedDataFT.shape[1],0)
        
        if useTD:
            self.integratedEchoes=np.sum(self.phasedData[:,:,leftLimit:rightLimit],axis=2).real
        else:
            self.integratedEchoes=np.sum(self.phasedDataFT[:,:,leftLimit:rightLimit],axis=2).real
    
        plt.matshow(self.integratedEchoes.T,cmap=plt.cm.inferno,interpolation='none',aspect='auto')
        plt.xlabel('Experiment index')
        plt.ylabel('Echo #')
    
   
    #T2 fitting for different measurements
    def fitT2(self,useOffset = False):
        self.T2s=np.zeros(self.numMeasures)
        self.T2spm=np.zeros(self.numMeasures)
        self.E0s=np.zeros(self.numMeasures)
        self.E0spm=np.zeros(self.numMeasures)
        self.Cs=np.zeros(self.numMeasures)
    

        ignorefrom=-1
        
        t2FitFn = lambda x,a,b,c: (a*np.exp(-x/b))+c
        t2FitFnNoOffset = lambda x,a,b: t2FitFn(x,a,b,0)
        
        for i in range(self.numMeasures):
            if useOffset:
                fitI,pcov = opt.curve_fit(t2FitFn, self.echoCentreTime, self.integratedEchoes[i,:], p0 = [700,200,0])
                self.Cs[i] = fitI[2]
            else:
                fitI,pcov = opt.curve_fit(t2FitFnNoOffset, self.echoCentreTime, self.integratedEchoes[i,:],p0=[700,200])
           
            self.E0s[i]=fitI[0]
            self.E0spm[i] = np.abs(pcov[0][0]**0.5)
            self.T2s[i] = fitI[1]
            self.T2spm[i] = np.abs(pcov[1][1]**0.5)
    
            if self.E0spm[i]>self.E0s[i]:
                self.E0s[i] = 0
                self.E0spm[i] = 0   
                self.T2s[i] = 0
                self.T2spm[i] = 0
        self.plotT2s()
    
    def plotT2s(self):
        plt.figure()
        #plt.plot(measureTime/60,T2s,label='T2 (ms)')
        plt.errorbar(self.measureTime/60,self.T2s,self.T2spm,None,ecolor='red')
        plt.xlabel('Experiment Time (mins)')
        plt.ylabel('T2 (ms)')
        plt.title('{0} T2'.format(self.filename))
    #    plt.ylim(0,300)
        
    
    def plotAs(self):
        plt.figure()
        plt.plot(self.measureTime/60,self.E0s,label='Amplitude')
        plt.plot(self.measureTime/60,self.E0s+self.E0spm,'r')
        plt.plot(self.measureTime/60,self.E0s-self.E0spm,'r')
        plt.errorbar(self.measureTime/60,self.E0s,self.E0spm,None,ecolor='r')
        plt.ylabel('Amplitude')
        plt.xlabel('Experiment time(mins)')
        plt.ylim(0,500)
    
    
    def fitCheck(self,i):
        t2FitFn = lambda x,a,b,c: (a*np.exp(-x/b))+c
        plt.plot(self.echoCentreTime,t2FitFn(self.echoCentreTime,self.E0s[i],self.T2s[i],self.Cs[i]),self.echoCentreTime,self.integratedEchoes[i,:],label='T2= %.0fms, t=%ds' %(self.T2s[i],self.measureTime[i]))    
    
    #fitcheck(numMeasures/10)
    #fitcheck(numMeasures/5)
    #fitcheck(numMeasures/3)
    #fitcheck(numMeasures/2)
    #fitcheck(4*numMeasures/5)
    #plt.legend()
    #plt.plot((ignorefrom,ignorefrom),(0,E0s.max()),'-k')
    
    
    def closePlots(self):
        for a in plt.get_fignums(): plt.close(a)
    
    def process(self,name):
        self.loadFile(name)
        self.integrate()
        self.fitT2()
    #RMS=np.sqrt(np.mean(integratedEchoes**2,axis=1))
    #
    ##plt.plot(measureTime/60,RMS)
    ##plt.xlabel('Experiment Time (mins)')
    ##plt.ylabel('Signal RMS')
 