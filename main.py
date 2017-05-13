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
import dataWorkerFT
from dataWorkerInteg import dataWorkerInteg

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
    
    def setupUIconnections(self, mainwindow):
        self.actionQuit.triggered.connect(self.quitApp)
        self.actionOpen_mat.triggered.connect(self.loadDataMat)
        
        #Handling raw echo data
        self.spnEcho.valueChanged.connect(self.drawEchoes)
        self.spnRangeLeft.valueChanged.connect(self.drawEchoes)
        self.spnRangeRight.valueChanged.connect(self.drawEchoes)
        self.chkDoFT.stateChanged.connect(self.doFT)
        self.btnDoIntegrate.clicked.connect(self.doIntegrate)
        #Integration and fitting
        self.chkPlotAllEchoes.stateChanged.connect(self.drawDecays)
        self.spnEcho.valueChanged.connect(self.drawDecays)
        
   
    def setupGraphs(self,mainwindow):
        self.fig1=Figure(dpi=100)
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setParent(self.centralwidget)
        self.plot1Nav = NavigationToolbar(self.canvas1,self)
        self.plot1Nav.setParent(self.centralwidget)
        self.ax1=self.fig1.add_subplot(1,2,1)
        self.ax2=self.fig1.add_subplot(1,2,2)
        self.verticalLayout_2.addWidget(self.plot1Nav)
        self.verticalLayout_2.addWidget(self.canvas1)
        
    def quitApp(self):
        QtGui.QApplication.quit()
        
    def loadDataMat(self):
        path=str(QtGui.QFileDialog.getOpenFileName(self,"Select matlab CPMGvT file to load", self.lastpath, '*.mat'))
        if not exists(path):
            self.complain('File does not exist')
            self.lastpath=path
            return -1
        else:
            fileIn=sio.loadmat(path)
            self.dechoTimes=fileIn['echoTimes'] [0]
            self.drawData=fileIn['phasedEchoData']
            self.hasEchoData=True
            self.populateEchoes()
    
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
                
                self.bgThread=dataWorkerFT.dataWorkerFT(self.drawData)
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
        self.drawDecays(keepView=False)
        self.bgThread=None
        
        
    def drawDecays(self,keepView=True):
        if self.hasDecayData:
            oldvp=(self.ax2.get_xlim(),self.ax2.get_ylim())
            selectedEcho=int(self.spnEcho.value())
            self.ax2.clear()
            self.canvas1.draw()
            
            if self.chkPlotAllEchoes.isChecked():
                xaxis=np.outer(self.dechoTimes,np.arange(self.dnumEchoes)+1)
                for i in xrange(self.dnumEchoTimes):
                    self.ax2.plot(xaxis[i],self.ddecays[i],marker='+',markerfacecolor='grey',linewidth=1,color='grey')
                self.ax2.plot(xaxis[selectedEcho],self.ddecays[selectedEcho],markerfacecolor='red',marker='+',linewidth=1,color='red')
                if keepView:                
                    self.ax2.set_xlim(oldvp[0])
                    self.ax2.set_ylim(oldvp[1])
            else:
                xaxis=np.arange(self.dnumEchoes) * self.dechoTimes[selectedEcho]
                self.ax2.plot(xaxis,self.ddecays[selectedEcho,:],linestyle='None',marker='+',markeredgecolor='red')                
            self.ax2.set_xlabel('Time (s)')
            self.ax2.set_ylabel('Signal')
            self.canvas1.draw()
    
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
        
       
def main():
    app=QtGui.QApplication(sys.argv)
    form = processCPMGvtApp()
    app.setStyle('Fusion')
    form.show()
    app.exec_()
    
  
if __name__== "__main__":
    main()