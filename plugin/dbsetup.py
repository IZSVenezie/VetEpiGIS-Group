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
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL, Qt, QSettings, QCoreApplication, QFile, QFileInfo, QDate, QVariant, \
    pyqtSignal, QRegExp, QDateTime, QTranslator, QFile, QIODevice, QTextStream
from PyQt4.QtSql import *


from dbsetup_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):         
    def __init__(self):
        """Constructor for the dialog.
        
        """
        
        QDialog.__init__(self)                               
                        
        self.setupUi(self)
        self.plugin_dir = ''

        self.comboBox.addItem('SpatiaLite')
        self.comboBox.addItem('PostGIS')

        self.comboBox.currentIndexChanged.connect(self.seltype)
        self.commandLinkButton.clicked.connect(self.createNewSLdb)



    def seltype(self):
        self.tabWidget.setCurrentIndex(self.comboBox.currentIndex())
        # if self.comboBox.currentText()=='SpatiaLite':
        #     self.tabWidget.setCurrentIndex(0)
        # else:
        #     self.tabWidget.setCurrentIndex(1)


    def createNewSLdb(self):
        fileName = QFileDialog.getSaveFileName(self, caption='Create new SpatiaLite database')
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            file = QFile(fileName + '.sqlite')
            dbpath = QFileInfo(file).absoluteFilePath()
            dbfold = os.path.join(self.plugin_dir, 'db')
            if not os.path.isfile(dbpath):
                shutil.copy(os.path.join(dbfold, 'base.sqlite'), dbpath)
                self.lineEdit.setText(dbpath)

            # file.open( QIODevice.WriteOnly | QIODevice.Text )

        #     out = QTextStream(file)
        #     out << self.plainTextEdit.toPlainText()
        #     out.flush()
        #     file.close()
        #     self.close()
        #     return True
            QApplication.restoreOverrideCursor()
        except IOError:
            return False


