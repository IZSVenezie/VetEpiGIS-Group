# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dbsetup_dialog_base.ui'
#
# Created: Thu Aug 18 07:07:22 2016
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(466, 336)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setMinimumSize(QtCore.QSize(85, 0))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout_3.addWidget(self.comboBox, 0, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 2, 2, 1, 1)
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit = QtGui.QLineEdit(self.tab)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.toolButton = QtGui.QToolButton(self.tab)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.gridLayout.addWidget(self.toolButton, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.commandLinkButton = QtGui.QCommandLinkButton(self.tab)
        self.commandLinkButton.setObjectName(_fromUtf8("commandLinkButton"))
        self.gridLayout_2.addWidget(self.commandLinkButton, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 81, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.gridLayout_4.addWidget(self.lineEdit_2, 0, 1, 1, 2)
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_3 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout_4.addWidget(self.lineEdit_3, 1, 1, 1, 2)
        self.label_4 = QtGui.QLabel(self.tab_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)
        self.lineEdit_4 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.gridLayout_4.addWidget(self.lineEdit_4, 2, 1, 1, 2)
        self.label_5 = QtGui.QLabel(self.tab_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_4.addWidget(self.label_5, 3, 0, 1, 1)
        self.lineEdit_5 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.gridLayout_4.addWidget(self.lineEdit_5, 3, 1, 1, 1)
        self.commandLinkButton_2 = QtGui.QCommandLinkButton(self.tab_2)
        self.commandLinkButton_2.setMaximumSize(QtCore.QSize(71, 16777215))
        self.commandLinkButton_2.setObjectName(_fromUtf8("commandLinkButton_2"))
        self.gridLayout_4.addWidget(self.commandLinkButton_2, 3, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.tab_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_4.addWidget(self.label_6, 4, 0, 1, 1)
        self.lineEdit_6 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_6.setText(_fromUtf8(""))
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.gridLayout_4.addWidget(self.lineEdit_6, 4, 1, 1, 2)
        self.label_7 = QtGui.QLabel(self.tab_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_4.addWidget(self.label_7, 5, 0, 1, 1)
        self.lineEdit_7 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_7.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.lineEdit_7.setInputMask(_fromUtf8(""))
        self.lineEdit_7.setText(_fromUtf8(""))
        self.lineEdit_7.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_7.setObjectName(_fromUtf8("lineEdit_7"))
        self.gridLayout_4.addWidget(self.lineEdit_7, 5, 1, 1, 2)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 3)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_8.setText(_translate("Dialog", "Active connection:", None))
        self.label.setText(_translate("Dialog", "Set SpatiaLite database:", None))
        self.toolButton.setText(_translate("Dialog", "...", None))
        self.commandLinkButton.setText(_translate("Dialog", "Create new SpatiaLite database", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "SpatiaLite", None))
        self.label_3.setText(_translate("Dialog", "Name:", None))
        self.lineEdit_2.setText(_translate("Dialog", "vetepigis", None))
        self.label_2.setText(_translate("Dialog", "Host:", None))
        self.lineEdit_3.setText(_translate("Dialog", "ahyghh.univet.hu", None))
        self.label_4.setText(_translate("Dialog", "Port:", None))
        self.lineEdit_4.setText(_translate("Dialog", "5432", None))
        self.label_5.setText(_translate("Dialog", "Database:", None))
        self.lineEdit_5.setText(_translate("Dialog", "vetepigisdb", None))
        self.commandLinkButton_2.setText(_translate("Dialog", "create", None))
        self.label_6.setText(_translate("Dialog", "Username:", None))
        self.label_7.setText(_translate("Dialog", "Password:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "PostgreSQL-PostGIS", None))

