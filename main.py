#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 13:08:09 2017

@author: dion
"""

import numpy as np
import matplotlib as plt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL

import mainWindowGUI

import sys
import os.path as path
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class processCPMGvtApp(QtGui.QMainWindow, mainWindowGUI.Ui_mainWindow):
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setupUIconnections(self)
        self.setupGraphs(self)
    
    def setupUIconnections(self, mainwindow):
        self.actionQuit.triggered.connect(self.quitApp)
   
    def setupGraphs(self,mainwindow):
        self.fig1=Figure()
        self.canvas1 = FigureCanvas(self.fig1)
        self.plot1Nav = NavigationToolbar(self.canvas1,self)
        self.ax=self.fig1.add_subplot(212, axisbg='r')
        
#        self.fig2=Figure()
#        self.canvas2=FigureCanvas(self.fig2)
#        self.plot2Nav= NavigationToolbar(self.canvas2, self)
        
    def quitApp(self):
        QtGui.QApplication.quit()
    
def main():
    app=QtGui.QApplication(sys.argv)
    form = processCPMGvtApp()
    app.setStyle('Fusion')
    form.show()
    app.exec_()
    
  
if __name__== "__main__":
    main()