# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dbsetup_dialog_base.ui'
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
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(430, 150)

        self.gridLayout_5 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))

        self.radioButton_spatialite = QtWidgets.QRadioButton(Dialog)
        self.radioButton_spatialite.setChecked(True)
        self.radioButton_spatialite.setText('Spatialite')
        self.radioButton_spatialite.setObjectName(_fromUtf8("radioButton_spatialite"))
        self.radioButton_spatialite.setMinimumWidth(80)
        self.radioButton_spatialite.setMaximumWidth(80)
        self.gridLayout_5.addWidget(self.radioButton_spatialite, 0, 0, 1, 1)

        css = """
                QLabel {
                    font-style: italic;
                }
            """

        self.label_sl_description = QtWidgets.QLabel(Dialog)
        self.label_sl_description.setObjectName(_fromUtf8("label_sl_description"))
        self.label_sl_description.setText('Load an SQLite database')
        self.label_sl_description.setStyleSheet(css)
        self.gridLayout_5.addWidget(self.label_sl_description, 0, 1, 1, 1)

        self.groupBox_spatialite = QtWidgets.QGroupBox(Dialog)
        self.groupBox_spatialite.setObjectName(_fromUtf8("groupBox"))

        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_spatialite)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.label_file = QtWidgets.QLabel(self.groupBox_spatialite)
        self.label_file.setObjectName(_fromUtf8("label_file"))
        self.label_file.setText('File:')
        self.label_file.setMinimumWidth(70)
        self.label_file.setMaximumWidth(70)
        self.gridLayout.addWidget(self.label_file, 1, 0, 1, 1)

        self.lineEdit_spatialite = QtWidgets.QLineEdit(self.groupBox_spatialite)
        self.lineEdit_spatialite.setReadOnly(True)
        self.lineEdit_spatialite.setObjectName(_fromUtf8("lineEdit_spatialite"))
        self.gridLayout.addWidget(self.lineEdit_spatialite, 1, 1, 1, 1)

        self.toolButton_sl_db = QtWidgets.QToolButton(self.groupBox_spatialite)
        self.toolButton_sl_db.setObjectName(_fromUtf8("toolButton_sl_db"))
        self.gridLayout.addWidget(self.toolButton_sl_db, 1, 2, 1, 1)

        self.gridLayout_5.addWidget(self.groupBox_spatialite, 1, 0, 1, 2)
        self.groupBox_spatialite.setEnabled(True)

        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_5.addItem(spacerItem1,2,0,1,2)

        self.sep_line = QFrame()
        self.sep_line.setFrameShape(QFrame.HLine)
        self.sep_line.setFrameShadow(QFrame.Sunken)
        self.gridLayout_5.addWidget(self.sep_line,3,0,1,2)

        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_5.addItem(spacerItem2,4,0,1,2)

        self.radioButton_postgis = QtWidgets.QRadioButton(Dialog)
        self.radioButton_postgis.setChecked(False)
        self.radioButton_postgis.setText('PostGIS')
        self.radioButton_postgis.setObjectName(_fromUtf8("radioButton_postgis"))
        self.radioButton_postgis.setMinimumWidth(80)
        self.radioButton_postgis.setMaximumWidth(80)
        self.gridLayout_5.addWidget(self.radioButton_postgis, 5, 0, 1, 1)

        self.label_pg_description = QtWidgets.QLabel(Dialog)
        self.label_pg_description.setObjectName(_fromUtf8("label_pg_description"))
        self.label_pg_description.setText("Load POSTGIS database")
        self.label_pg_description.setStyleSheet(css)
        self.gridLayout_5.addWidget(self.label_pg_description, 5, 1, 1, 1)

        self.groupBox_postgis = QtWidgets.QGroupBox(Dialog)
        self.groupBox_postgis.setObjectName(_fromUtf8("groupBox_2"))

        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_postgis)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))

        self.label_name_pg_db = QtWidgets.QLabel(self.groupBox_postgis)
        self.label_name_pg_db.setObjectName(_fromUtf8("label_name_pg_db"))
        self.label_name_pg_db.setText('Name:')
        self.label_name_pg_db.setMinimumWidth(70)
        self.label_name_pg_db.setMaximumWidth(70)
        self.gridLayout_2.addWidget(self.label_name_pg_db, 0, 0, 1, 1)

        self.comboBox_pg_db = QtWidgets.QComboBox(self.groupBox_postgis)
        self.comboBox_pg_db.setMinimumSize(QtCore.QSize(150, 0))
        self.comboBox_pg_db.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout_2.addWidget(self.comboBox_pg_db, 0, 1, 1, 1)

        self.gridLayout_5.addWidget(self.groupBox_postgis, 6, 0, 1, 2)
        self.groupBox_postgis.setEnabled(False)

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_5.addWidget(self.buttonBox, 7, 0, 1, 2)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        # self.groupBox_spatialite.setTitle(_translate("Dialog", "SpatiaLite database", None))
        self.label_file.setText(_translate("Dialog", "File:", None))
        self.label_file.setText(_translate("Dialog", "File:", None))
        self.toolButton_sl_db.setText(_translate("Dialog", "...", None))
        # self.commandLinkButton_2.setText(_translate("Dialog", "Create new SpatiaLite database", None))
        # self.groupBox_2.setTitle(_translate("Dialog", "PostgreSQL-PostGIS connection", None))
        self.label_name_pg_db.setText(_translate("Dialog", "Name:", None))
        # self.commandLinkButton_2.setText(_translate("Dialog", "Create empty tables", None))

