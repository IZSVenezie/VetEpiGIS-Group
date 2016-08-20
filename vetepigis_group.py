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
    pyqtSignal, QRegExp, QDateTime, QTranslator, QSize
from PyQt4.QtSql import *
# from PyQt4.QtXml import *

from qgis.core import QgsField, QgsSpatialIndex, QgsMessageLog, QgsProject, \
    QgsCoordinateTransform, QGis, QgsVectorFileWriter, QgsMapLayerRegistry, QgsFeature, \
    QgsGeometry, QgsFeatureRequest, QgsPoint, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsRectangle, QgsDataSourceURI, QgsDataProvider, QgsComposition, QgsComposerMap, QgsAtlasComposition

from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMessageBar, QgsRubberBand

from plugin import xabout, dbsetup, merge
import resources_rc

import psycopg2
import psycopg2.extensions
# use unicode!
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from uuid import getnode as get_mac

class VetEpiGISgroup:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        # self.loadSettings()
        self.settings = QSettings()


        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VetEpiGISgroup_{}.qm'.format(locale))

        self.vers = '0.1'
        self.prevcur = self.iface.mapCanvas().cursor()

        self.origtool = QgsMapTool(self.iface.mapCanvas())

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # mac = '_'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
        # dbuid = 'db_%s.sqlite' % mac
        # dbfold = os.path.join(self.plugin_dir, 'db')
        # dbuidpath = os.path.join(dbfold, dbuid)
        # if not os.path.isfile(dbuidpath):
        #     shutil.copy(os.path.join(dbfold, 'base.sqlite'), dbuidpath)
        #
        self.dbtype = ''
        self.uri = QgsDataSourceURI()
        # self.uri.setDatabase(dbuidpath)
        #
        # self.db = QSqlDatabase.addDatabase('QSPATIALITE')
        # self.db.setDatabaseName(self.uri.database())

        self.obrflds = ['gid', 'localid', 'code', 'largescale', 'disease', 'animalno', 'species',
            'production', 'year', 'status', 'suspect', 'confirmation', 'expiration', 'notes',
            'hrid', 'timestamp', 'grouping', 'geom']
        self.poiflds = self.obrflds[0:3]
        self.poiflds.append('activity')
        self.poiflds.append('hrid')
        self.poiflds.append('geom')


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VetEpiGIS-Group', message)


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.actAbout = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/icon02.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'About'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actAbout)
        self.actAbout.triggered.connect(self.about)

        self.actSetdb = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/server.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'Setup working database'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actSetdb)
        self.actSetdb.triggered.connect(self.setupDB)

        self.actMerge = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/server-1.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'Merging databases'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actMerge)
        self.actMerge.triggered.connect(self.mergeDB)

        self.toolbar = self.iface.addToolBar(
            QCoreApplication.translate('VetEpiGIS-Group', 'VetEpiGIS-Group'))
        self.toolbar.setObjectName(
            QCoreApplication.translate('VetEpiGIS-Group', 'VetEpiGIS-Group'))

        """Add buttons to the toolbar"""

        self.toolbar.addAction(self.actSetdb)
        self.toolbar.addAction(self.actMerge)


    def mergeDB(self):
        # if self.dbtype == '':
        #     self.iface.messageBar().pushMessage('Information', 'Setup central database connection!',
        #                                         level=QgsMessageBar.INFO)
        #     return

        dlg = merge.Dialog()
        dlg.setWindowTitle('Import database')
        # dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        dlg.lineEdit.setText('/home/sn/dev/QGISplugins/VetEpiGIS/groupdata/db_9A_36_38_21_25_9A.sqlite')

        if dlg.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            idb = QSqlDatabase.addDatabase('QSPATIALITE')
            idb.setDatabaseName(dlg.lineEdit.text())
            idb.open()

            tablst = idb.tables()

     #        tablst = []
     #        query = idb.exec_("SELECT name FROM sqlite_master WHERE type='table'")
     #        while query.next():
     #            tablst.append(query.value(0))
     #
     # QSqlDatabase.record()

            s = ''
            # for t in tablst:
            #     s = s + ', ' + t

            poi_tabs = []
            outbrk_tabs = []

            for tab in tablst:
                rec = idb.record(tab)
                flds = []
                for i in xrange(rec.count()):
                    flds.append(rec.fieldName(i))
                if flds==self.poiflds:
                    poi_tabs.append(tab)
                if flds == self.obrflds:
                    outbrk_tabs.append(tab)

            idb.close()

            self.iface.messageBar().pushMessage('Information', outbrk_tabs[0], level=QgsMessageBar.INFO)

            QApplication.restoreOverrideCursor()


    def setupDB(self):
        dlg = dbsetup.Dialog()
        dlg.setWindowTitle('Setup database connection')
        dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        self.settings.beginGroup('PostgreSQL/connections')
        PGconns = self.settings.childGroups()
        for pg in PGconns:
            dlg.comboBox.addItem(pg)
        self.settings.endGroup()

        dlg.settings = self.settings

        if dlg.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            if dlg.groupBox.isChecked():
                self.dbtype = 'spatialite'
                self.uri.setDatabase(dlg.lineEdit.text())
                self.db = QSqlDatabase.addDatabase('QSPATIALITE')
                self.db.setDatabaseName(self.uri.database())

            if dlg.groupBox_2.isChecked():
                self.dbtype = 'postgis'
                self.settings.beginGroup('PostgreSQL/connections/' + dlg.comboBox.currentText())
                self.PGhost = self.settings.value('host', '')
                self.PGport = self.settings.value('port', '')
                self.PGdatabase = self.settings.value('database', '')
                self.PGusername = self.settings.value('username', '')
                self.PGpassword = self.settings.value('password', '')
                # self.iface.messageBar().pushMessage('Information',
                #     self.PGhost + ', ' + self.PGport + ', ' + self.PGdatabase + ', ' + self.PGusername + ', ' + self.PGpassword, level=QgsMessageBar.INFO)
                self.settings.endGroup()
                # self.uri.setConnection(self.PGhost, str(self.PGport), self.PGdatabase, self.PGusername, self.PGpassword)
# http://gis.stackexchange.com/questions/86707/how-to-perform-sql-queries-and-get-results-from-qgis-python-console
#                 self.db = QSqlDatabase.addDatabase('QPSQL')
#                 self.db.setHostName(self.PGhost)
#                 self.db.setPort(int(self.PGport))
#                 self.db.setDatabaseName(self.PGdatabase)
#                 self.db.setUserName(self.PGusername)
#                 self.db.setPassword(self.PGpassword)
#
#                 self.db.open()
#                 query = QSqlQuery(self.db)
#                 query.exec_("select * from kisterseg175;")
#                 query.next()
#                 self.iface.messageBar().pushMessage('Information', str(query.value(0)), level=QgsMessageBar.INFO)
#                 self.db.close()

                try:
                    self.PGcon = psycopg2.connect(host=self.PGhost, port=self.PGport, database=self.PGdatabase, user=self.PGusername, password=self.PGpassword)
                except TypeError:
                    self.PGcon = psycopg2.connect(host=self.PGhost, database=self.PGdatabase, user=self.PGusername, password=self.PGpassword)

                # self.cursor = self.PGcon.cursor()
                # sql = "select * from kisterseg175;"
                # self.cursor.execute(sql)
                # result = self.cursor.fetchone()
                #
                # self.iface.messageBar().pushMessage('Information', str(result[0]), level=QgsMessageBar.INFO)

            QApplication.restoreOverrideCursor()


    # def __del__(self):
    #     self.PGcon.close()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # self.PGcon.close()
        self.iface.removePluginMenu('&VetEpiGIS-Group', self.actAbout)
        del self.toolbar


    def about(self):
        dlg = xabout.Dialog()
        dlg.setWindowTitle('About')
        dlg.label.setPixmap(QPixmap(':/plugins/VetEpiGISgroup/images/QVetGroup-about-banner.png'))
        ow = dlg.textEdit.fontWeight()

        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('VetEpiGIS-Group ' + self.vers +'\n')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append('VetEpiGIS-Group is a free QGIS plugin helping veterinarians in the management of spatial data related to animal disease.\n')
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Developers:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append('Norbert Solymosi *;\n* from University of Veterinary Medicine, Budapest.\n')
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Contributors:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append(u'Nicola Ferrè *;\nMatteo Mazzucato *;\n* from Istituto Zooprofilattico Sperimentale delle Venezie.\n')
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Contacts:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append('Send an email to gis@izsvenezie.it\n\n')
        dlg.textEdit.append('Original icons designed by Feepik. They were modified for this project by IZSVe.')
        dlg.textEdit.moveCursor(QTextCursor.Start, QTextCursor.MoveAnchor)
        dlg.textEdit.setReadOnly(True)

        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)
        dlg.exec_()

