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
        self.hasData=False
    
    def setupUIconnections(self, mainwindow):
        self.actionQuit.triggered.connect(self.quitApp)
        self.actionOpen_mat.triggered.connect(self.loadDataMat)
        
        self.spnEcho.valueChanged.connect(self.drawEchoes)
        self.spnRangeLeft.valueChanged.connect(self.drawEchoes)
        self.spnRangeRight.valueChanged.connect(self.drawEchoes)
        self.chkDoFT.stateChanged.connect(self.doFT)
        
   
    def setupGraphs(self,mainwindow):
        self.fig1=Figure(dpi=100)
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setParent(self.verticalLayoutWidget)
        self.plot1Nav = NavigationToolbar(self.canvas1,self)
        self.plot1Nav.setParent(self.verticalLayoutWidget)
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
            self.hasData=True
            self.populateEchoes()
    
    def populateEchoes(self):
        if self.hasData:
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
        if self.hasData:
                selectedEcho=int(self.spnEcho.value())
                curslice=self.ddispData[selectedEcho,:,:].real
                self.lblEchoTime.setText('ET: %.3es'%self.dechoTimes[selectedEcho])
                self.ax1.clear()
                self.canvas1.draw()

                self.ax1.imshow(curslice)
                self.ax1.axvline(x =  int(self.spnRangeLeft.value()), lw=1, color='red')
                self.ax1.axvline(x = int(self.spnRangeRight.value()), lw=1, color='red')
                self.canvas1.draw()

    def doFT(self):
        if self.hasData:
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