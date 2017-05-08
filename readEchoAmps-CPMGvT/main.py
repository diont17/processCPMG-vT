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
        self.btnSelectFile.clicked.connect(self.browseOutputFile)
        self.btnQuit.clicked.connect(self.quitApp)
        self.btnLoad.clicked.connect(self.userOK)
        self.lastPath='/home/dion/Documents/Experimental Data'
        
    def browseFolder(self):
        path=QtGui.QFileDialog.getExistingDirectory(self,"Select folder with data",directory=self.lastPath)
        if exists(path + '/echoTimes.csv'):
           self.inFolder.setText(path)
           self.lastPath=path
           ET=np.loadtxt(str(path+'/echoTimes.csv'), delimiter=',')
           self.lblStatus.setText('{} Echoes: ET {:2e} ->{:2e}'.format(ET.shape[0],ET[0],ET[-1]))
        else:
            self.complain()

    def browseOutputFile(self):
        path=QtGui.QFileDialog.getSaveFileName(self, "Name and path of output matlab file",directory=self.lastPath)
        if path:
            self.outFile.setText(path)
    
    def quitApp(self):
        QtGui.QApplication.exit()
    
    def userOK(self):
        if self.inFolder.text() == "" or self.outFile.text()=="":
            self.complain()
            return
        if bool(self.chkDoAverage.isChecked()) and self.numAverages.value()==0:
            self.complain()
            return
            
        self.btnLoad.setEnabled(False)
        
        self.workThread=dataWorker(self.inFolder.text(),self.outFile.text(),self.chkDoAverage.isChecked(),self.numAverages.value())
        self.connect(self.workThread,SIGNAL("finished()"),self.done )
        self.connect(self.workThread,SIGNAL("updateprogress(QString)"), self.doprogress)
        self.workThread.start()
    
    def done(self):
#        QtGui.QMessageBox.about(self,'Done!','Done')
        self.btnLoad.setEnabled(True)
            
    def complain(self):
        msg=QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.setText("Invalid Parameter")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtGui.QMessageBox.Cancel)
        retval=msg.exec_()
        
    def doprogress(self,message):
        self.lblStatus.setText(message)


class dataWorker(QtCore.QThread):
    
    def __init__(self,pathin,pathout,doaverage,avgpp):
        QtCore.QThread.__init__(self)
        self.fnameIn=pathin
        self.fnameOut=pathout
        self.doAverage=doaverage
        self.averagesPerPoint=avgpp
    
    def __del__(self):
        self.wait()
    
    def run(self):
        self.process()

    def process(self):    
        #Get rid of any of that QString stuff..
        fnameIn=str(self.fnameIn)
        fnameOut=str(self.fnameOut)
        doAverage=bool(self.doAverage)
        averagesPerPoint=int(self.averagesPerPoint)

        #scan folder to get number of measures
        echoTimes=np.loadtxt(fnameIn+'/echoTimes.csv')
        i=1
        for i in range(echoTimes.shape[0]):
            
            numMeasures=i-1
        self.emit(SIGNAL("updateprogress(QString)"),'Found %d files'%numMeasures)
        
        #Get dimensions for experiment data
        rawEA=np.loadtxt(fnameIn+'/echoAmps%d.csv'%1, delimiter=',')
        numEchoes=rawEA.shape[0]
        numPoints=rawEA.shape[1]/2
        
        #make array to rebuild measure acq time
        measureTime=np.zeros(numMeasures)
        measureTime0=getmtime(fnameIn+'/echoAmps%d.csv'%1)
        echoAmpsX=1e-3*np.loadtxt(fnameIn+'/echoAmpXaxis.csv')
        
        #Make data array
        fullData=np.zeros((numMeasures,numEchoes,numPoints),dtype=np.complex)
        
        for i in xrange(0,numMeasures):
            rawEA=np.loadtxt(fnameIn+'/echoAmps%d.csv'%(i+1),delimiter=',')
            realEA=rawEA[:,::2]
            imagEA=rawEA[:,1::2]
            fullData[i,:,:]=realEA+1j*imagEA
            measureTime[i]=getmtime(fnameIn+'/echoAmps%d.csv'%(i+1))-measureTime0
            self.emit(SIGNAL("updateprogress(QString)"),'Loaded %d of %d'%(i,numMeasures))
        print fullData.shape      
        
        if doAverage:
            #Setup index array to select the measures to be averaged, outputs an array with [# of averaged points,# of averaged,numEchoes,numPoints]
            avgIndex=np.arange((averagesPerPoint)*(numMeasures/averagesPerPoint))
            avgIndex.shape=((numMeasures/averagesPerPoint),averagesPerPoint)

            reAverageData=fullData.take(avgIndex,axis=0,mode='clip')
            reAverage= (1.0/float(avgIndex.shape[1])) * np.sum(reAverageData,axis=1)
        
            del(reAverageData)
            reAverageMeasureTime=measureTime[avgIndex[:,3]]

        
        def sumCplx(ph,a): return np.sum( ((np.exp(2j*np.pi*ph/360.0) * a).imag)**2)
        def phaseByMinCplx(a):
            """Simple method to automatically get phase angle by minimizing sum of imaginary data points squared"""
        
            res = opt.minimize(fun=sumCplx,x0=[180],args=(a),bounds=[(0,360)],options={'disp':False})
        #    print(res)
            if res.success:
                return float(res.x)
            else: return 0
            
            
        self.emit(SIGNAL("updateprogress(QString)"),'Phasing data')            
        if doAverage:
            phase=phaseByMinCplx(reAverage[0,1,:])
            reAverage*=np.exp((phase/360.0)*2j*np.pi)
        else:
            phase=phaseByMinCplx(fullData[0,1,:])
            
        fullData*=np.exp((phase/360.0)*2j*np.pi)
        
        
        self.emit(SIGNAL("updateprogress(QString)"),'Saving')
        
        if doAverage:
            sio.savemat(fnameOut+' %dAvg.mat'%averagesPerPoint,{'phasedEchoData':reAverage,'echoCentreTime':echoAmpsX,'measureTime':reAverageMeasureTime}, )
            print 'data shape:'
            print reAverage.shape
            print echoAmpsX.shape
            print reAverageMeasureTime.shape
        else:
            sio.savemat(fnameOut+' Phased.mat',{'phasedEchoData':fullData,'echoCentreTime':echoAmpsX,'measureTime':measureTime})
        
        self.emit(SIGNAL("updateprogress(QString)"),'Done')

def main():
    app=QtGui.QApplication(sys.argv)
    form=reaApp()
    form.show()
    app.setStyle('Fusion')
    app.exec_()

if __name__ == '__main__':
    main()
    