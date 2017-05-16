#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 13:08:09 2017

@author: dion
"""

import numpy as np
import matplotlib as plt
import scipy
import scipy.io as sio
plt.use('Qt4Agg')
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread

import mainWindowGUI
from bgFT import dataWorkerFT
from bgInteg import dataWorkerInteg
from bgT2 import dataWorkerT2
from bgRelaxFit import dataWorkerRelaxationFit

import sys
from os.path import exists
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class processCPMGvtApp(QtGui.QMainWindow, mainWindowGUI.Ui_mainWindow):
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setupUIconnections(self)
        self.setupGraphs(self)
        
        #window vars:
        self.lastpath='/home/dion/Documents/Python/processCPMG-vT/testData/r87'
        self.hasEchoData=False
        self.hasDecayData=False
        self.hasT2Data=False
        self.hasRelaxationData=False
    
    def setupUIconnections(self, mainwindow):
        self.actionQuit.triggered.connect(self.quitApp)
        self.actionOpen_mat.triggered.connect(self.loadDataMat)
        self.actionOpen_Decay_mat.triggered.connect(self.loadDecayMat)
        self.actionSave_Decay_mat.triggered.connect(self.saveDecayMat)
        
        #Handling raw echo data
        self.spnEcho.valueChanged.connect(self.drawEchoes)
        self.spnRangeLeft.valueChanged.connect(self.drawEchoes)
        self.spnRangeRight.valueChanged.connect(self.drawEchoes)
        self.chkDoFT.stateChanged.connect(self.doFT)
        self.btnDoIntegrate.clicked.connect(self.doIntegrate)
        #Integration and T2fitting
        self.chkPlotAllEchoes.stateChanged.connect(self.drawDecays)
        self.chkShowFits.stateChanged.connect(self.drawDecays)
        self.spnEcho.valueChanged.connect(self.drawDecays)
        self.cmbT2Fit.addItem('Monoexponential')
        self.cmbT2Fit.addItem('Monoexponential (fixed c)')
        self.btnDoT2fit.clicked.connect(self.doT2Fit)
        
        #Relaxation fits
        self.chkPlotRelaxivity.stateChanged.connect(self.drawRelaxation)
        self.cmbRelaxFitType.addItem('Luz-Meiboom (from Stefanovic & Pike 2004)')
        self.cmbRelaxFitType.addItem('Jensen Chandra (from Stefanovic & Pike 2004')
        self.cmbRelaxFitType.currentIndexChanged.connect(self.nameRelaxationPar)
        self.btnDoRelaxFit.clicked.connect(self.doRelaxationFit)
        
        self.tabWidget.setCurrentIndex(0)
   
    def setupGraphs(self,mainwindow):
        self.fig1=Figure(dpi=100)
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setParent(self.tabWidget)
        self.plot1Nav = NavigationToolbar(self.canvas1,self)
        self.plot1Nav.setParent(self.tabWidget)
        self.ax1=self.fig1.add_subplot(1,2,1)
        self.ax2=self.fig1.add_subplot(1,2,2)
        self.verticalLayout_3.addWidget(self.plot1Nav)
        self.verticalLayout_3.addWidget(self.canvas1)
        
        self.fig2=Figure(dpi=100)
        self.canvas2=FigureCanvas(self.fig2)
        self.canvas2.setParent(self.tabWidget)
        self.plot2Nav=NavigationToolbar(self.canvas2,self)
        self.ax3=self.fig2.add_subplot(1,1,1)
        self.t3_vlayout.addWidget(self.plot2Nav)
        self.t3_vlayout.addWidget(self.canvas2)
    def quitApp(self):
        QtGui.QApplication.quit()
        
    def loadDataMat(self):
        path=str(QtGui.QFileDialog.getOpenFileName(self,"Select matlab CPMGvT file to load", self.lastpath, '*.mat'))
        if exists(path):
            fileIn=sio.loadmat(path)
            if 'phasedEchoData' in fileIn:
                self.dechoTimes=fileIn['echoTimes'] [0]
                self.drawData=fileIn['phasedEchoData']
                self.hasEchoData=True
                self.populateEchoes()
                self.updateFitText('Loaded from ' + path)
            else:
                self.complain('File does not contain echodata')
                    
        else:
            self.complain('File does not exist')
            self.lastpath=path
            return -1
        
    def loadDecayMat(self):
        path=str(QtGui.QFileDialog.getOpenFileName(self, "Select matlab CPMGvT file to load", self.lastpath, "*.mat"))
        if exists(path):
            fileIn=sio.loadmat(path)
            if 'decays' in fileIn:
                self.dechoTimes=fileIn['echoTimes'] [0]
                self.ddecays=fileIn['decays']
                self.dnumEchoes=self.ddecays.shape[1]
                self.dnumEchoTimes=self.dechoTimes.shape[0]
                self.spnEcho.setMaximum(self.dnumEchoTimes-1)
                self.hasDecayData=True
                if 'T2fits' in fileIn:
                    self.dT2Fit=fileIn['T2Fit'] [0]
                    self.dT2Fitpm=fileIn['T2Fitpm'] [0]
                    self.dR2=fileIn['R2'] [0]
                    self.dR2pm=fileIn['R2pm'] [0]
                    self.hasT2Data=True
                self.updateFitText('Loaded from ' + path)
            else:
                self.complain('File does not contain decay data')

                
    def saveDecayMat(self):
        path=str(QtGui.QFileDialog.getSaveFileName(self, "Save matlab CPMGvt file", self.lastpath))
        if path is None:
            return -1
        else:
            if self.hasT2Data:
                sio.savemat(path,{'echoTimes':self.dechoTimes, 'decays':self.ddecays,'T2Fit':self.dT2Fit, 'T2Fitpm':self.dT2Fitpm, 'R2':self.dR2, 'R2pm':self.dR2pm})
            else:
                sio.savemat(path,{'echoTimes':self.dechoTimes, 'decays':self.ddecays})
                
                
    def populateEchoes(self):
        if self.hasEchoData:
            self.dnumPoints=self.drawData.shape[2]
            self.dnumEchoTimes=self.drawData.shape[0]
            self.dnumEchoes=self.drawData.shape[1]
            self.spnEcho.setMinimum(0)
            self.spnEcho.setMaximum(self.dnumEchoTimes-1)
            self.spnRangeLeft.setMaximum(self.dnumPoints-1)
            self.spnRangeRight.setMaximum(self.dnumPoints-1)            
            self.ddispData=self.drawData
            self.drawEchoes()           
                        
    def drawEchoes(self):
        if self.hasEchoData:
                selectedEcho=int(self.spnEcho.value())
                curslice=self.ddispData[selectedEcho,:,:].real
                self.lblEchoTime.setText('ET: %.3es'%self.dechoTimes[selectedEcho])
                self.ax1.clear()
                self.canvas1.draw()

                self.ax1.imshow(curslice)
                self.ax1.axvline(x =  int(self.spnRangeLeft.value()), lw=1, color='red')
                self.ax1.axvline(x = int(self.spnRangeRight.value()), lw=1, color='red')
                self.ax1.set_ylabel('Echo')
                self.ax1.set_xlabel('Acq time')
                self.canvas1.draw()

    def doFT(self):
        if self.hasEchoData:
            if self.chkDoFT.isChecked():
                self.setUILocked(False)
                self.setStatusText('Starting FT thread')
                
                self.bgThread=dataWorkerFT(self.drawData)
                self.bgThread.updateprogress.connect(self.setStatusText)
                self.bgThread.bgThreadResult.connect(self.doneFT)
                self.bgThread.run()
            else:
                self.ddispData=self.drawData
                self.drawEchoes()
    
    def doneFT(self, result):
        self.dFTData=result
        self.setUILocked(False)
        self.setStatusText('Returned from FT bg work thread')
#        print(result[0,0])
#        print(self.drawData[0,0])        
        self.ddispData=self.dFTData
        self.drawEchoes()
        self.bgThread=None
        

    def doIntegrate(self):
        if self.hasEchoData:
            #Test integration range is okay, and make left edge the smaller value
            lbox=self.spnRangeLeft.value()
            rbox=self.spnRangeRight.value()
            if lbox==rbox:
                self.complain('Set nonzero integration range')
                return(-1)
            if lbox > self.dnumPoints-1 or rbox>self.dnumPoints-1 or lbox<0 or rbox<0:
                self.complain('Integration out of range')
            
            leftEdge= lbox if lbox < rbox else rbox
            rightEdge= rbox if lbox < rbox else lbox
             
            #Start data
            self.setUILocked(True)
            self.setStatusText('Starting Integrate thread')
                       
            if self.chkDoFT.isChecked():
                self.bgThread=dataWorkerInteg(self.dFTData,leftEdge,rightEdge)
            else:
                self.bgThread=dataWorkerInteg(self.drawData,leftEdge,rightEdge)
            
            self.bgThread.updateprogress.connect(self.setStatusText)
            self.bgThread.bgThreadResult.connect(self.doneIntegrate)
            self.bgThread.run()
            
    def doneIntegrate(self, result):
        #Test if result looks right
        if not (result.shape[0] == self.dnumEchoTimes and result.shape[1] ==self.dnumEchoes):       
            self.complain('Integrated wrong dimensions')
        self.ddecays=result
        self.setUILocked(False)
        
        self.hasDecayData=True
        self.hasT2Data = False
        self.drawDecays(keepView=False)
        self.bgThread=None
        
    def doT2Fit(self):
        if self.hasDecayData:
            xaxis=np.outer(self.dechoTimes,np.arange(self.dnumEchoes)+1)
            
            self.bgThread=dataWorkerT2(xaxis,self.ddecays,self.dechoTimes,int(self.cmbT2Fit.currentIndex()))
            self.setStatusText('Starting T2fit thread')
            
            self.bgThread.updateprogress.connect(self.setStatusText)
            self.bgThread.bgThreadTextOut.connect(self.updateFitText)
            self.bgThread.bgThreadResult.connect(self.doneT2Fit)
            self.bgThread.run()
        
    def doneT2Fit(self,result,resultpm):
        self.dT2Fit=result
        self.dT2Fitpm=resultpm
        self.hasT2Data=True
        self.bgThread=None
        
        if self.cmbT2Fit.currentIndex() == 0:
            self.T2FitFunction=self.monoexponentialFit
        elif self.cmbT2Fit.currentIndex() == 1:
            self.T2FitFunction=self.monoexponentialFit
        
        self.dR2=1.0/self.dT2Fit[:,0]
        self.dR2pm= self.dT2Fit[:,0]**-2 * self.dT2Fitpm[:,0]
        
        self.drawDecays(keepView=False)
        self.drawRelaxation()
    
    def updateFitText(self,txt):
        self.txtFitResults.append(txt)
        
        
    def drawDecays(self,keepView=True):
        if self.hasDecayData:
            oldvp=(self.ax2.get_xlim(),self.ax2.get_ylim())
            selectedEcho=int(self.spnEcho.value())

            self.ax2.clear()
            self.canvas1.draw()
            
            xaxis=np.outer(self.dechoTimes,np.arange(self.dnumEchoes)+1)

            if self.chkPlotAllEchoes.isChecked():
                
                for i in xrange(self.dnumEchoTimes):
                    self.ax2.plot(xaxis[i],self.ddecays[i],marker='+',markerfacecolor='grey',linewidth=1,color='grey')
                self.ax2.plot(xaxis[selectedEcho],self.ddecays[selectedEcho],markerfacecolor='red',marker='+',linewidth=1,color='red')
                
                if keepView:                
                    self.ax2.set_xlim(oldvp[0])
                    self.ax2.set_ylim(oldvp[1])
            else:
                self.ax2.plot(xaxis[selectedEcho],self.ddecays[selectedEcho,:],linestyle='None',marker='+',markeredgecolor='red')
                
            if self.hasT2Data and self.chkShowFits.isChecked():
                yfit=self.T2FitFunction(xaxis[selectedEcho],selectedEcho)
                self.ax2.plot(xaxis[selectedEcho],yfit,linewidth=1,color='green')

            self.ax2.set_xlabel('Time (s)')
            self.ax2.set_ylabel('Signal')
            self.canvas1.draw()
        
    def drawRelaxation(self,clearax=True):
        if self.hasT2Data:
            if clearax:
                self.ax3.clear()
                self.canvas2.draw()
                
            if self.chkPlotRelaxivity.isChecked():
                
                self.ax3.errorbar(self.dechoTimes,self.dR2,yerr=self.dR2pm, linestyle='None')
                
                if self.hasRelaxationData:
                    xaxis=np.linspace(self.dechoTimes[0],self.dechoTimes[-1],30)
                    self.ax3.plot(xaxis, self.RelaxationFitFunction(xaxis))
                    self.ax3.set_ylabel('R2 (s-1)')
            else:
                self.ax3.errorbar(self.dechoTimes,self.dT2Fit[:,0],yerr=self.dT2Fitpm[:,0],linestyle='None')
                if self.hasRelaxationData:
                    xaxis=np.linspace(self.dechoTimes[0],self.dechoTimes[-1],30)
                    self.ax3.plot(xaxis, 1.0/self.RelaxationFitFunction(xaxis))                
                
                self.ax3.set_ylabel('T2 (s)')
            
            self.ax3.set_xlabel('Echotime (s)')
            self.canvas2.draw()
    
    def doRelaxationFit(self):

        if self.hasT2Data:
            fittype=int(self.cmbRelaxFitType.currentIndex())
        
            fixedPar=[self.chkRxP0.isChecked(), self.chkRxP1.isChecked(), self.chkRxP2.isChecked(), self.chkRxP3.isChecked()]
            if not fixedPar[0]:
                self.txtRxP0.setText('0')
            if not fixedPar[1]:
                self.txtRxP1.setText('0')
            if not fixedPar[2]:
                self.txtRxP2.setText('0')
            if not fixedPar[3]:
                self.txtRxP3.setText('0')
            try:            
                fixedParVal=[float(self.txtRxP0.text()), float(self.txtRxP1.text()), float(self.txtRxP2.text()),float(self.txtRxP3.text())]
            except ValueError:
                self.complain('Invalid fit parameter')
                return -1
                
            self.bgThread=dataWorkerRelaxationFit(self.dechoTimes, self.dR2, self.dR2pm, fixedPar, fixedParVal, fittype)
                
            self.bgThread.updateprogress.connect(self.setStatusText)
            self.bgThread.bgThreadTextOut.connect(self.updateFitText)
            self.bgThread.bgThreadResult.connect(self.doneRelaxationFit)
            self.bgThread.run()

    def doneRelaxationFit(self,fitpar,fitparpm):

        self.dRelaxationFit=fitpar
        self.dRelaxationFitpm=fitparpm

        self.hasRelaxationData=True
        self.RelaxationFitFunction=self.LuzMeiboomFit
        self.bgThread=None

        self.drawRelaxation()
    
    def nameRelaxationPar(self):
        if self.cmbRelaxFitType.currentIndex() == 0:
            # Luz meiboom
            self.chkRxP0.setText('Exchange time (s)')
            self.chkRxP0.setEnabled(True)
            self.chkRxP1.setText('R0')
            self.chkRxP1.setEnabled(True)
            self.chkRxP2.setText('K0')
            self.chkRxP2.setEnabled(True)
            self.chkRxP3.setText('')
            self.chkRxP3.setEnabled(False)
            self.chkRxP3.setChecked(True)
        
    
    def setStatusText(self, text):
        self.statusbar.showMessage(text,0)
        
    def setUILocked(self, locked):
        if locked:
            self.btnDoIntegrate.setEnabled(False)
            self.chkDoFT.setEnabled(False)
            self.spnEcho.setEnabled(False)
            self.spnRangeLeft.setEnabled(False)
            self.spnRangeRight.setEnabled(False)
        else:
            self.btnDoIntegrate.setEnabled(True)
            self.chkDoFT.setEnabled(True)
            self.spnEcho.setEnabled(True)
            self.spnRangeLeft.setEnabled(True)
            self.spnRangeRight.setEnabled(True)
    
    def complain(self, message):
        msg=QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtGui.QMessageBox.Cancel)
        retval=msg.exec_()
    
    def monoexponentialFit(self,xaxis,selectedEcho):
        return self.dT2Fit[selectedEcho,1] * np.exp(-xaxis/self.dT2Fit[selectedEcho,0]) + self.dT2Fit[selectedEcho,2]
    
    def LuzMeiboomFit(self,xaxis):
        gamma=2.675e8
        Tex=self.dRelaxationFit[0]
        R0=self.dRelaxationFit[1]
        K0=self.dRelaxationFit[2]
        return R0 + (gamma**2 * K0 * Tex) *(1- 2*(Tex/xaxis)*np.tanh(xaxis/(2*Tex)))

       
def main():
    app=QtGui.QApplication(sys.argv)
    form = processCPMGvtApp()
    app.setStyle('Fusion')
    form.show()
    app.exec_()

  
if __name__== "__main__":
    main()