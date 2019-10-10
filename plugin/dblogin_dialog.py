# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'merge_dialog_base.ui'
#
# Created: Mon May 15 11:05:12 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(250, 131)

        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.label_user = QtWidgets.QLabel(Dialog)
        self.label_user.setObjectName(_fromUtf8("label_user"))
        self.gridLayout.addWidget(self.label_user, 0, 0, 1, 1)

        self.lineEdit_user = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_user.setReadOnly(False)
        self.lineEdit_user.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit_user, 0, 1, 1, 1)

        self.label_pw = QtWidgets.QLabel(Dialog)
        self.label_pw.setObjectName(_fromUtf8("label_pw"))
        self.gridLayout.addWidget(self.label_pw, 1, 0, 1, 1)

        self.lineEdit_pw = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_pw.setEchoMode(QLineEdit.Password)
        self.lineEdit_pw.setReadOnly(False)
        self.lineEdit_pw.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit_pw, 1, 1, 1, 1)

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 3)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Set user and password", None))
        self.label_user.setText(_translate("Dialog", "User: ", None))
        self.label_pw.setText(_translate("Dialog", "Password: ", None))

