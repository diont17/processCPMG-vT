#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 17:10:36 2017

@author: dion
"""

import numpy as np
import scipy.optimize as opt
from scipy import integrate
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
        # P0: R0
        # P1: r_c
        # P2: G0
        
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
            fitPar=np.zeros(3)
            fitPar[0:3]=self.fixedParVal[0:3]
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
                        fitPar[1]=popt[0]
                        fitPar[2]=popt[1]
                        fitParpm[1]=np.abs(pcov[0,0]**0.5)
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)
                        
                    elif self.fixedPar[1]:
                        LM1 = lambda x,a,b: LM0(x, a, self.fixedParVal[1], b)
                        popt,pcov= opt.curve_fit(LM1, self.echoTimes, self.R2, p0=[guesses[0],guesses[2]])
                        fitPar[0]=popt[0]
                        fitPar[2]=popt[1]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)

                    elif self.fixedPar[2]:
                        LM1 = lambda x,a,b: LM0(x, a, b, self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(LM1, self.echoTimes, self.R2, p0=[guesses[0],guesses[1]])
                        fitPar[0]=popt[0]
                        fitPar[1]=popt[1]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[1]=np.abs(pcov[1,1]**0.5)

            elif numFixed==2:
                if self.fixedPar[0]:
                    if self.fixedPar[1]:
                        LM2 = lambda x,a: LM0(x,self.fixedParVal[0],self.fixedParVal[1],a)
                        popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[2])
                        fitPar[2]=popt
                        fitParpm[2]=np.abs(pcov**0.5)
                    
                    else:
                        LM2 = lambda x,a: LM0(x,self.fixedParVal[0],a,self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[1])
                        fitPar[1]=popt
                        fitParpm[1]=np.abs(pcov**0.5)
                else:
                    LM2 = lambda x,a: LM0(x, a, self.fixedParVal[1], self.fixedParVal[2])
                    popt,pcov= opt.curve_fit(LM2, self.echoTimes, self.R2, p0=guesses[0])
                    fitPar[0]=popt
                    fitParpm[0]=np.abs(pcov**0.5)

                    
            elif numFixed==3:
                pass

            def printTrue(val):
                if val:
                    return '**'
                else:
                    return ''
                

            self.bgThreadTextOut.emit('Fit R2 values to R2 = R0 + (gamma**2 * K0 * Tex) *(1- 2*(Tex/Tec)*tanh(Tec/(2*Tex)))' )
            self.bgThreadTextOut.emit('%d/3 Fixed parameters' % numFixed)            
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
            self.bgThreadTextOut.emit('\n\n')

        
            self.updateprogress.emit('Done Relaxation fitting')
            self.bgThreadResult.emit(fitPar, fitParpm)
        
        elif self.methodIndex==1: #JC Fit
            self.updateprogress.emit('Starting Relaxation Fit - Jensen Chandra')     
                       
            def JCF(x):
                #devectorised F function in JC equation
                res=np.zeros_like(x)
                for i in range(len(x)):
                    intfn=lambda y: np.exp(-y) * y**-0.5 * ( 1 - np.tanh(x[i]*y) / (x[i]*y) )
                    res[i],abserr=integrate.quad(intfn, 0, np.inf)
                return res/np.sqrt(np.pi)

#            def JCF(x):
#                intfn=lambda y: np.exp(-y) * y**-0.5 * ( 1 - np.tanh(x*y) / (x*y) )
#                integ,abserr=integrate.quad(intfn, 0, np.inf)
#                return integ/np.sqrt(np.pi)
           
            def JC0(Tec,R0,rc,G0):
                gamma=2.675e8
                D=2e3
                #D=2 um/ms, fixed
                return R0 + (G0 * gamma**2 * rc**2)/(2*D) * JCF(2*D*Tec/(rc**2))
            guesses=[5.05, 4.6, 6.6e-14]
                        
            numFixed=self.fixedPar[0] + self.fixedPar[1] +self.fixedPar[2]
            fitPar=np.zeros(3)
            fitPar[0:3]=self.fixedParVal[0:3]
#            print(fitPar)
            fitParpm=np.zeros(3)

            if numFixed==0:
                popt,pcov=opt.curve_fit(JC0, self.echoTimes, self.R2, p0=guesses)
                fitPar=popt
                fitParpm[0]=np.abs(pcov[0,0]**0.5)
                fitParpm[1]=np.abs(pcov[1,1]**0.5)
                fitParpm[2]=np.abs(pcov[2,2]**0.5)
                
            elif numFixed==1:
                    if self.fixedPar[0]:
                        JC1 = lambda x,a,b: JC0(x, self.fixedParVal[0], a, b)
                        popt,pcov= opt.curve_fit(JC1, self.echoTimes, self.R2, p0=[guesses[1],guesses[2]])
                        fitPar[1]=popt[0]
                        fitPar[2]=popt[1]
                        fitParpm[1]=np.abs(pcov[0,0]**0.5)
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)
                        
                    elif self.fixedPar[1]:
                        JC1 = lambda x,a,b: JC0(x, a, self.fixedParVal[1], b)
                        popt,pcov= opt.curve_fit(JC1, self.echoTimes, self.R2, p0=[guesses[0],guesses[2]])
                        fitPar[0]=popt[0]
                        fitPar[2]=popt[1]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[2]=np.abs(pcov[1,1]**0.5)

                    elif self.fixedPar[2]:
                        JC1 = lambda x,a,b: JC0(x, a, b, self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(JC1, self.echoTimes, self.R2, p0=[guesses[0],guesses[1]])
                        fitPar[0]=popt[0]
                        fitPar[1]=popt[1]
                        fitParpm[0]=np.abs(pcov[0,0]**0.5)
                        fitParpm[1]=np.abs(pcov[1,1]**0.5)

            elif numFixed==2:
                if self.fixedPar[0]:
                    if self.fixedPar[1]:
                        JC2 = lambda x,a: JC0(x, self.fixedParVal[0], self.fixedParVal[1], a)
                        popt,pcov= opt.curve_fit(JC2, self.echoTimes, self.R2, p0=guesses[2])
                        fitPar[2]=popt
                        fitParpm[2]=np.abs(pcov**0.5)
                    
                    else:
                        JC2 = lambda x,a: JC0(x, self.fixedParVal[0], a, self.fixedParVal[2])
                        popt,pcov= opt.curve_fit(JC2, self.echoTimes, self.R2, p0=guesses[1])
                        fitPar[1]=popt
                        fitParpm[1]=np.abs(pcov**0.5)
                else:
                    JC2 = lambda x,a: JC0(x, a, self.fixedParVal[1], self.fixedParVal[2])
                    popt,pcov= opt.curve_fit(JC2, self.echoTimes, self.R2, p0=guesses[0])
                    fitPar[0]=popt
                    fitParpm[0]=np.abs(pcov**0.5)

                    
            elif numFixed==3:
                pass

            def printTrue(val):
                if val:
                    return '**'
                else:
                    return ''
                

            self.bgThreadTextOut.emit('Fit R2 values to R2 = R0 + (G0 * gamma**2 * rc**2)/(2*D) * JCF(2*D*Tec/(rc**2))' )
            self.bgThreadTextOut.emit('%d/3 Fixed parameters' % numFixed)
            if numFixed>0:
                self.bgThreadTextOut.emit('** = Fixed value')
            self.bgThreadTextOut.emit('|{0:^10.10s}|{1:^10.10s}|{2:^10.10s}|{3:^10.10s}|{4:^10.10s}|{5:^10.10s}|'.format('R0' + printTrue(self.fixedPar[0]),'+/-','rc' + printTrue(self.fixedPar[1]),'+/-','G0' + printTrue(self.fixedPar[2]), '+/-'))
            fitString='|{0:^10.4f}|{1:^10.4f}|{2:^10.4f}|{3:^10.4f}|{4:^10.4e}|{5:^10.4e}|'.format(fitPar[0], fitParpm[0], fitPar[1], fitParpm[1], fitPar[2], fitParpm[2])
               
#           print('\nxdata\n')
#           print(self.xdataIn[i])
#           print('\nydata\n')
#           print(self.ydataIn[i])
#           print(fitData[i])
                
            self.bgThreadTextOut.emit(fitString)
            self.bgThreadTextOut.emit('\n\n')

        
        self.updateprogress.emit('Done Relaxation fitting')
        self.bgThreadResult.emit(fitPar, fitParpm)
