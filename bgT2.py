#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 12:29:11 2017

@author: dion
"""

import numpy as np
import scipy.optimize as opt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from flintlib import flint

class dataWorkerT2(QtCore.QThread):
    bgThreadResult=QtCore.pyqtSignal(object)
    bgThreadTextOut=QtCore.pyqtSignal(QtCore.QString)
    updateprogress=QtCore.pyqtSignal(QtCore.QString)
    
    def __init__(self,xdataIn,ydataIn,echoTimes,methodIndex):
        QtCore.QThread.__init__(self)
        self.xdataIn=xdataIn
        self.ydataIn=ydataIn
        self.numSequences=xdataIn.shape[0]
        self.echoTimes=echoTimes
        self.methodIndex=methodIndex 
        
        #0 - monoexponential fit
        #1 - monoexponential, no offset (c)
        
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
        self.updateprogress.emit('Starting T2 fitting')
        
        if self.methodIndex==0:
            T2Fit=np.zeros((self.numSequences,3))
            T2Fitpm=np.zeros((self.numSequences,3))
            
            def t2Fit(x,t2,a,c):
                return (a*np.exp(-x/t2))+c
            self.bgThreadTextOut.emit('Fit decays to  A*exp(-x/T2) + c' )
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}|{6:^10.10s}|'.format('#','Echotime','T2','+/-','A','+/-','c'))

            for i in xrange(self.numSequences):
                popt,pcov=opt.curve_fit(t2Fit,self.xdataIn[i,:],self.ydataIn[i,:],p0=[0.1,120,0])
                T2Fit[i,0]=popt[0]
                T2Fitpm[i,0]=np.abs(pcov[0,0]**0.5)
                T2Fit[i,1]=popt[1]
                T2Fitpm[i,1]=np.abs(pcov[1,1]**0.5)
                T2Fit[i,2]=popt[2]
                T2Fitpm[i,2]=np.abs(pcov[2,2]**0.5)
                fitString='|{0:^10d}|{1:^10.3e}|{2:^10.4f}|{3:^10.4f}|{4:^10.4f}|{5:^10.4f}|{6:^10.4f}|'.format(i,self.echoTimes[i],T2Fit[i,0],T2Fitpm[i,0],T2Fit[i,1],T2Fitpm[i,1],T2Fit[i,2])
               
                self.bgThreadTextOut.emit(fitString)
                self.updateprogress.emit('Fit %d of %d'%(i,self.numSequences))
            
            res={'fitpar': T2Fit, 'fitparpm': T2Fitpm}
                
        elif self.methodIndex==1:
            T2Fit=np.zeros((self.numSequences,3))
            T2Fitpm=np.zeros((self.numSequences,3))
            
            t2expConst = lambda x,t2,a,c: (a*np.exp(-x/t2)+c)
            
            #Calculate c from longest echotime measurement
            popt,pcov=opt.curve_fit(t2expConst, self.xdataIn[-1,:], self.ydataIn[-1,:],p0=[0.1,120,0])
            c=popt[2]
            
            t2exp = lambda x,t2,a: ((a*np.exp(-x/t2))+c) 
            
            self.bgThreadTextOut.emit('Fit decays to  A*exp(-x/T2) + c, c={0:.3f}'.format(c))
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}|'.format('#','Echotime','T2','+/-','A','+/-'))
            
            for i in xrange(self.numSequences):
                popt,pcov=opt.curve_fit(t2exp,self.xdataIn[i,:],self.ydataIn[i,:],p0=[0.1,120])
                
                T2Fit[i,0]=popt[0]
                T2Fitpm[i,0]=np.abs(pcov[0,0]**0.5)
                T2Fit[i,1]=popt[1]
                T2Fitpm[i,1]=np.abs(pcov[1,1]**0.5)
                
                fitString='|{0:^10d}|{1:^10.3e}|{2:^10.4f}|{3:^10.4f}|{4:^10.4f}|{5:^10.4f}|'.format(i,self.echoTimes[i],T2Fit[i,0],T2Fitpm[i,0],T2Fit[i,1],T2Fitpm[i,1])
                
                self.bgThreadTextOut.emit(fitString)
                self.updateprogress.emit('Fit %d of %d'%(i,self.numSequences))
            T2Fit[:,2]=c
            res={'fitpar': T2Fit, 'fitparpm': T2Fitpm}

        elif self.methodIndex==2:
            t2expConst = lambda x,t2,a,c: (a*np.exp(-x/t2)+c)
            
            #Calculate c from longest echotime measurement
            popt,pcov=opt.curve_fit(t2expConst, self.xdataIn[-1,:], self.ydataIn[-1,:],p0=[0.1,120,0])
            c=popt[2]
            
            self.updateprogress.emit('Starting ILT, prints to console')
            
            self.bgThreadTextOut.emit('Running flint ILT')
            
            ILbins = 128
            alpha = 8e-2
            self.bgThreadTextOut.emit('Using alpha={0:.2e}, {1:d} bins'.format(alpha, ILbins))
            #Stays the same for each iteration
            numechoes = self.xdataIn.shape[1]
            T2out = np.logspace(-3, 0, ILbins)
            K1 = np.array([[1]])
            
            #modified in each iteration
            ILspectra = np.zeros((self.numSequences, ILbins))
            K2 = np.zeros((numechoes, ILbins))
            pickedT2 = np.zeros(self.numSequences)
            pickedT2peak = np.zeros(self.numSequences)
            pickedT2pm = np.zeros(self.numSequences)
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}'.format('#','Echotime','T2 at Max','T2 +/-'))
            
            for i in xrange(self.numSequences):
                flag=''
                K2[:,:] = np.exp(np.outer(-1*self.xdataIn[i,:], 1.0/T2out))
                ILspectra[i,:], resida = flint(K1, K2, self.ydataIn[i]-c, alpha, S = ILspectra[i-1])
                
                mxloc=np.argmax(ILspectra[i,:])
                #If max is at the edge, force it back into the middle
                if mxloc==0 or mxloc == ILbins-1:
                    mxloc=np.argmax(ILspectra[i,5:-5])
                    flag='offscale'
                pickedT2[i] = T2out[mxloc]
                pickedT2peak[i] = ILspectra[i,mxloc]
#                
                gaussPeak = lambda x,a: (np.exp(-1*((x-T2out[mxloc])/a)**2))
                popt,pcov = opt.curve_fit(gaussPeak, T2out[mxloc-10:mxloc+10], ILspectra[i, mxloc-10:mxloc+10]/pickedT2peak[i])
                pickedT2pm[i] = popt[0]
                pickedT2pm = np.abs(pickedT2pm)
                self.updateprogress.emit('Done ILT %d/%d'%(i,self.numSequences))
                fitString='|{0:^10d}|{1:^10.3e}|{2:^10.4f}|{4:^10.4f}|{3:s}'.format(i,self.echoTimes[i],pickedT2[i],flag,pickedT2pm[i])
                self.bgThreadTextOut.emit(fitString)
            
            res = {'pickedT2': pickedT2, 'ILspectra':ILspectra, 'T2axis': T2out, 'const': c, 'pickedT2pm': pickedT2pm}
#            print(pickedT2.shape, ILspectra.shape, T2out.shape)
        self.updateprogress.emit('Done T2 fitting')
        self.bgThreadTextOut.emit('\n')
        self.bgThreadResult.emit(res)

