#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 17:10:36 2017

@author: dion
"""

import numpy as np
import scipy.optimize as opt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL

class dataWorkerRelaxationFit(QtCore.QThread):
    bgThreadResult=QtCore.pyqtSignal(np.ndarray,np.ndarray)
    bgThreadTextOut=QtCore.pyqtSignal(QtCore.QString)
    updateprogress=QtCore.pyqtSignal(QtCore.QString)
    
    def __init__(self, echoTimes, R2, R2pm, fixedPar, fixedParVal, methodIndex):
        QtCore.QThread.__init__(self)
        self.echoTimes=echoTimes
        self.R2 = R2
        self.R2pm = R2pm
        self.fixedPar = fixedPar
        self.fixedParVal = fixedParVal
        self.methodIndex=methodIndex 
        
        #0 - Luz/Meiboom
        # P0: Exchange time
        # P1: R0
        # P2: K0
        
        
        #1 - Jensen/Chandra
        
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
        if self.methodIndex==0:
            self.updateprogress.emit('Starting Relaxation Fit - Luz-Meiboom')            
            def LM0(Tec,Tex,R0,K0):
                gamma=2.675e8
                return R0 + (gamma**2 * K0 * Tex) *(1- 2*(Tex/Tec)*np.tanh(Tec/(2*Tex)))
            guesses=[5.05, 3e-3, 0.5e-14]
            
            numFixed=self.fixedPar[0] + self.fixedPar[1] +self.fixedPar[2]
            self.updateprogress.emit('%d Free parameters' % numFixed)            
            fitPar=np.zeros(3)
            fitParpm=np.zeros(3)

            if numFixed==0:
                popt,pcov=opt.curve_fit(LM0, self.echoTimes, self.R2, p0=guesses)
                fitPar=popt
                fitParpm[0]=np.abs(pcov[0,0]**0.5)
                fitParpm[1]=np.abs(pcov[1,1]**0.5)
                fitParpm[2]=np.abs(pcov[2,2]**0.5)
                
            elif numFixed==1:
                    if self.fixedPar[0]:
                        LM1 = lambda x,a,b: LM0(x, self.fixedParVal[0], a, b)
                        popt,pcov= opt.curve_fit(LM1, self.echoTimes, self.R2, p0=[guesses[1],guesses[2]])
                        fitPar[0]=self.fixedParVal[0]
                        fitPar[1]=popt[0]
                        fitPar[2]=popt[1]
                        fitParpm[0]=0
                        fitParpm[1]=np.abs(pcov[0,0]**0.5)
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)
                        
                    elif self.fixedPar[1]:
                        LM1 = lambda x,a,b: LM0(x, a, self.fixedParVal[1], b)
                        popt,pcov= opt.curve_fit(LM1, self.echoTimes, self.R2, p0=[guesses[0],guesses[2]])
                        fitPar[0]=popt[0]
                        fitPar[1]=self.fixedParVal[1]
                        fitPar[2]=popt[1]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[1]=0
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)

                    elif self.fixedPar[2]:
                        LM1 = lambda x,a,b: LM0(x, a, b, self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(LM1, self.echoTimes, self.R2, p0=[guesses[0],guesses[1]])
                        fitPar[0]=popt[0]
                        fitPar[1]=popt[1]
                        fitPar[2]=self.fixedParVal[2]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[1]=np.abs(pcov[1,1]**0.5)
                        fitParpm[2]=0
           
            elif numFixed==2:
                if self.fixedPar[0]:
                    if self.fixedPar[1]:
                        LM2 = lambda x,a: LM0(x,self.fixedParVal[0],self.fixedParVal[1],a)
                        popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[2])
                        fitPar[0]=self.fixedParVal[0]
                        fitPar[1]=self.fixedParVal[1]
                        fitPar[2]=popt
                        fitParpm[0]=0
                        fitParpm[1]=0                    
                        fitParpm[2]=np.abs(pcov**0.5)
                    
                    else:
                        LM2 = lambda x,a: LM0(x,self.fixedParVal[0],a,self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[1])
                        fitPar[0]=self.fixedParVal[0]
                        fitPar[1]=popt
                        fitPar[2]=self.fixedParVal[2]
                        fitParpm[0]=0
                        fitParpm[1]=np.abs(pcov**0.5)
                        fitParpm[2]=0
                else:
                    LM2 = lambda x,a: LM0(x, a, self.fixedParVal[1], self.fixedParVal[2])
                    popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[0])
                    fitPar[0]=popt
                    fitPar[1]=self.fixedParVal[1]
                    fitPar[2]=self.fixedParVal[2]
                    fitParpm[0]=np.abs(pcov**0.5)
                    fitParpm[1]=0
                    fitParpm[2]=0
                    
            elif numFixed==3:
                fitPar[0]=self.fixedParVal[0]
                fitPar[1]=self.fixedParVal[1]
                fitPar[2]=self.fixedParVal[2]
                fitParpm=np.zeros(3)

            def printTrue(val):
                if val:
                    return '**'
                else:
                    return ''
                

            self.bgThreadTextOut.emit('Fit decays to  R0 + (gamma**2 * K0 * Tex) *(1- 2*(Tex/Tec)*tanh(Tec/(2*Tex)))' )
            if numFixed>0:
                self.bgThreadTextOut.emit('** = Fixed value')
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}|'.format('Tex' + printTrue(self.fixedPar[0]),'+/-','R0' + printTrue(self.fixedPar[1]),'+/-','K0' + printTrue(self.fixedPar[2]), '+/-'))
            fitString='|{0:^10.4f}|{1:^10.4f}|{2:^10.4f}|{3:^10.4f}|{4:^10.4e}|{5:^10.4e}|'.format(fitPar[0], fitParpm[0], fitPar[1], fitParpm[1], fitPar[2], fitParpm[2])
               
#           print('\nxdata\n')
#           print(self.xdataIn[i])
#           print('\nydata\n')
#           print(self.ydataIn[i])
#           print(fitData[i])
                
            self.bgThreadTextOut.emit(fitString)
                
        
        self.updateprogress.emit('Done Relaxation fitting')
        self.bgThreadResult.emit(fitPar, fitParpm)

