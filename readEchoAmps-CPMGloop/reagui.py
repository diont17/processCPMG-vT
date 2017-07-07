# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'REA.ui'
#
# Created: Tue Jan 10 17:58:11 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_REAWindow(object):
    def setupUi(self, REAWindow):
        REAWindow.setObjectName(_fromUtf8("REAWindow"))
        REAWindow.resize(482, 191)
        self.verticalLayoutWidget = QtGui.QWidget(REAWindow)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.inFolder = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.inFolder.setText(_fromUtf8(""))
        self.inFolder.setObjectName(_fromUtf8("inFolder"))
        self.horizontalLayout_3.addWidget(self.inFolder)
        self.btnSelectFolder = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnSelectFolder.setObjectName(_fromUtf8("btnSelectFolder"))
        self.horizontalLayout_3.addWidget(self.btnSelectFolder)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_3 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_4.addWidget(self.label_3)
        self.outFile = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.outFile.setObjectName(_fromUtf8("outFile"))
        self.horizontalLayout_4.addWidget(self.outFile)
        self.btnSelectFile = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout_4.addWidget(self.btnSelectFile)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chkDoAverage = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.chkDoAverage.setObjectName(_fromUtf8("chkDoAverage"))
        self.horizontalLayout.addWidget(self.chkDoAverage)
        self.label_2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.numAverages = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.numAverages.setObjectName(_fromUtf8("numAverages"))
        self.horizontalLayout.addWidget(self.numAverages)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblStatus = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.horizontalLayout_2.addWidget(self.lblStatus)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnQuit = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.horizontalLayout_2.addWidget(self.btnQuit)
        self.btnRun = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.horizontalLayout_2.addWidget(self.btnRun)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        REAWindow.setCentralWidget(self.verticalLayoutWidget)

        self.retranslateUi(REAWindow)
        QtCore.QMetaObject.connectSlotsByName(REAWindow)

    def retranslateUi(self, REAWindow):
        REAWindow.setWindowTitle(_translate("REAWindow", "Read raw echo data", None))
        self.label.setText(_translate("REAWindow", "Input folder", None))
        self.btnSelectFolder.setText(_translate("REAWindow", "Select Folder", None))
        self.label_3.setText(_translate("REAWindow", "Output file", None))
        self.btnSelectFile.setText(_translate("REAWindow", "Save", None))
        self.chkDoAverage.setText(_translate("REAWindow", "Average", None))
        self.label_2.setText(_translate("REAWindow", "Measurements to average", None))
        self.lblStatus.setText(_translate("REAWindow", "  ", None))
        self.btnQuit.setText(_translate("REAWindow", "Quit", None))
        self.btnRun.setText(_translate("REAWindow", "Run", None))

