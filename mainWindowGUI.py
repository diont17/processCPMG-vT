# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
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

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName(_fromUtf8("mainWindow"))
        mainWindow.resize(795, 717)
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 754, 451))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lbldisplayedEcho = QtGui.QLabel(self.verticalLayoutWidget)
        self.lbldisplayedEcho.setObjectName(_fromUtf8("lbldisplayedEcho"))
        self.horizontalLayout.addWidget(self.lbldisplayedEcho)
        self.spnEcho = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.spnEcho.setObjectName(_fromUtf8("spnEcho"))
        self.horizontalLayout.addWidget(self.spnEcho)
        self.chkDoFT = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.chkDoFT.setObjectName(_fromUtf8("chkDoFT"))
        self.horizontalLayout.addWidget(self.chkDoFT)
        self.lblRangeLeft = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblRangeLeft.setObjectName(_fromUtf8("lblRangeLeft"))
        self.horizontalLayout.addWidget(self.lblRangeLeft)
        self.spnRangeLeft = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.spnRangeLeft.setObjectName(_fromUtf8("spnRangeLeft"))
        self.horizontalLayout.addWidget(self.spnRangeLeft)
        self.lblRightSide = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblRightSide.setObjectName(_fromUtf8("lblRightSide"))
        self.horizontalLayout.addWidget(self.lblRightSide)
        self.spnRangeRight = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.spnRangeRight.setObjectName(_fromUtf8("spnRangeRight"))
        self.horizontalLayout.addWidget(self.spnRangeRight)
        self.btnDoIntegrate = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnDoIntegrate.setObjectName(_fromUtf8("btnDoIntegrate"))
        self.horizontalLayout.addWidget(self.btnDoIntegrate)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.plot1Nav = QtGui.QWidget(self.verticalLayoutWidget)
        self.plot1Nav.setObjectName(_fromUtf8("plot1Nav"))
        self.verticalLayout_2.addWidget(self.plot1Nav)
        self.canvas1 = QtGui.QWidget(self.verticalLayoutWidget)
        self.canvas1.setObjectName(_fromUtf8("canvas1"))
        self.verticalLayout_2.addWidget(self.canvas1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(mainWindow)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        mainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(mainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionOpen_mat = QtGui.QAction(mainWindow)
        self.actionOpen_mat.setObjectName(_fromUtf8("actionOpen_mat"))
        self.actionOpen_Folder = QtGui.QAction(mainWindow)
        self.actionOpen_Folder.setObjectName(_fromUtf8("actionOpen_Folder"))
        self.menuMenu.addAction(self.actionOpen_mat)
        self.menuMenu.addAction(self.actionOpen_Folder)
        self.menuMenu.addAction(self.actionQuit)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "Process CPMG-vT", None))
        self.lbldisplayedEcho.setText(_translate("mainWindow", "Showing echoes from", None))
        self.chkDoFT.setText(_translate("mainWindow", "FT", None))
        self.lblRangeLeft.setText(_translate("mainWindow", "Integrate left side", None))
        self.lblRightSide.setText(_translate("mainWindow", "right side", None))
        self.btnDoIntegrate.setText(_translate("mainWindow", "Reintegrate", None))
        self.menuMenu.setTitle(_translate("mainWindow", "Menu", None))
        self.actionQuit.setText(_translate("mainWindow", "Quit", None))
        self.actionOpen_mat.setText(_translate("mainWindow", "Open .mat", None))
        self.actionOpen_Folder.setText(_translate("mainWindow", "Open Folder", None))

