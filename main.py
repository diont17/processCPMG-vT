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
from PyQt4.QtCore import QThread, SIGNAL

import mainWindowGUI
from bgFT import dataWorkerFT
from bgInteg import dataWorkerInteg
from bgT2 import dataWorkerT2

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
    
    def setupUIconnections(self, mainwindow):
        self.actionQuit.triggered.connect(self.quitApp)
        self.actionOpen_mat.triggered.connect(self.loadDataMat)
        
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
            self.dechoTimes=fileIn['echoTimes'] [0]
            self.drawData=fileIn['phasedEchoData']
            self.hasEchoData=True
            self.populateEchoes()
            self.updateFitText('Loaded from ' + path)
        else:
            self.complain('File does not exist')
            self.lastpath=path
            return -1
    
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
        
        
    def doneT2Fit(self,result):
        self.dT2Fit=result
        self.hasT2Data=True
        self.bgThread=None
        
        if self.cmbT2Fit.currentIndex() == 0:
            self.dPlotT2=result[:,np.array([0,2,4])]
            self.T2FitFunction=self.monoexponentialFit
        elif self.cmbT2Fit.currentIndex() == 1:
            self.dPlotT2=result[:,np.array([0,2,4])]
            self.T2FitFunction=self.monoexponentialFit
        
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
    
    def monoexponentialFit(self,xaxis,selectedEcho):
        return self.dPlotT2[selectedEcho,1] * np.exp(-xaxis/self.dPlotT2[selectedEcho,0]) + self.dPlotT2[selectedEcho,2]
    
    def drawRelaxation(self):
        if self.hasT2Data:
            if self.chkPlotRelaxivity.isChecked():
                self.dRelaxivity=1.0/self.dT2Fit[:,0]
                self.dRelaxivitypm= self.dT2Fit[:,0]**-2 * self.dT2Fit[1]
                self.ax3.clear()
                self.canvas2.draw()
                self.ax3.errorbar(self.dechoTimes,self.dRelaxivity,yerr=self.dRelaxivitypm[:,1])
                self.canvas2.draw()

            else:
                self.ax3.clear()
                self.canvas2.draw()
                self.ax3.errorbar(self.dechoTimes,self.dT2Fit[:,0],yerr=self.dT2Fit[:,1])
                self.canvas2.draw()
    
    
    def doRelaxationFit(self):
        #Read checkbutton state and push into fit module
        #Calculate relaxivity and push into fit module
        pass    
    
    
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
    
    def t2Fit(self,x,a,b,c):
        return (b*np.exp(-x/a))+c    
       
def main():
    app=QtGui.QApplication(sys.argv)
    form = processCPMGvtApp()
    app.setStyle('Fusion')
    form.show()
    app.exec_()

  
if __name__== "__main__":
    main()