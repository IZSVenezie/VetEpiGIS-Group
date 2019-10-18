# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VetEpiGIS-Group
   A QGIS plugin
   Spatial functions for vet epidemiology
                              -------------------
        begin                : 2016-05-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Norbert Solymosi
        email                : solymosi.norbert@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os, shutil
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal, Qt, QSettings, QCoreApplication, QFile, QFileInfo, QDate, QVariant, \
    pyqtSignal, QRegExp, QDateTime, QTranslator, QFile, QDir, QIODevice, QTextStream

from PyQt5.QtWidgets import *

from qgis.core import QgsDataSourceUri
from PyQt5.QtSql import *

import psycopg2
import psycopg2.extensions
# use unicode!
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from .dbconnection_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):
    def __init__(self):
        """Constructor for the dialog.

        """

        QDialog.__init__(self)

        self.setupUi(self)
        self.plugin_dir = ''
        self.settings = ''

        #self.comboBox_pg_db.currentIndexChanged.connect(self.seltype)
        #self.commandLinkButton.clicked.connect(self.createNewSLdb)
        self.toolButton_sl_db.clicked.connect(self.dbSource)

        self.radioButton_spatialite.clicked.connect(self.seltype)
        self.radioButton_postgis.clicked.connect(self.seltype)

        #self.commandLinkButton_2.clicked.connect(self.createPGtables)

        # self.lineEdit.setText('/home/sn/dev/QGISplugins/VetEpiGIS/groupdata/c.sqlite')


    def dbSource(self):
        dbpath = QFileDialog.getOpenFileName(self, 'Select file', QDir.currentPath(), 'SpatiaLite file (*.sqlite *.*)')
        dbpath = dbpath[0]
        if not dbpath or dbpath =='':
          self.lineEdit_spatialite.setText('')
        else:
          self.lineEdit_spatialite.setText(dbpath)


    def seltype(self):
        if self.radioButton_spatialite.isChecked():
            self.groupBox_postgis.setEnabled(False)
            self.groupBox_spatialite.setEnabled(True)
            self.radioButton_postgis.setChecked(False)

        if self.radioButton_postgis.isChecked():
            self.groupBox_spatialite.setEnabled(False)
            self.groupBox_postgis.setEnabled(True)
            self.radioButton_spatialite.setChecked(False)







