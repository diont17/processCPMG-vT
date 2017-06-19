# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'REA.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        REAWindow.resize(482, 207)
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblBlank = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblBlank.setObjectName(_fromUtf8("lblBlank"))
        self.horizontalLayout.addWidget(self.lblBlank)
        self.txtBlank = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.txtBlank.setObjectName(_fromUtf8("txtBlank"))
        self.horizontalLayout.addWidget(self.txtBlank)
        self.btnSelectBlank = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnSelectBlank.setObjectName(_fromUtf8("btnSelectBlank"))
        self.horizontalLayout.addWidget(self.btnSelectBlank)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.chkUseBlank = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.chkUseBlank.setObjectName(_fromUtf8("chkUseBlank"))
        self.horizontalLayout_2.addWidget(self.chkUseBlank)
        self.lblStatus = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblStatus.setText(_fromUtf8(""))
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.horizontalLayout_2.addWidget(self.lblStatus)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnQuit = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.horizontalLayout_2.addWidget(self.btnQuit)
        self.btnLoad = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnLoad.setObjectName(_fromUtf8("btnLoad"))
        self.horizontalLayout_2.addWidget(self.btnLoad)
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setEnabled(False)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        REAWindow.setCentralWidget(self.verticalLayoutWidget)

        self.retranslateUi(REAWindow)
        QtCore.QMetaObject.connectSlotsByName(REAWindow)

    def retranslateUi(self, REAWindow):
        REAWindow.setWindowTitle(_translate("REAWindow", "Read raw echo data- CPMGvariableTau", None))
        self.label.setText(_translate("REAWindow", "Input folder", None))
        self.btnSelectFolder.setText(_translate("REAWindow", "Select Folder", None))
        self.lblBlank.setText(_translate("REAWindow", "Blank folder", None))
        self.btnSelectBlank.setText(_translate("REAWindow", "Select Folder", None))
        self.label_3.setText(_translate("REAWindow", "Output file", None))
        self.btnSelectFile.setText(_translate("REAWindow", "Save", None))
        self.chkUseBlank.setText(_translate("REAWindow", "Use Blank", None))
        self.btnQuit.setText(_translate("REAWindow", "Quit", None))
        self.btnLoad.setText(_translate("REAWindow", "Load", None))
        self.pushButton.setText(_translate("REAWindow", "Process", None))

