#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 12:29:11 2017

@author: dion
"""

import numpy as np
import scipy.fftpack as fft
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL


class dataWorkerInteg(QtCore.QThread):
    bgThreadResult=QtCore.pyqtSignal(np.ndarray)
    updateprogress=QtCore.pyqtSignal(QtCore.QString)
    def __init__(self,dataIn,leftEdge,rightEdge):
        QtCore.QThread.__init__(self)
        self.dataIn=dataIn.real
        self.numEchoTimes=dataIn.shape[0]
        self.numEchoes=dataIn.shape[1]
        self.leftEdge=leftEdge
        self.rightEdge=rightEdge
        
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
        self.updateprogress.emit('Integrating echos, sum')
        decays=np.sum(self.dataIn[:,:,self.leftEdge:self.rightEdge],axis=2)            
        self.updateprogress.emit('Done')
        self.bgThreadResult.emit(decays)