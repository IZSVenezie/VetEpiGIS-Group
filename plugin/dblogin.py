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

from PyQt5.QtSql import *
from PyQt5.QtWidgets import QDialog, QFileDialog

import psycopg2
import psycopg2.extensions
# use unicode!
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from .dblogin_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):
    def __init__(self):
        """Constructor for the dialog.

        """

        QDialog.__init__(self)

        self.setupUi(self)

        self.accepted.connect(self.checkValues)

    def checkValues(self):
        username = self.lineEdit_user.text()
        pw = self.lineEdit_pw.text()

        if not username or username =='':
            self.lineEdit_user.setText('')

        if not pw or pw =='':
            self.lineEdit_pw.setText('')







