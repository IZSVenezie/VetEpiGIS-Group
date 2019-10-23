# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'merge_dialog_base.ui'
#
# Created: Mon May 15 11:05:12 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

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
        Dialog.resize(451, 131)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.label_db = QtWidgets.QLabel(Dialog)
        self.label_db.setObjectName(_fromUtf8("label_db"))
        self.gridLayout.addWidget(self.label_db, 0, 0, 1, 1)

        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.toolButton = QtWidgets.QToolButton(Dialog)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)

        self.checkBox = QtWidgets.QCheckBox(Dialog)
        self.checkBox.setEnabled(False)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 1, 1, 1, 1)

        self.label_WD = QtWidgets.QLabel(Dialog)
        self.label_WD.setObjectName(_fromUtf8("label_WD"))
        self.label_WD.setText('Working database:')
        self.gridLayout.addWidget(self.label_WD, 2, 0, 1, 1)

        self.label_path_WD = QtWidgets.QLabel(Dialog)
        self.label_path_WD.setObjectName(_fromUtf8("label_path_WD"))
        self.label_path_WD.setText('')
        self.gridLayout.addWidget(self.label_path_WD, 2, 1, 1, 1)

        spacerItem = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 2, 1, 2)

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 2)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_db.setText(_translate("Dialog", "SpatiaLite file:", None))
        self.toolButton.setText(_translate("Dialog", "...", None))
        self.checkBox.setText(_translate("Dialog", "Update existing records", None))

