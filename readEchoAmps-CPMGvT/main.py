import sys
from os.path import getmtime, exists

from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import QThread, SIGNAL
import readEchoAmpsGui

import numpy as np
import scipy.optimize as opt
import scipy.io as sio

class reaApp(QtGui.QMainWindow, readEchoAmpsGui.Ui_REAWindow):

    def __init__(self, parent=None):
        super(reaApp, self).__init__(parent)
        self.setupUi(self)
        
        
        self.btnSelectFolder.clicked.connect(self.browseFolder)
        self.btnSelectBlank.clicked.connect(self.browseBlank)
        self.btnSelectFile.clicked.connect(self.browseOutputFile)
        self.hasData=False
        self.hasBlank=False
        self.btnQuit.clicked.connect(self.quitApp)
        self.btnLoad.clicked.connect(self.userOK)
        self.lastPath='/home/dion/Documents/Experimental Data'
        
    def browseFolder(self):
        path=QtGui.QFileDialog.getExistingDirectory(self,"Select folder with data",directory=self.lastPath)
        if exists(path + '/echoTimes.csv'):
           self.inFolder.setText(path)
           self.lastPath=path
           ET=np.loadtxt(str(path+'/echoTimes.csv'), delimiter=',')*1e-6
           self.lblStatus.setText('{} Echoes: ET {:.2e} ->{:.2e}'.format(ET.shape[0],ET[0],ET[-1]))
        elif path == None:
            return
        else:
            self.complain(complaint = 'Couldn\'t find echoTimes.csv')

    def browseBlank(self):
        path=QtGui.QFileDialog.getExistingDirectory(self,"Select folder with Blank data",directory=self.lastPath)
        if exists(path + '/echoTimes.csv'):
           self.txtBlank.setText(path)
           self.lastPath=path
           ET=np.loadtxt(str(path+'/echoTimes.csv'), delimiter=',')*1e-6
           self.lblStatus.setText('{} Echoes: ET {:.2e} ->{:.2e}'.format(ET.shape[0],ET[0],ET[-1]))
        elif path == None:
            return
        else:
            self.complain(complaint = 'Couldn\'t find echoTimes.csv')

    def browseOutputFile(self):
        path=QtGui.QFileDialog.getSaveFileName(self, "Name and path of output matlab file",directory=self.lastPath)
        if path:
            if not path.endsWith('.mat'):
                path = path+'.mat'
            self.outFile.setText(path)
    
    def quitApp(self):
        QtGui.QApplication.exit()
    
    def userOK(self):
        if self.inFolder.text() == "" or self.outFile.text()=="":
            self.complain(complaint = 'Missing folder / save location')
            return
        
        if self.chkUseBlank.isChecked():
            ETdata = np.loadtxt(str(self.inFolder.text())+'/echoTimes.csv')
            ETblank = np.loadtxt(str(self.txtBlank.text()) + '/echoTimes.csv')
        
            if not np.array_equal(ETdata,ETblank):
                self.complain(complaint = "Blank & data echoTimes don't match")
                return
            self.workThread = dataWorker(self.inFolder.text(), self.outFile.text(), self.txtBlank.text())
        
        else:
            self.workThread=dataWorker(self.inFolder.text(),self.outFile.text())
        
        self.connect(self.workThread,SIGNAL("finished()"),self.done )
        self.connect(self.workThread,SIGNAL("updateprogress(QString)"), self.doprogress)
        self.workThread.start()
    
    def done(self):
        self.btnLoad.setEnabled(True)
            
    def complain(self, complaint = ""):
        msg=QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.setText("Invalid Parameter:\n" + complaint)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtGui.QMessageBox.Cancel)
        retval=msg.exec_()
        
    def doprogress(self,message):
        self.lblStatus.setText(message)


class dataWorker(QtCore.QThread):
    
    def __init__(self,pathin,pathout,pathBlank=None):
        QtCore.QThread.__init__(self)
        self.fnameIn = pathin
        self.fnameOut = pathout
        self.fnameBlank = pathBlank
        
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
        #Get rid of any of that QString stuff..
        fnameIn = str(self.fnameIn)
        fnameOut = str(self.fnameOut)
        if self.fnameBlank is not None:
            fnameBlank = str(self.fnameBlank)
        else:
            fnameBlank = None
        
        
        echoTimes = 1e-6*np.loadtxt(fnameIn+'/echoTimes.csv')
        numEchoTimes = echoTimes.shape[0]
        i = 1
        #Test if all files exist
        for i in xrange(numEchoTimes):
            if (not exists(fnameIn+'/ET%1d.csv'%i)):
                self.emit(SIGNAL("updateprogress(QString)"), 'Failed, missing ET%1d'%i)
                return 1
        self.emit(SIGNAL("updateprogress(QString)"),'Found %d files'%i)
        
        #Get dimensions for experiment data
        rawEA=np.loadtxt(fnameIn+'/ET%d.csv'%1, delimiter=',',dtype=np.complex)
        
        #For real Prospa data (doesnt export a+bj format data)
        numEchoes=rawEA.shape[0]
        numPoints=rawEA.shape[1]/2
#        numEchoes=rawEA.shape[0]
#        numPoints=rawEA.shape[1]
        
        #Make data array
        fullData=np.zeros((numEchoTimes,numEchoes,numPoints),dtype=np.complex)
                
        for i in xrange(0,numEchoTimes):
            rawEA=np.loadtxt(fnameIn+'/ET%1d.csv'%(i),delimiter=',',dtype=np.complex)
            
            realEA=rawEA[:,::2]
            imagEA=rawEA[:,1::2]
            fullData[i,:,:]=realEA+1j*imagEA
            
#            fullData[i,:,:]=rawEA[:,:]
            self.emit(SIGNAL("updateprogress(QString)"),'Loaded %d of %d'%(i,numEchoTimes))
        
        def sumCplx(ph,a): return np.sum( ((np.exp(2j*np.pi*ph/360.0) * a).imag)**2)
        def phaseByMinCplx(a):
            """Simple method to automatically get phase angle by minimizing sum of imaginary data points squared"""
        
            res = opt.minimize(fun=sumCplx,x0=[180],args=(a),bounds=[(0,360)],options={'disp':False})
        #    print(res)
            if res.success:
                return float(res.x)
            else: return 0
            
            
        self.emit(SIGNAL("updateprogress(QString)"),'Phasing data')            
        phase=phaseByMinCplx(fullData[0,0,:])
        phase=0
        fullData*=np.exp((phase/360.0)*2j*np.pi)
        
        blankData = np.zeros((numEchoTimes,numEchoes,numPoints),dtype=np.complex)
        if fnameBlank is not None:
            for i in xrange(0,numEchoTimes):
                blankEA = np.loadtxt(fnameBlank + '/ET%1d.csv'%i, delimiter=',', dtype=np.complex)
                realEA = blankEA[:, ::2]
                imagEA = blankEA[:, 1::2]
                blankData[i,:,:] = realEA + 1j*imagEA
                self.emit(SIGNAL("updateprogress(QString)"),'Loaded blank %d of %d'%(i,numEchoTimes))

        blankPhase = 0#phaseByMinCplx(blankData[0,0,:])
        blankData*=np.exp((blankPhase/360.0)*2j*np.pi)
        
        fullData[:,:,:] -= blankData[:,:,:]
        
        self.emit(SIGNAL("updateprogress(QString)"),'Saving')
        
        sio.savemat(fnameOut,{'phasedEchoData':fullData,'echoTimes':echoTimes})
        
        self.emit(SIGNAL("updateprogress(QString)"),'Done')

def main():
    app=QtGui.QApplication(sys.argv)
    form=reaApp()
    form.show()
    app.setStyle('Fusion')
    app.exec_()

if __name__ == '__main__':
    main()
    