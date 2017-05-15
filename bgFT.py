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

class dataWorkerFT(QtCore.QThread):
    bgThreadResult=QtCore.pyqtSignal(np.ndarray)
    updateprogress=QtCore.pyqtSignal(QtCore.QString)
    def __init__(self,dataIn):
        QtCore.QThread.__init__(self)
        self.dataIn=dataIn
        
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
#        self.emit(SIGNAL("updateprogress(QString)"),'Running FT')
        self.updateprogress.emit('Running FT')
        phasedDataFT=fft.fftshift(fft.fft(fft.fftshift(self.dataIn,axes=2),axis=2),axes=2) #Echo, so needs to be shift/rotated
        self.updateprogress.emit('Done')
#        self.emit(SIGNAL("updateprogress(QString)"),'Done')
        self.bgThreadResult.emit(phasedDataFT)