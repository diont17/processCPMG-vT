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

class dataWorkerT2(QtCore.QThread):
    bgThreadResult=QtCore.pyqtSignal(np.ndarray)
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
            fitData=np.zeros((self.numSequences,5))
            
            def t2Fit(x,t2,a,c):
                return (a*np.exp(-x/t2))+c
            self.bgThreadTextOut.emit('Fit decays to  A*exp(-x/T2) + c' )
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}|{6:^10.10s}|'.format('#','Echotime','T2','+/-','A','+/-','c'))
            for i in xrange(self.numSequences):
                popt,pcov=opt.curve_fit(t2Fit,self.xdataIn[i,:],self.ydataIn[i,:],p0=[0.1,120,0])
                fitData[i,0]=popt[0]
                fitData[i,1]=np.abs(pcov[0][0]**0.5)
                fitData[i,2]=popt[1]
                fitData[i,3]=np.abs(pcov[1][1]**0.5)
                fitData[i,4]=popt[2]
                fitString='|{0:^10d}|{1:^10.3e}|{2:^10.4f}|{3:^10.4f}|{4:^10.4f}|{5:^10.4f}|{6:^10.4f}|'.format(i,self.echoTimes[i],*fitData[i])
               
#                print('\nxdata\n')
#                print(self.xdataIn[i])
#                print('\nydata\n')
#                print(self.ydataIn[i])
#                print(fitData[i])
                
                self.bgThreadTextOut.emit(fitString)
                self.updateprogress.emit('Fit %d of %d'%(i,self.numSequences))
                
        elif self.methodIndex==1:
            fitData=np.zeros((self.numSequences,5))
            
            def t2Fit(x,t2,a):
                return (a*np.exp(-x/t2))
            self.bgThreadTextOut.emit('Fit decays to  A*exp(-x/T2)' )
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}'.format('#','Echotime','T2','+/-','A','+/-'))
            for i in xrange(self.numSequences):
                popt,pcov=opt.curve_fit(t2Fit,self.xdataIn[i,:],self.ydataIn[i,:],p0=[0.1,120])
                fitData[i,0]=popt[0]
                fitData[i,1]=np.abs(pcov[0][0]**0.5)
                fitData[i,2]=popt[1]
                fitData[i,3]=np.abs(pcov[1][1]**0.5)
                fitData[i,4]=0
                fitString='|{0:^10d}|{1:^10.3e}|{2:^10.4f}|{3:^10.4f}|{4:^10.4f}|{5:^10.4f}|'.format(i,self.echoTimes[i],*fitData[i])
               
#                print('\nxdata\n')
#                print(self.xdataIn[i])
#                print('\nydata\n')
#                print(self.ydataIn[i])
#                print(fitData[i])
                
                self.bgThreadTextOut.emit(fitString)
                self.updateprogress.emit('Fit %d of %d'%(i,self.numSequences))

        
        self.updateprogress.emit('Done T2 fitting')
        self.bgThreadResult.emit(fitData)

