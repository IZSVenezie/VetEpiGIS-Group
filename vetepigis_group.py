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
import psycopg2
import psycopg2.extensions
# use unicode!
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from enum import Enum

from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal, Qt, QSettings, QCoreApplication, QFile, QFileInfo, QDate, QVariant, \
    pyqtSignal, QRegExp, QDateTime, QTranslator, QSize
from PyQt5.QtSql import *
# from PyQt4.QtXml import *
from PyQt5.QtWidgets import *

from qgis.core import QgsField, QgsSpatialIndex, QgsMessageLog, QgsProject, \
    QgsCoordinateTransform, QgsVectorFileWriter, QgsFeature, \
    QgsGeometry, QgsFeatureRequest, QgsPoint, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsRectangle, QgsDataSourceUri, QgsDataProvider, QgsLayout, QgsLayoutItem, Qgis, QgsWkbTypes

from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMessageBar, QgsRubberBand

from .plugin import xabout, dbsetup, merge, dblogin, dbconnection, selitem
from .resources_rc import *


#from pyspatialite import dbapi2 as spdb

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

        self.vers = '0.111'
        self.prevcur = self.iface.mapCanvas().cursor()

        self.origtool = QgsMapTool(self.iface.mapCanvas())

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        #
        self.dbtype = ''
        self.dbpath = ''

        self.obrflds = ['gid', 'localid', 'code', 'largescale', 'disease', 'animalno', 'species',
            'production', 'year', 'status', 'suspect', 'confirmation', 'expiration', 'notes',
            'hrid', 'timestamp', 'grouping']
        self.poiflds = self.obrflds[0:3]
        self.poiflds.append('activity')
        self.poiflds.append('hrid')
        self.sl_path_memorized = ''
        self.pg_memorized =''
        self.zonelfds = []
        self.pg_user = ''
        self.pg_pw = ''
        self.tableList = ['outbreaks_point','outbreaks_area','pois', 'buffers','zones','xdiseases','xpoitypes','xspecies','xstyles']

        #fields of layers in local db
        self.obr_pt_poly_flds = ['gid', 'localid', 'code', 'largescale', 'disease', 'animalno', 'species',
            'production', 'year', 'status', 'suspect', 'confirmation', 'expiration', 'notes',
            'hrid', 'timestamp', 'grouping']
        self.buff_flds = ['gid', 'localid', 'code', 'largescale', 'disease', 'animalno', 'species',
            'production', 'year', 'status', 'suspect', 'confirmation', 'expiration', 'notes',
            'hrid', 'timestamp']

        self.poi_pt_flds = self.obr_pt_poly_flds [0:3]
        self.poi_pt_flds.append('activity')
        self.poi_pt_flds.append('hrid')

        self.zone_poly_flds = ['localid', 'code', 'disease', 'zonetype', 'subpopulation', 'validity_start', \
                'validity_end', 'legal_framework', 'competent_authority', 'biosecurity_measures', \
                'control_of_vectors', 'control_of_wildlife_reservoir', 'modified_stamping_out', \
                'movement_restriction', 'stamping_out', 'surveillance', 'vaccination', \
                'other_measure', 'related', 'hrid', 'timestamp']




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

        self.actConndb = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/connection.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'Load working database'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actConndb)
        self.actConndb.triggered.connect(self.loadDB)

        self.actMerge = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/server-1.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'Merging databases'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actMerge)
        self.actMerge.triggered.connect(self.mergeDB)

        self.actSelMerge = QAction(
            QIcon(':/plugins/VetEpiGISgroup/images/server-2.png'),
            QCoreApplication.translate('VetEpiGIS-Group', 'Merging databases from selected feature'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actSelMerge)
        self.actSelMerge.triggered.connect(self.mergeSelItem)

        # self.actExport = QAction(
        #     QIcon(':/plugins/VetEpiGISgroup/images/export.png'),
        #     QCoreApplication.translate('VetEpiGIS-Group', 'Export layers'),
        #     self.iface.mainWindow())
        # self.iface.addPluginToMenu('&VetEpiGIS-Group', self.actExport)
        # self.actExport.triggered.connect(self.exportLy)

        self.toolbar = self.iface.addToolBar(
            QCoreApplication.translate('VetEpiGIS-Group', 'VetEpiGIS-Group'))
        self.toolbar.setObjectName(
            QCoreApplication.translate('VetEpiGIS-Group', 'VetEpiGIS-Group'))

        """Add buttons to the toolbar"""

        #self.toolbar.addAction(self.actSetdb)
        #self.toolbar.addAction(self.actConndb)
        #self.toolbar.addAction(self.actMerge)
        # self.toolbar.addAction(self.actExport)

        self.grp1 = QToolButton(self.toolbar)
        self.grp1.setPopupMode(QToolButton.MenuButtonPopup)
        self.grp1.addActions([self.actSetdb, self.actConndb])
        self.grp1.setDefaultAction(self.actSetdb)
        self.toolbar.addWidget(self.grp1)

        self.grp2 = QToolButton(self.toolbar)
        self.grp2.setPopupMode(QToolButton.MenuButtonPopup)
        self.grp2.addActions([self.actMerge, self.actSelMerge])
        self.grp2.setDefaultAction(self.actMerge)
        self.toolbar.addWidget(self.grp2)



    def mergeSelItem(self):
        self.grp2.setDefaultAction(self.actSelMerge)

        tool_name = 'Add selected item to Working DB'
        #Check if working database is selected
        if (not self.dbpath or self.dbpath =='') or (not self.dbtype or self.dbtype ==''):
            self.iface.messageBar().pushMessage(tool_name, 'Before continuing, select the working database with \
                "Setup workind directory" or "Load working directory" tools.', level=Qgis.Warning)
            return

        #check if there are feature selected
        if QgsProject.instance().count()==0:
            self.iface.messageBar().pushMessage(tool_name, \
                'Please add a vector layer.', level=Qgis.Warning)
            # QMessageBox.warning(self.iface.mainWindow(),
            #     "Warning", "Please add a vector layer.",
            #     buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
            return

        mLayer = self.iface.activeLayer()
        if mLayer is None:
            self.iface.messageBar().pushMessage(tool_name, \
                'Please select an input layer.', level=Qgis.Warning)
            # QMessageBox.warning(self.iface.mainWindow(),
            #     "Warning", "Please select an input layer.",
            #     buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
            return

        if mLayer.type()!=0:
            self.iface.messageBar().pushMessage(tool_name, \
                'Please select a vector layer.', level=Qgis.Warning)
            # QMessageBox.warning(self.iface.mainWindow(),
            #     "Warning", "Please select a vector layer.",
            #     buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
            return

        if mLayer.selectedFeatureCount()==0:
            self.iface.messageBar().pushMessage(tool_name, \
                'Select one or more features for selected layer.', level=Qgis.Warning)
            # QMessageBox.warning(self.iface.mainWindow(),
            #     "Warning", "Select one or more features for selected layer",
            #     buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
            return

        c = 0
        nslst = []
        prvsrc = mLayer.dataProvider()
        flds = prvsrc.fields()
        for fld in flds:
            nslst.append(fld.name())

        #Check geometry type and its relative fields
        if mLayer.geometryType() == QgsWkbTypes.PointGeometry:
            #outbreak or poi
            if nslst == self.obr_pt_poly_flds:
                c = 1
                layer_type = VetLayerType.OUT_PT
            elif nslst==self.poi_pt_flds:
                c = 1
                layer_type = VetLayerType.POI_PT
        elif mLayer.geometryType() == QgsWkbTypes.PolygonGeometry:
            #outbreak, outbreaks buffer, poi buffer, zone
            if nslst == self.obr_pt_poly_flds:
                c = 1
                layer_type = VetLayerType.OUT_POLY
            elif nslst == self.buff_flds:
                c = 1
                layer_type = VetLayerType.BUFFER_OUT
            elif nslst==self.zone_poly_flds:
                c = 1
                layer_type = VetLayerType.ZONE

        if c == 0:
            self.iface.messageBar().pushMessage(tool_name, \
                'The selected layer is not compliant with VetEPIGIS-Tool layers.', level=Qgis.Warning)
            return

        #get selected feature
        dlg = selitem.Dialog(self.dbpath, self.dbtype,mLayer.selectedFeatureCount())

        dlg.setWindowTitle(tool_name)
        # dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        if dlg.exec_() == QDialog.Accepted:

            sfeats = mLayer.selectedFeatures()

            #check if selected feature already exist in WD
            exist_hrid = False
            overwrite_answer = False
            hrid_list = self.getHridFromWDB(layer_type.value)
            for sf in sfeats:
                hrid = sf.attribute('hrid')
                if hrid in hrid_list:
                #check_exist = self.existHrid(layer_type.value,hrid)
                #if check_exist == True:
                    exist_hrid = True
                    break

            if dlg.checkBox.isChecked() and exist_hrid == True:
                #message box for overwrite features
                overwrite_msg = QMessageBox.question(self.iface.mainWindow(),
                    "Warning", "Are you sure to overwrite features?",
                    QMessageBox.Ok, QMessageBox.No)
                #if ok overwrite
                if overwrite_msg == QMessageBox.Ok:
                    overwrite_answer = True

            if self.dbtype == 'postgis':
                sql = ''
                for sf in sfeats:
                    check_exist = False
                    #get hrid of selected feature
                    hrid = sf.attribute('hrid')
                    if hrid in hrid_list:
                        check_exist = True

                    #Feature is not in WD --> insert feature
                    if check_exist == False:
                        sql = sql + self.getInsertSQLPG(nslst, layer_type.value, sf)

                    #Feature in WD but not overwrite --> skip feature
                    elif check_exist == True and overwrite_answer == False:
                        continue

                    #Feature in WD and overwrite --> update feature
                    elif check_exist == True and overwrite_answer == True:
                        sql = sql + self.getUpdateSQLPG(nslst, layer_type.value, sf, hrid)

                if sql == '':
                    self.iface.messageBar().pushMessage(tool_name, \
                        "No features were added or modified in the Working database", level=Qgis.Info)
                    return

                cursor = self.PGcon.cursor()
                cursor.execute(sql)
                self.PGcon.commit()
                # #self.PGcon.close()
                self.iface.messageBar().pushMessage(tool_name, \
                        'Features added to working database', level=Qgis.Info)

            #TODO: manage feature data with apostophe in the attribute table es: Infection with Aujeszky's disease virus
            if self.dbtype == 'spatialite':

                idb = QSqlDatabase.addDatabase('QSPATIALITE')
                idb.setDatabaseName(self.ipath)
                if not idb.open():
                    idb.open()

                sql = ''
                error_list = []
                for sf in sfeats:
                    check_exist = False
                    #get hrid of selected feature
                    hrid = sf.attribute('hrid')
                    if hrid in hrid_list:
                        check_exist = True

                    #Feature is not in WD --> insert feature
                    if check_exist == False:
                        sql = self.getInsertSQLPG(nslst, layer_type.value, sf)
                        rs = idb.exec_(sql)
                        if rs.lastError().type() !=0:
                            error_list.append((layer_type.name, sf.attribute('code')))

                    #Feature in WD but not overwrite --> skip feature
                    elif check_exist == True and overwrite_answer == False:
                        continue

                    #Feature in WD and overwrite --> update feature
                    elif check_exist == True and overwrite_answer == True:

                        sql = self.getUpdateSQLPG(nslst, layer_type.value, sf, hrid)
                        rs = idb.exec_(sql)
                        if rs.lastError().type() !=0:
                            error_list.append((layer_type.name, sf.attribute('gid')))

                #TODO: check if this control is ok here
                if sql == '':
                    self.iface.messageBar().pushMessage(tool_name, \
                        "No features were added or modified in the Working database", level=Qgis.Info)
                    return

                idb.commit()
                idb.close()

                #TODO: manage no added feature, for example with a log file or put in a message...
                if error_list:
                    QMessageBox.warning(self.iface.mainWindow(),
                        "Warning", "Some features are not added to working database.",
                        buttons=QMessageBox.Ok, defaultButton=QMessageBox.NoButton)
                else:
                    self.iface.messageBar().pushMessage(tool_name, \
                            'Features added to working database', level=Qgis.Info)


    def getTableName(self, vet_layer_type):
        table = ''
        if vet_layer_type == VetLayerType.OUT_PT.value:
            table = 'outbreaks_point'
        elif vet_layer_type == VetLayerType.POI_PT.value:
            table = 'pois'
        elif vet_layer_type == VetLayerType.OUT_POLY.value:
            table = 'outbreaks_area'
        elif vet_layer_type == VetLayerType.BUFFER_OUT.value:
            table = 'buffers'
        elif vet_layer_type == VetLayerType.ZONE.value:
            table = 'zones'
        return table

    def getHridFromWDB(self, vet_layer_type):

        hrid_list = []
        tableName = self.getTableName(vet_layer_type)
        sqlHrid = "SELECT hrid FROM %s ;" % (tableName)

        if self.dbtype == 'postgis':
            cursor = self.PGcon.cursor()
            cursor.execute(sqlHrid)
            res = cursor.fetchall()
            for r in res:
                hrid_list.append(r[0])

        elif self.dbtype == 'spatialite':
            idb = QSqlDatabase.addDatabase('QSPATIALITE')
            idb.setDatabaseName(self.dbpath)
            if not idb.open():
                idb.open()

            q = idb.exec_(sqlHrid)
            while q.next():
                hrid_list.append(q.value(0))

            idb.close()
        #TODO: if table is empty
        return hrid_list




    def getInsertSQLPG(self, nslst, vet_layer_type, sf):
        #outbreak point or poi
        if vet_layer_type == VetLayerType.OUT_PT.value:
            sql = """INSERT INTO outbreaks_point (localid, code, largescale, disease,
                animalno, species, production, year, status, suspect, confirmation,
                expiration, notes, hrid, timestamp, grouping, geom)
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                    '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('largescale'),
                    sf.attribute('disease'),
                    sf.attribute('animalno'),
                    sf.attribute('species'),
                    sf.attribute('production'),
                    sf.attribute('year'),
                    sf.attribute('status'),
                    sf.attribute('suspect'),
                    sf.attribute('confirmation'),
                    sf.attribute('expiration'),
                    sf.attribute('notes'),
                    sf.attribute('hrid'),
                    sf.attribute('timestamp'),
                    sf.attribute('grouping'),
                    sf.geometry().asWkt()
                )

        elif vet_layer_type == VetLayerType.POI_PT.value:
            sql = """INSERT INTO pois (localid, code, activity, hrid, geom)
                VALUES ('%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('activity'),
                    sf.attribute('hrid'),
                    sf.geometry().asWkt()
                )

        if vet_layer_type == VetLayerType.OUT_POLY.value:
            # outbreaks_area is a polygon (simple)
            # outbreaks_area have to be converted to multipolygon
            tmp = sf.geometry().convertToType(QgsWkbTypes.PolygonGeometry, True)
            sql = """INSERT INTO outbreaks_area(localid, code, largescale, disease,
                    animalno, species, production, year, status, suspect, confirmation,
                    expiration, notes, hrid, timestamp, grouping, geom)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                        '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));""" \
                    % (
                        sf.attribute('localid'),
                        sf.attribute('code'),
                        sf.attribute('largescale'),
                        sf.attribute('disease'),
                        sf.attribute('animalno'),
                        sf.attribute('species'),
                        sf.attribute('production'),
                        sf.attribute('year'),
                        sf.attribute('status'),
                        sf.attribute('suspect'),
                        sf.attribute('confirmation'),
                        sf.attribute('expiration'),
                        sf.attribute('notes'),
                        sf.attribute('hrid'),
                        sf.attribute('timestamp'),
                        sf.attribute('grouping'),
                        tmp.asWkt()
                    )
        elif vet_layer_type == VetLayerType.BUFFER_OUT.value:
            sql = """INSERT INTO buffers (localid, code, largescale, disease,
                    animalno, species, production, year, status, suspect, confirmation,
                    expiration, notes, hrid, timestamp, geom)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                        '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));""" \
                    % (
                        sf.attribute('localid'),
                        sf.attribute('code'),
                        sf.attribute('largescale'),
                        sf.attribute('disease'),
                        sf.attribute('animalno'),
                        sf.attribute('species'),
                        sf.attribute('production'),
                        sf.attribute('year'),
                        sf.attribute('status'),
                        sf.attribute('suspect'),
                        sf.attribute('confirmation'),
                        sf.attribute('expiration'),
                        sf.attribute('notes'),
                        sf.attribute('hrid'),
                        sf.attribute('timestamp'),
                        sf.geometry().asWkt()
                    )

        elif vet_layer_type == VetLayerType.ZONE.value:
            sql = """INSERT INTO zones (localid, code, disease, zonetype, subpopulation, validity_start,
                        validity_end, legal_framework, competent_authority, biosecurity_measures,
                        control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out,
                        movement_restriction, stamping_out, surveillance, vaccination,
                        other_measure, related, hrid, timestamp, geom)
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                        '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('disease'),
                    sf.attribute('zonetype'),
                    sf.attribute('subpopulation'),
                    sf.attribute('validity_start'),
                    sf.attribute('validity_end'),
                    sf.attribute('legal_framework'),
                    sf.attribute('competent_authority'),
                    sf.attribute('biosecurity_measures'),
                    sf.attribute('control_of_vectors'),
                    sf.attribute('control_of_wildlife_reservoir'),
                    sf.attribute('modified_stamping_out'),
                    sf.attribute('movement_restriction'),
                    sf.attribute('stamping_out'),
                    sf.attribute('surveillance'),
                    sf.attribute('vaccination'),
                    sf.attribute('other_measure'),
                    sf.attribute('related'),
                    sf.attribute('hrid'),
                    sf.attribute('timestamp'),
                    sf.geometry().asWkt()
                )
        return sql


    def getUpdateSQLPG(self, nslst, vet_layer_type, sf, hrid):
        #outbreak point or poi
        if vet_layer_type == VetLayerType.OUT_PT.value:
            #I don't update hrid
            sql = """UPDATE outbreaks_point
                     SET localid = '%s', code = '%s', largescale = '%s', disease = '%s',
                        animalno = '%s', species = '%s', production = '%s', year = '%s', status = '%s',
                        suspect = '%s', confirmation = '%s', expiration = '%s', notes = '%s',
                        timestamp = '%s', grouping = '%s', geom = ST_GeomFromText('%s', 4326)
                     WHERE hrid = '%s';""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('largescale'),
                    sf.attribute('disease'),
                    sf.attribute('animalno'),
                    sf.attribute('species'),
                    sf.attribute('production'),
                    sf.attribute('year'),
                    sf.attribute('status'),
                    sf.attribute('suspect'),
                    sf.attribute('confirmation'),
                    sf.attribute('expiration'),
                    sf.attribute('notes'),
                    sf.attribute('timestamp'),
                    sf.attribute('grouping'),
                    sf.geometry().asWkt(),
                    hrid
                )

        elif vet_layer_type == VetLayerType.POI_PT.value:
            sql = """UPDATE pois
                     SET localid = '%s', code = '%s', activity = '%s', geom = ST_GeomFromText('%s', 4326)
                     WHERE hrid = '%s';""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('activity'),
                    sf.geometry().asWkt(),
                    hrid
                )

        if vet_layer_type == VetLayerType.OUT_POLY.value:
            # outbreaks_area is a polygon (simple)
            # outbreaks_area have to be converted to multipolygon
            tmp = sf.geometry().convertToType(QgsWkbTypes.PolygonGeometry, True)
            sql = """UPDATE outbreaks_area
                     SET localid = '%s', code = '%s', largescale = '%s', disease = '%s',
                        animalno = '%s', species = '%s', production = '%s', year = '%s', status = '%s',
                        suspect = '%s', confirmation = '%s', expiration = '%s', notes = '%s',
                        timestamp = '%s', grouping = '%s', geom = ST_GeomFromText('%s', 4326)
                     WHERE hrid = '%s';""" \
                    % (
                        sf.attribute('localid'),
                        sf.attribute('code'),
                        sf.attribute('largescale'),
                        sf.attribute('disease'),
                        sf.attribute('animalno'),
                        sf.attribute('species'),
                        sf.attribute('production'),
                        sf.attribute('year'),
                        sf.attribute('status'),
                        sf.attribute('suspect'),
                        sf.attribute('confirmation'),
                        sf.attribute('expiration'),
                        sf.attribute('notes'),
                        sf.attribute('timestamp'),
                        sf.attribute('grouping'),
                        tmp.asWkt(),
                        hrid
                    )
        elif vet_layer_type == VetLayerType.BUFFER_OUT.value:
            sql = """UPDATE buffers
                     SET localid = '%s', code = '%s', largescale = '%s', disease = '%s',
                        animalno = '%s', species = '%s', production = '%s', year = '%s', status = '%s',
                        suspect = '%s', confirmation = '%s', expiration = '%s', notes = '%s',
                        timestamp = '%s', geom = ST_GeomFromText('%s', 4326)
                     WHERE hrid = '%s';""" \
                    % (
                        sf.attribute('localid'),
                        sf.attribute('code'),
                        sf.attribute('largescale'),
                        sf.attribute('disease'),
                        sf.attribute('animalno'),
                        sf.attribute('species'),
                        sf.attribute('production'),
                        sf.attribute('year'),
                        sf.attribute('status'),
                        sf.attribute('suspect'),
                        sf.attribute('confirmation'),
                        sf.attribute('expiration'),
                        sf.attribute('notes'),
                        sf.attribute('timestamp'),
                        sf.geometry().asWkt(),
                        hrid
                    )
        elif vet_layer_type == VetLayerType.ZONE.value:
            sql = """UPDATE zones
                     SET localid = '%s', code = '%s', disease = '%s', zonetype = '%s', subpopulation = '%s',
                         validity_start = '%s', validity_end = '%s', legal_framework = '%s',
                         competent_authority = '%s', biosecurity_measures = '%s', control_of_vectors = '%s',
                         control_of_wildlife_reservoir = '%s', modified_stamping_out = '%s',
                        movement_restriction = '%s', stamping_out = '%s', surveillance = '%s', vaccination = '%s',
                        other_measure = '%s', related = '%s', timestamp = '%s',
                        geom = ST_GeomFromText('%s', 4326)
                    WHERE hrid = '%s';""" \
                % (
                    sf.attribute('localid'),
                    sf.attribute('code'),
                    sf.attribute('disease'),
                    sf.attribute('zonetype'),
                    sf.attribute('subpopulation'),
                    sf.attribute('validity_start'),
                    sf.attribute('validity_end'),
                    sf.attribute('legal_framework'),
                    sf.attribute('competent_authority'),
                    sf.attribute('biosecurity_measures'),
                    sf.attribute('control_of_vectors'),
                    sf.attribute('control_of_wildlife_reservoir'),
                    sf.attribute('modified_stamping_out'),
                    sf.attribute('movement_restriction'),
                    sf.attribute('stamping_out'),
                    sf.attribute('surveillance'),
                    sf.attribute('vaccination'),
                    sf.attribute('other_measure'),
                    sf.attribute('related'),
                    sf.attribute('timestamp'),
                    sf.geometry().asWkt(),
                    hrid
                )
        return sql


    def mergeDB(self):
        # if self.dbtype == '':
        #     self.iface.messageBar().pushMessage('Information', 'Setup central database connection!',
        #                                         level=QgsMessageBar.INFO)
        #     return

        dlg = merge.Dialog(self.dbpath,self.dbtype)
        dlg.setWindowTitle('Import database')
        # dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        # dlg.lineEdit.setText('/home/sn/dev/QGISplugins/VetEpiGIS/groupdata/db_9A_36_38_21_25_9A.sqlite')

        if dlg.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            self.ipath = dlg.lineEdit.text()

            isql = ''
            sqlinup = ''
            bflds = self.obrflds[0:16]
            bflds.append('geom')
            zflds = ['localid', 'code', 'disease', 'zonetype', 'subpopulation', 'validity_start', 'validity_end', 'legal_framework', 'competent_authority', 'biosecurity_measures', 'control_of_vectors', 'control_of_wildlife_reservoir', 'modified_stamping_out', 'movement_restriction', 'stamping_out', 'surveillance', 'vaccination', 'other_measure', 'related', 'hrid', 'timestamp', 'geom']
            poin = opointn = oarean = zonen = buffn = 0

            if self.dbtype == 'spatialite':
                # self.db = QSqlDatabase.addDatabase('QSPATIALITE')
                # self.db.setDatabaseName(self.dbpath)
                # if not self.db.open():
                #     self.db.open()
                # self.iface.messageBar().pushMessage('Information', 'self.db: %s' % self.db.isOpen(),
                #                                     level=QgsMessageBar.INFO)

                idb = QSqlDatabase.addDatabase('QSPATIALITE')
                idb.setDatabaseName(self.ipath)
                if not idb.open():
                    idb.open()
                tablst = idb.tables()

                # self.iface.messageBar().pushMessage('Information', self.ipath, level=QgsMessageBar.INFO)
                # self.iface.messageBar().pushMessage('Information', self.dbpath, level=QgsMessageBar.INFO)

                conn = idb.connect(self.dbpath)
                cur = conn.cursor()
                # rs = cur.execute("""
                #     CREATE TABLE opointtmp (
                #       gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                #       localid text,
                #       code text,
                #       largescale text,
                #       disease text,
                #       animalno numeric,
                #       species text,
                #       production text,
                #       year numeric,
                #       status text,
                #       suspect text,
                #       confirmation text,
                #       expiration text,
                #       notes text,
                #       hrid text,
                #       timestamp text,
                #       grouping text
                #     );
                # """)
                # rs = cur.execute("SELECT AddGeometryColumn('opointtmp', 'geom', 4326, 'POINT', 'XY');")
                # rs = cur.execute("""
                #     CREATE TABLE oareatmp (
                #       gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                #       localid text,
                #       code text,
                #       largescale text,
                #       disease text,
                #       animalno numeric,
                #       species text,
                #       production text,
                #       year numeric,
                #       status text,
                #       suspect text,
                #       confirmation text,
                #       expiration text,
                #       notes text,
                #       hrid text,
                #       timestamp text,
                #       grouping text
                #     );
                #     """)
                # rs = cur.execute("SELECT AddGeometryColumn('oareatmp', 'geom', 4326, 'MULTIPOLYGON', 'XY');")
                # rs = cur.execute("""
                #     CREATE TABLE poistmp (
                #       gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                #       localid text,
                #       code text,
                #       activity text,
                #       hrid text
                #     );
                # """)
                # rs = cur.execute("SELECT AddGeometryColumn('poistmp', 'geom', 4326, 'POINT', 'XY');")
                # rs = cur.execute("""
                #     CREATE TABLE bufferstmp (
                #       gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                #       localid text,
                #       code text,
                #       largescale text,
                #       disease text,
                #       animalno numeric,
                #       species text,
                #       production text,
                #       year numeric,
                #       status text,
                #       suspect text,
                #       confirmation text,
                #       expiration text,
                #       notes text,
                #       hrid text,
                #       timestamp text
                #     );
                # """)
                # rs = cur.execute("SELECT AddGeometryColumn('bufferstmp', 'geom', 4326, 'MULTIPOLYGON', 'XY');")
                # rs = cur.execute("""
                #     CREATE TABLE zonestmp (
                #       gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                #       localid text,
                #       code text,
                #       disease text,
                #       zonetype text,
                #       subpopulation text,
                #       validity_start text,
                #       validity_end text,
                #       legal_framework text,
                #       competent_authority text,
                #       biosecurity_measures text,
                #       control_of_vectors text,
                #       control_of_wildlife_reservoir text,
                #       modified_stamping_out text,
                #       movement_restriction text,
                #       stamping_out text,
                #       surveillance text,
                #       vaccination text,
                #       other_measure text,
                #       related text,
                #       hrid text,
                #       timestamp text
                #     );
                # """)
                # rs = cur.execute("SELECT AddGeometryColumn('zonestmp', 'geom', 4326, 'MULTIPOLYGON', 'XY');")

                # self.iface.messageBar().pushMessage('Information', 'idb: %s' % idb.isOpen(),
                #                                     level=QgsMessageBar.INFO)
                # /home/sn/Downloads/install/src/qgis-2.16.1/python/plugins/processing/tools/spatialite.py

                for tab in tablst:
                    rec = idb.record(tab)
                    flds = []
                    # s = ''
                    for i in xrange(rec.count()):
                        flds.append(rec.fieldName(i))
                        # s = s + rec.fieldName(i)

                    if flds==self.poiflds:
                        poin += 1
                        q = idb.exec_('select localid, code, activity, hrid, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            sql = "insert into poistmp (localid, code, activity, hrid, geom) values ('%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));" \
                                % (q.value(0), q.value(1), q.value(2), q.value(3), q.value(4))
                            rs = cur.execute(sql)

                    if flds == self.obrflds:
                        q = idb.exec_('select localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            g = q.value(16)
                            if g.find('POINT(')==-1:
                                t = 'oareatmp'
                                oarean += 1
                            else:
                                t = 'opointtmp'
                                opointn += 1

                            try:
                                v1 = int(q.value(4))
                            except ValueError:
                                v1 = 'NULL'

                            try:
                                v2 = int(q.value(7))
                            except ValueError:
                                v2 = 'NULL'

                            sql = """
                                insert into %s (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                                values ('%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (t, q.value(0), q.value(1), q.value(2), q.value(3),
                                   v1, q.value(5), q.value(6), v2, q.value(8), q.value(9), q.value(10), q.value(11),
                                   q.value(12), q.value(13), q.value(14), q.value(15), g)
                            rs = cur.execute(sql)

                    if flds == bflds:
                        buffn += 1
                        q = idb.exec_('select localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            try:
                                v1 = int(q.value(4))
                            except ValueError:
                                v1 = 'NULL'

                            try:
                                v2 = int(q.value(7))
                            except ValueError:
                                v2 = 'NULL'

                            sql = """
                                insert into bufferstmp (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, geom)
                                values ('%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (q.value(0), q.value(1), q.value(2), q.value(3),
                                   v1, q.value(5), q.value(6), v2, q.value(8), q.value(9), q.value(10), q.value(11),
                                   q.value(12), q.value(13), q.value(14), q.value(15))
                            rs = cur.execute(sql)

                    if flds == zflds:
                        zonen += 1
                        q = idb.exec_('select localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            sql = """
                                insert into zonestmp (localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, geom)
                                values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (q.value(0), q.value(1), q.value(2), q.value(3), q.value(4), q.value(5), q.value(6), q.value(7), q.value(8), q.value(9), q.value(10), q.value(11), q.value(12), q.value(13), q.value(14), q.value(15), q.value(16), q.value(17), q.value(18), q.value(19), q.value(20), q.value(21))
                            rs = cur.execute(sql)

                if oarean>0:
                    sql = """
                        insert into outbreaks_area (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                        select
                          oareatmp.localid,
                          oareatmp.code,
                          oareatmp.largescale,
                          oareatmp.disease,
                          oareatmp.animalno,
                          oareatmp.species,
                          oareatmp.production,
                          oareatmp.year,
                          oareatmp.status,
                          oareatmp.suspect,
                          oareatmp.confirmation,
                          oareatmp.expiration,
                          oareatmp.notes,
                          oareatmp.hrid,
                          oareatmp.timestamp,
                          oareatmp.grouping,
                          oareatmp.geom
                        from oareatmp left join outbreaks_area on oareatmp.hrid=outbreaks_area.hrid where outbreaks_area.hrid is null;
                    """
                    rs = cur.execute(sql)
                    sql = """
                        update outbreaks_area
                        set localid = (select localid from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          code = (select code from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          largescale = (select largescale from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          disease = (select disease from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          animalno = (select animalno from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          species = (select species from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          production = (select production from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          year = (select year from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          status = (select status from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          suspect = (select suspect from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          confirmation = (select confirmation from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          expiration = (select expiration from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          notes = (select notes from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          hrid = (select hrid from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          timestamp = (select timestamp from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          grouping = (select grouping from oareatmp where outbreaks_area.hrid = oareatmp.hrid),
                          geom = (select geom from oareatmp where outbreaks_area.hrid = oareatmp.hrid)
                          WHERE EXISTS (select * from oareatmp where outbreaks_area.hrid = oareatmp.hrid)
                        ;
                    """
                    rs = cur.execute(sql)

                if opointn>0:
                    sql = """
                        insert into outbreaks_point (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                        select
                          opointtmp.localid,
                          opointtmp.code,
                          opointtmp.largescale,
                          opointtmp.disease,
                          opointtmp.animalno,
                          opointtmp.species,
                          opointtmp.production,
                          opointtmp.year,
                          opointtmp.status,
                          opointtmp.suspect,
                          opointtmp.confirmation,
                          opointtmp.expiration,
                          opointtmp.notes,
                          opointtmp.hrid,
                          opointtmp.timestamp,
                          opointtmp.grouping,
                          opointtmp.geom
                        from opointtmp left join outbreaks_point on opointtmp.hrid=outbreaks_point.hrid where outbreaks_point.hrid is null;
                    """
                    rs = cur.execute(sql)
                    sql = """
                        update outbreaks_point
                        set localid = (select localid from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          code = (select code from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          largescale = (select largescale from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          disease = (select disease from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          animalno = (select animalno from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          species = (select species from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          production = (select production from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          year = (select year from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          status = (select status from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          suspect = (select suspect from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          confirmation = (select confirmation from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          expiration = (select expiration from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          notes = (select notes from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          hrid = (select hrid from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          timestamp = (select timestamp from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          grouping = (select grouping from opointtmp where outbreaks_point.hrid = opointtmp.hrid),
                          geom = (select geom from opointtmp where outbreaks_point.hrid = opointtmp.hrid)
                          WHERE EXISTS (select * from opointtmp where outbreaks_point.hrid = opointtmp.hrid)
                        ;
                    """
                    rs = cur.execute(sql)

                if poin>0:
                    sql = """
                        insert into pois (localid, code, activity, hrid, geom)
                        select
                          poistmp.localid,
                          poistmp.code,
                          poistmp.activity,
                          poistmp.hrid,
                          poistmp.geom
                        from poistmp left join pois on poistmp.hrid=pois.hrid where pois.hrid is null;
                    """
                    rs = cur.execute(sql)
                    sql = """
                        update pois
                        set localid = (select localid from poistmp where pois.hrid = poistmp.hrid),
                          code = (select code from poistmp where pois.hrid = poistmp.hrid),
                          activity = (select activity from poistmp where pois.hrid = poistmp.hrid),
                          hrid = (select hrid from poistmp where pois.hrid = poistmp.hrid),
                          geom = (select geom from poistmp where pois.hrid = poistmp.hrid)
                          WHERE EXISTS (select * from poistmp where pois.hrid = poistmp.hrid)
                        ;
                    """
                    rs = cur.execute(sql)


                if buffn>0:
                    sql = """
                        insert into buffers (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, geom)
                        select
                          bufferstmp.localid,
                          bufferstmp.code,
                          bufferstmp.largescale,
                          bufferstmp.disease,
                          bufferstmp.animalno,
                          bufferstmp.species,
                          bufferstmp.production,
                          bufferstmp.year,
                          bufferstmp.status,
                          bufferstmp.suspect,
                          bufferstmp.confirmation,
                          bufferstmp.expiration,
                          bufferstmp.notes,
                          bufferstmp.hrid,
                          bufferstmp.timestamp,
                          bufferstmp.geom
                        from bufferstmp left join buffers on bufferstmp.hrid=buffers.hrid where buffers.hrid is null;
                    """
                    rs = cur.execute(sql)
                    sql = """
                        update buffers
                        set localid = (select localid from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          code = (select code from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          largescale = (select largescale from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          disease = (select disease from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          animalno = (select animalno from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          species = (select species from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          production = (select production from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          year = (select year from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          status = (select status from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          suspect = (select suspect from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          confirmation = (select confirmation from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          expiration = (select expiration from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          notes = (select notes from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          hrid = (select hrid from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          timestamp = (select timestamp from bufferstmp where buffers.hrid = bufferstmp.hrid),
                          geom = (select geom from bufferstmp where buffers.hrid = bufferstmp.hrid)
                          WHERE EXISTS (select * from bufferstmp where buffers.hrid = bufferstmp.hrid)
                        ;
                    """
                    rs = cur.execute(sql)


                if zonen>0:
                    sql = """
                        insert into zones (localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, geom)
                        select
                          zonestmp.localid,
                          zonestmp.code,
                          zonestmp.disease,
                          zonestmp.zonetype,
                          zonestmp.subpopulation,
                          zonestmp.validity_start,
                          zonestmp.validity_end,
                          zonestmp.legal_framework,
                          zonestmp.competent_authority,
                          zonestmp.biosecurity_measures,
                          zonestmp.control_of_vectors,
                          zonestmp.control_of_wildlife_reservoir,
                          zonestmp.modified_stamping_out,
                          zonestmp.movement_restriction,
                          zonestmp.stamping_out,
                          zonestmp.surveillance,
                          zonestmp.vaccination,
                          zonestmp.other_measure,
                          zonestmp.related,
                          zonestmp.hrid,
                          zonestmp.timestamp,
                          zonestmp.geom
                        from zonestmp left join zones on zonestmp.hrid=zones.hrid where zones.hrid is null;
                    """
                    rs = cur.execute(sql)
                    sql = """
                        update zones
                        set localid = (select localid from zonestmp where zones.hrid = zonestmp.hrid),
                          code = (select code from zonestmp where zones.hrid = zonestmp.hrid),
                          disease = (select disease from zonestmp where zones.hrid = zonestmp.hrid),
                          zonetype = (select zonetype from zonestmp where zones.hrid = zonestmp.hrid),
                          subpopulation = (select subpopulation from zonestmp where zones.hrid = zonestmp.hrid),
                          validity_start = (select validity_start from zonestmp where zones.hrid = zonestmp.hrid),
                          validity_end = (select validity_end from zonestmp where zones.hrid = zonestmp.hrid),
                          legal_framework = (select legal_framework from zonestmp where zones.hrid = zonestmp.hrid),
                          competent_authority = (select competent_authority from zonestmp where zones.hrid = zonestmp.hrid),
                          biosecurity_measures = (select biosecurity_measures from zonestmp where zones.hrid = zonestmp.hrid),
                          control_of_vectors = (select control_of_vectors from zonestmp where zones.hrid = zonestmp.hrid),
                          control_of_wildlife_reservoir = (select control_of_wildlife_reservoir from zonestmp where zones.hrid = zonestmp.hrid),
                          modified_stamping_out = (select modified_stamping_out from zonestmp where zones.hrid = zonestmp.hrid),
                          movement_restriction = (select movement_restriction from zonestmp where zones.hrid = zonestmp.hrid),
                          stamping_out = (select stamping_out from zonestmp where zones.hrid = zonestmp.hrid),
                          surveillance = (select surveillance from zonestmp where zones.hrid = zonestmp.hrid),
                          vaccination = (select vaccination from zonestmp where zones.hrid = zonestmp.hrid),
                          other_measure = (select other_measure from zonestmp where zones.hrid = zonestmp.hrid),
                          related = (select related from zonestmp where zones.hrid = zonestmp.hrid),
                          hrid = (select hrid from zonestmp where zones.hrid = zonestmp.hrid),
                          timestamp = (select timestamp from zonestmp where zones.hrid = zonestmp.hrid),
                          geom = (select geom from zonestmp where zones.hrid = zonestmp.hrid)
                          WHERE EXISTS (select * from zonestmp where zones.hrid = zonestmp.hrid)
                        ;
                    """
                    rs = cur.execute(sql)

                    rs = cur.execute("DROP TABLE opointtmp;")
                    rs = cur.execute("delete from geometry_columns where  f_table_name='opointtmp';")
                    rs = cur.execute("DROP TABLE oareatmp;")
                    rs = cur.execute("delete from geometry_columns where  f_table_name='oareatmp';")
                    rs = cur.execute("DROP TABLE poistmp;")
                    rs = cur.execute("delete from geometry_columns where  f_table_name='poistmp';")
                    rs = cur.execute("DROP TABLE bufferstmp;")
                    rs = cur.execute("delete from geometry_columns where  f_table_name='bufferstmp';")
                    rs = cur.execute("DROP TABLE zonestmp;")
                    rs = cur.execute("delete from geometry_columns where  f_table_name='zonestmp';")

                conn.commit()
                rs.close()
                conn.close()


            if self.dbtype == 'postgis':
                idb = QSqlDatabase.addDatabase('QSPATIALITE')
                idb.setDatabaseName(self.ipath)
                idb.open()
                tablst = idb.tables()

                for tab in tablst:
                    rec = idb.record(tab)
                    flds = []
                    for i in xrange(rec.count()):
                        flds.append(rec.fieldName(i))

                    if flds == self.poiflds:
                        poin += 1
                        q = idb.exec_('select localid, code, activity, hrid, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            isql = isql + "insert into poistmp (localid, code, activity, hrid, geom) values ('%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));" \
                                          % (q.value(0), q.value(1), q.value(2), q.value(3), q.value(4))

                    if flds == self.obrflds:
                        q = idb.exec_(
                            'select localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            g = q.value(16)
                            if g.find('POINT(') == -1:
                                t = 'oareatmp'
                                oarean += 1
                            else:
                                t = 'opointtmp'
                                opointn += 1

                            try:
                                v1 = int(q.value(4))
                            except ValueError:
                                v1 = 'NULL'

                            try:
                                v2 = int(q.value(7))
                            except ValueError:
                                v2 = 'NULL'

                            isql = isql + """
                                insert into %s (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                                values ('%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (t, q.value(0), q.value(1), q.value(2), q.value(3),
                                   v1, q.value(5), q.value(6), v2, q.value(8), q.value(9), q.value(10), q.value(11),
                                   q.value(12), q.value(13), q.value(14), q.value(15), g)

                    if flds == bflds:
                        buffn += 1
                        q = idb.exec_(
                            'select localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            try:
                                v1 = int(q.value(4))
                            except ValueError:
                                v1 = 'NULL'

                            try:
                                v2 = int(q.value(7))
                            except ValueError:
                                v2 = 'NULL'

                            isql = isql + """
                                insert into bufferstmp (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, geom)
                                values ('%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (q.value(0), q.value(1), q.value(2), q.value(3),
                                   v1, q.value(5), q.value(6), v2, q.value(8), q.value(9), q.value(10), q.value(11),
                                   q.value(12), q.value(13), q.value(14), q.value(15))

                    if flds == zflds:
                        zonen += 1
                        q = idb.exec_(
                            'select localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, astext(geom) as geom from %s;' % tab)
                        while q.next():
                            isql = isql + """
                                insert into zonestmp (localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, geom)
                                values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s', 4326));
                            """ % (q.value(0), q.value(1), q.value(2), q.value(3), q.value(4), q.value(5), q.value(6),
                                   q.value(7), q.value(8), q.value(9), q.value(10), q.value(11), q.value(12),
                                   q.value(13), q.value(14), q.value(15), q.value(16), q.value(17), q.value(18),
                                   q.value(19), q.value(20), q.value(21))

                idb.close()

                csql = """
                    CREATE TABLE opointtmp (
                      gid serial NOT NULL,
                      localid character varying(254),
                      code character varying(254),
                      largescale character varying(254),
                      disease character varying(254),
                      animalno integer,
                      species character varying(254),
                      production character varying(254),
                      year integer,
                      status character varying(254),
                      suspect character varying(254),
                      confirmation character varying(254),
                      expiration character varying(254),
                      notes character varying(254),
                      hrid character varying(254),
                      timestamp character varying(254),
                      grouping character varying(254),
                      geom geometry,
                      CONSTRAINT opointtmp_pkey PRIMARY KEY (gid),
                      CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                      CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'POINT'::text OR geom IS NULL),
                      CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                    );
                    CREATE TABLE oareatmp (
                      gid serial NOT NULL,
                      localid character varying(254),
                      code character varying(254),
                      largescale character varying(254),
                      disease character varying(254),
                      animalno integer,
                      species character varying(254),
                      production character varying(254),
                      year integer,
                      status character varying(254),
                      suspect character varying(254),
                      confirmation character varying(254),
                      expiration character varying(254),
                      notes character varying(254),
                      hrid character varying(254),
                      timestamp character varying(254),
                      grouping character varying(254),
                      geom geometry,
                      CONSTRAINT oareatmp_pkey PRIMARY KEY (gid),
                      CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                      CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                      CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                    );
                    CREATE TABLE poistmp (
                      gid serial NOT NULL,
                      localid character varying(254),
                      code character varying(254),
                      activity character varying(254),
                      hrid character varying(254),
                      geom geometry,
                      CONSTRAINT poistmp_pkey PRIMARY KEY (gid),
                      CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                      CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'POINT'::text OR geom IS NULL),
                      CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                    );
                    CREATE TABLE bufferstmp (
                      gid serial NOT NULL,
                      localid character varying(254),
                      code character varying(254),
                      largescale character varying(254),
                      disease character varying(254),
                      animalno integer,
                      species character varying(254),
                      production character varying(254),
                      year integer,
                      status character varying(254),
                      suspect character varying(254),
                      confirmation character varying(254),
                      expiration character varying(254),
                      notes character varying(254),
                      hrid character varying(254),
                      timestamp character varying(254),
                      geom geometry,
                      CONSTRAINT bufferstmp_pkey PRIMARY KEY (gid),
                      CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                      CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                      CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                    );
                    CREATE TABLE zonestmp (
                      gid serial NOT NULL,
                      localid character varying(254),
                      code character varying(254),
                      disease character varying(254),
                      zonetype character varying(254),
                      subpopulation character varying(254),
                      validity_start character varying(254),
                      validity_end character varying(254),
                      legal_framework character varying(254),
                      competent_authority character varying(254),
                      biosecurity_measures character varying(254),
                      control_of_vectors character varying(254),
                      control_of_wildlife_reservoir character varying(254),
                      modified_stamping_out character varying(254),
                      movement_restriction character varying(254),
                      stamping_out character varying(254),
                      surveillance character varying(254),
                      vaccination character varying(254),
                      other_measure character varying(254),
                      related character varying(254),
                      hrid character varying(254),
                      timestamp character varying(254),
                      geom geometry,
                      CONSTRAINT zonestmp_pkey PRIMARY KEY (gid),
                      CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                      CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                      CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                    );
                """

                if oarean>0:
                    sqlinup = sqlinup + """
                        insert into outbreaks_area (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                        select
                          oareatmp.localid,
                          oareatmp.code,
                          oareatmp.largescale,
                          oareatmp.disease,
                          oareatmp.animalno,
                          oareatmp.species,
                          oareatmp.production,
                          oareatmp.year,
                          oareatmp.status,
                          oareatmp.suspect,
                          oareatmp.confirmation,
                          oareatmp.expiration,
                          oareatmp.notes,
                          oareatmp.hrid,
                          oareatmp.timestamp,
                          oareatmp.grouping,
                          oareatmp.geom
                        from outbreaks_area right join oareatmp on outbreaks_area.hrid = oareatmp.hrid where outbreaks_area.hrid is null;
                        update outbreaks_area as t
                        set localid = s.localid,
                          code = s.code,
                          largescale = s.largescale,
                          disease = s.disease,
                          animalno = s.animalno,
                          species = s.species,
                          production = s.production,
                          year = s.year,
                          status = s.status,
                          suspect = s.suspect,
                          confirmation = s.confirmation,
                          expiration = s.expiration,
                          notes = s.notes,
                          hrid = s.hrid,
                          timestamp = s.timestamp,
                          grouping = s.grouping,
                          geom = s.geom
                        from oareatmp as s where t.hrid = s.hrid;
                    """

                if opointn>0:
                    sqlinup = sqlinup + """
                        insert into outbreaks_point (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, grouping, geom)
                        select
                          opointtmp.localid,
                          opointtmp.code,
                          opointtmp.largescale,
                          opointtmp.disease,
                          opointtmp.animalno,
                          opointtmp.species,
                          opointtmp.production,
                          opointtmp.year,
                          opointtmp.status,
                          opointtmp.suspect,
                          opointtmp.confirmation,
                          opointtmp.expiration,
                          opointtmp.notes,
                          opointtmp.hrid,
                          opointtmp.timestamp,
                          opointtmp.grouping,
                          opointtmp.geom
                        from outbreaks_point right join opointtmp on outbreaks_point.hrid = opointtmp.hrid where outbreaks_point.hrid is null;
                        update outbreaks_point as t
                        set localid = s.localid,
                          code = s.code,
                          largescale = s.largescale,
                          disease = s.disease,
                          animalno = s.animalno,
                          species = s.species,
                          production = s.production,
                          year = s.year,
                          status = s.status,
                          suspect = s.suspect,
                          confirmation = s.confirmation,
                          expiration = s.expiration,
                          notes = s.notes,
                          hrid = s.hrid,
                          timestamp = s.timestamp,
                          grouping = s.grouping,
                          geom = s.geom
                        from opointtmp as s where t.hrid = s.hrid;
                    """

                if poin>0:
                    sqlinup = sqlinup + """
                        insert into pois (localid, code, activity, hrid, geom)
                        select
                          poistmp.localid,
                          poistmp.code,
                          poistmp.activity,
                          poistmp.hrid,
                          poistmp.geom
                        from pois right join poistmp on pois.hrid = poistmp.hrid where pois.hrid is null;
                        update pois as t
                        set localid = s.localid,
                          code = s.code,
                          activity = s.activity,
                          hrid = s.hrid,
                          geom = s.geom
                        from poistmp as s where t.hrid = s.hrid;
                    """

                if buffn>0:
                    sqlinup = sqlinup + """
                        insert into buffers (localid, code, largescale, disease, animalno, species, production, year, status, suspect, confirmation, expiration, notes, hrid, timestamp, geom)
                        select
                          bufferstmp.localid,
                          bufferstmp.code,
                          bufferstmp.largescale,
                          bufferstmp.disease,
                          bufferstmp.animalno,
                          bufferstmp.species,
                          bufferstmp.production,
                          bufferstmp.year,
                          bufferstmp.status,
                          bufferstmp.suspect,
                          bufferstmp.confirmation,
                          bufferstmp.expiration,
                          bufferstmp.notes,
                          bufferstmp.hrid,
                          bufferstmp.timestamp,
                          bufferstmp.geom
                        from buffers right join bufferstmp on buffers.hrid = bufferstmp.hrid where buffers.hrid is null;
                        update buffers as t
                        set localid = s.localid,
                          code = s.code,
                          largescale = s.largescale,
                          disease = s.disease,
                          animalno = s.animalno,
                          species = s.species,
                          production = s.production,
                          year = s.year,
                          status = s.status,
                          suspect = s.suspect,
                          confirmation = s.confirmation,
                          expiration = s.expiration,
                          notes = s.notes,
                          hrid = s.hrid,
                          timestamp = s.timestamp,
                          geom = s.geom
                        from bufferstmp as s where t.hrid = s.hrid;
                    """

                if zonen>0:
                    sqlinup = sqlinup + """
                        insert into zones (localid, code, disease, zonetype, subpopulation, validity_start, validity_end, legal_framework, competent_authority, biosecurity_measures, control_of_vectors, control_of_wildlife_reservoir, modified_stamping_out, movement_restriction, stamping_out, surveillance, vaccination, other_measure, related, hrid, timestamp, geom)
                        select
                          zonestmp.localid,
                          zonestmp.code,
                          zonestmp.disease,
                          zonestmp.zonetype,
                          zonestmp.subpopulation,
                          zonestmp.validity_start,
                          zonestmp.validity_end,
                          zonestmp.legal_framework,
                          zonestmp.competent_authority,
                          zonestmp.biosecurity_measures,
                          zonestmp.control_of_vectors,
                          zonestmp.control_of_wildlife_reservoir,
                          zonestmp.modified_stamping_out,
                          zonestmp.movement_restriction,
                          zonestmp.stamping_out,
                          zonestmp.surveillance,
                          zonestmp.vaccination,
                          zonestmp.other_measure,
                          zonestmp.related,
                          zonestmp.hrid,
                          zonestmp.timestamp,
                          zonestmp.geom
                        from zones right join zonestmp on zones.hrid = zonestmp.hrid where zones.hrid is null;
                        update zones as t
                        set localid = s.localid,
                          code = s.code,
                          disease = s.disease,
                          zonetype = s.zonetype,
                          subpopulation = s.subpopulation,
                          validity_start = s.validity_start,
                          validity_end = s.validity_end,
                          legal_framework = s.legal_framework,
                          competent_authority = s.competent_authority,
                          biosecurity_measures = s.biosecurity_measures,
                          control_of_vectors = s.control_of_vectors,
                          control_of_wildlife_reservoir = s.control_of_wildlife_reservoir,
                          modified_stamping_out = s.modified_stamping_out,
                          movement_restriction = s.movement_restriction,
                          stamping_out = s.stamping_out,
                          surveillance = s.surveillance,
                          vaccination = s.vaccination,
                          other_measure = s.other_measure,
                          related = s.related,
                          hrid = s.hrid,
                          timestamp = s.timestamp,
                          geom = s.geom
                        from zonestmp as s where t.hrid = s.hrid;
                    """

                #dsql = "DROP TABLE IF EXISTS oareatmp, opointtmp, poistmp, bufferstmp, zonestmp;"

                sql = csql + isql + sqlinup + dsql

                cursor = self.PGcon.cursor()
                cursor.execute(sql)
                self.PGcon.commit()

            self.iface.messageBar().pushMessage('Information', 'Selected database merged into the target database.', level=Qgis.Info)

            QApplication.restoreOverrideCursor()

    def loadDB(self):
        tool_name = 'Load database'
        dlg = dbconnection.Dialog()
        dlg.setWindowTitle(tool_name)
        dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        self.settings.beginGroup('PostgreSQL/connections')
        PGconns = self.settings.childGroups()
        for pg in PGconns:
            dlg.comboBox_pg_db.addItem(pg)
        self.settings.endGroup()

        dlg.settings = self.settings

        if dlg.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if dlg.radioButton_spatialite.isChecked():

                self.ipath = dlg.lineEdit_spatialite.text()
                idb = QSqlDatabase.addDatabase('QSPATIALITE')
                idb.setDatabaseName(self.ipath)
                if not idb.open():
                    idb.open()
                tablst = idb.tables()

                #Check if all tables exist in database
                for tab in self.tableList:
                    if tab not in tablst:
                        self.iface.messageBar().pushMessage(tool_name, "Database NOT loaded. One or more tables don't exist", level=Qgis.Warning, duration=10)
                        QApplication.restoreOverrideCursor()
                        return

                self.iface.messageBar().pushMessage(tool_name, "Database loaded.", level=Qgis.Info, duration=10)
                self.dbtype = 'spatialite'
                self.dbpath = self.ipath

            elif dlg.radioButton_postgis.isChecked():
                self.settings.beginGroup('PostgreSQL/connections/' + dlg.comboBox_pg_db.currentText())
                PGhost = self.settings.value('host', '')
                PGport = self.settings.value('port', '')
                PGdatabase = self.settings.value('database', '')
                PGusername = self.settings.value('username', '')
                PGpassword = self.settings.value('password', '')
                self.settings.endGroup()

                #check if pw and user exist
                PGcon = None
                if not PGusername or PGusername =='':
                    dlg2 = dblogin.Dialog()
                    dlg2.setWindowTitle('Set login')
                    dlg2.plugin_dir = self.plugin_dir
                    x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg2.width()/2
                    y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg2.height()/2
                    dlg2.move(x,y)

                    if dlg2.exec_() == QDialog.Accepted:
                        PGusername = dlg2.lineEdit_user.text()
                        PGpassword = dlg2.lineEdit_pw.text()

                        if (not PGusername or PGusername =='') or (not PGpassword or PGpassword ==''):
                            self.iface.messageBar().pushMessage(tool_name, 'Write user and password to connect to database', level=Qgis.Warning, duration=10)
                            QApplication.restoreOverrideCursor()
                            return
                    else:
                        self.iface.messageBar().pushMessage(tool_name, 'Write user and password to connect to database', level=Qgis.Warning, duration=10)
                        QApplication.restoreOverrideCursor()
                        return

                try:
                    self.PGcon = psycopg2.connect(host=PGhost, port=PGport, database=PGdatabase, user=PGusername, password=PGpassword)
                except Exception:
                    self.PGcon = psycopg2.connect(host=PGhost, database=PGdatabase, user=PGusername, password=PGpassword)

                #check if database is spatial
                # https://stackoverflow.com/questions/53462775/how-to-determine-if-postgis-is-enabled-on-a-database
                cursor = self.PGcon.cursor()
                try:
                    sql = "SELECT PostGIS_version();"
                    cursor.execute(sql)
                except  psycopg2.Error as e:
                    self.iface.messageBar().pushMessage(tool_name, 'Select a SPATIAL database!', level=Qgis.Warning, duration=10)
                    self.PGcon.close()
                    QApplication.restoreOverrideCursor()
                    return

                # Check if tables already exist
                cursor = self.PGcon.cursor()
                # https://www.dbrnd.com/2017/07/postgresql-different-options-to-check-if-table-exists-in-database-to_regclass/
                # check on public schema
                sql = """SELECT table_name
                         FROM information_schema.tables
                         WHERE table_schema = 'public'; """

                cursor.execute(sql)
                ret_q = cursor.fetchall()
                table_q_list = []
                for a in ret_q:
                    table_q_list.append(a[0])

                for tab in self.tableList:
                    if tab not in table_q_list:
                        self.iface.messageBar().pushMessage(tool_name, "Database NOT loaded. One or more tables don't exist", level=Qgis.Warning, duration=10)
                        QApplication.restoreOverrideCursor()
                        return

                self.iface.messageBar().pushMessage(tool_name, 'Database loaded.', level=Qgis.Info)
                self.dbtype = 'postgis'
                self.dbpath = dlg.comboBox_pg_db.currentText()

            QApplication.restoreOverrideCursor()


    def setupDB(self):
        tool_name = 'Setup working database'
        dlg = dbsetup.Dialog()
        dlg.setWindowTitle('Setup database connection')
        dlg.plugin_dir = self.plugin_dir
        x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg.width()/2
        y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg.height()/2
        dlg.move(x,y)

        self.settings.beginGroup('PostgreSQL/connections')
        self.PGconns = self.settings.childGroups()
        for pg in self.PGconns:
            dlg.comboBox_pg_db.addItem(pg)
        self.settings.endGroup()

        dlg.settings = self.settings

        if dlg.exec_() == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            if dlg.radioButton_spatialite.isChecked():
                ret_sl = self.createNewSLdb(dlg.lineEdit_spatialite.text())
                if ret_sl:
                    self.dbtype = 'spatialite'
                    self.dbpath = dlg.lineEdit_spatialite.text()
                    self.iface.messageBar().pushMessage(tool_name, 'Created database.', level=Qgis.Info)
                    self.sl_path_memorized = dlg.comboBox_pg_db.currentText()
                else:
                    self.iface.messageBar().pushMessage(tool_name, 'Error creating database.', level=Qgis.Warning)

            elif dlg.radioButton_postgis.isChecked():
                self.settings.beginGroup('PostgreSQL/connections/' + dlg.comboBox_pg_db.currentText())
                PGhost = self.settings.value('host', '')
                PGport = self.settings.value('port', '')
                PGdatabase = self.settings.value('database', '')
                PGusername = self.settings.value('username', '')
                PGpassword = self.settings.value('password', '')
                self.settings.endGroup()

                #check if pw and user exist
                self.PGcon = None
                if not PGusername or PGusername =='':
                    dlg2 = dblogin.Dialog()
                    dlg2.setWindowTitle('Set login')
                    dlg2.plugin_dir = self.plugin_dir
                    x = (self.iface.mainWindow().x()+self.iface.mainWindow().width()/2)-dlg2.width()/2
                    y = (self.iface.mainWindow().y()+self.iface.mainWindow().height()/2)-dlg2.height()/2
                    dlg2.move(x,y)

                    if dlg2.exec_() == QDialog.Accepted:
                        PGusername = dlg2.lineEdit_user.text()
                        PGpassword = dlg2.lineEdit_pw.text()

                        if (not PGusername or PGusername =='') or (not PGpassword or PGpassword ==''):
                            self.iface.messageBar().pushMessage(tool_name, 'Write user and password to connect to database', level=Qgis.Warning, duration=10)
                            QApplication.restoreOverrideCursor()
                            return
                    else:
                        self.iface.messageBar().pushMessage(tool_name, 'Write user and password to connect to database', level=Qgis.Warning, duration=10)
                        QApplication.restoreOverrideCursor()
                        return

                try:
                    self.PGcon = psycopg2.connect(host=PGhost, port=PGport, database=PGdatabase, user=PGusername, password=PGpassword)
                except Exception:
                    self.PGcon = psycopg2.connect(host=PGhost, database=PGdatabase, user=PGusername, password=PGpassword)

                #check if database is spatial
                # https://stackoverflow.com/questions/53462775/how-to-determine-if-postgis-is-enabled-on-a-database
                cursor = self.PGcon.cursor()
                try:
                    sql = "SELECT PostGIS_version();"
                    cursor.execute(sql)
                except  psycopg2.Error as e:
                    self.iface.messageBar().pushMessage(tool_name, 'Select a SPATIAL database!', level=Qgis.Warning, duration=10)
                    self.PGcon.close()
                    QApplication.restoreOverrideCursor()
                    return

                # Check if tables already exist
                cursor = self.PGcon.cursor()
                # https://www.dbrnd.com/2017/07/postgresql-different-options-to-check-if-table-exists-in-database-to_regclass/
                # check on public schema
                sql = """SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND (table_name = 'outbreaks_point'
                                OR table_name = 'outbreaks_area'
                                OR table_name = 'pois'
                                OR table_name = 'buffers'
                                OR table_name = 'zones'
                                OR table_name = 'xdiseases'
                                OR table_name = 'xpoitypes'
                                OR table_name = 'xspecies'
                                OR table_name = 'xstyles')); """

                cursor.execute(sql)
                ret_q = cursor.fetchone()
                # if a table already exist end the tool
                if ret_q[0]:
                    self.iface.messageBar().clearWidgets()
                    self.iface.messageBar().pushMessage(tool_name, 'Tables already exist. No tables were added to database', level=Qgis.Warning, duration=10)
                else:
                    ret_pg = self.createPGtables(PGdatabase)
                    if ret_pg:
                        self.iface.messageBar().pushMessage(tool_name, 'Added tables to database.', level=Qgis.Info)
                        self.pg_memorized = dlg.comboBox_pg_db.currentText()
                    else:
                        self.iface.messageBar().pushMessage(tool_name, 'Error adding tables database.', level=Qgis.Warning)

            QApplication.restoreOverrideCursor()


    def createNewSLdb(self, fileName):
        #↓fileName = QFileDialog.getSaveFileName(self, caption='Create new SpatiaLite database')
        #fileName = fileName[0]
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            #file = QFile(fileName + '.sqlite')
            file = fileName
            dbpath = QFileInfo(file).absoluteFilePath()
            dbfold = os.path.join(self.plugin_dir, 'db')
            if not os.path.isfile(dbpath):
                shutil.copy(os.path.join(dbfold, 'base.sqlite'), dbpath)
                #self.lineEdit_spatialite.setText(dbpath)

                db = QSqlDatabase.addDatabase('QSPATIALITE')
                db.setDatabaseName(dbpath)
                db.open()
                query = db.exec_(
                """
                    CREATE TABLE outbreaks_point (
                      gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                      localid text,
                      code text,
                      largescale text,
                      disease text,
                      animalno numeric,
                      species text,
                      production text,
                      year numeric,
                      status text,
                      suspect text,
                      confirmation text,
                      expiration text,
                      notes text,
                      hrid text,
                      timestamp text,
                      grouping text
                    );
                """
                )
                query = db.exec_("SELECT AddGeometryColumn('outbreaks_point', 'geom', 4326, 'POINT', 'XY');")
                query = db.exec_(
                """
                    CREATE TABLE outbreaks_area (
                      gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                      localid text,
                      code text,
                      largescale text,
                      disease text,
                      animalno numeric,
                      species text,
                      production text,
                      year numeric,
                      status text,
                      suspect text,
                      confirmation text,
                      expiration text,
                      notes text,
                      hrid text,
                      timestamp text,
                      grouping text
                    );
                """
                )
                query = db.exec_("SELECT AddGeometryColumn('outbreaks_area', 'geom', 4326, 'MULTIPOLYGON', 'XY');")
                query = db.exec_(
                """
                CREATE TABLE pois (
                  gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  localid text,
                  code text,
                  activity text,
                  hrid text
                );
                """)
                query = db.exec_("SELECT AddGeometryColumn('pois', 'geom', 4326, 'POINT', 'XY');")
                query = db.exec_(
                """
                CREATE TABLE buffers (
                  gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  localid text,
                  code text,
                  largescale text,
                  disease text,
                  animalno numeric,
                  species text,
                  production text,
                  year numeric,
                  status text,
                  suspect text,
                  confirmation text,
                  expiration text,
                  notes text,
                  hrid text,
                  timestamp text
                );
                """)
                query = db.exec_("SELECT AddGeometryColumn('buffers', 'geom', 4326, 'MULTIPOLYGON', 'XY');")
                query = db.exec_(
                """
                CREATE TABLE zones (
                  gid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  localid text,
                  code text,
                  disease text,
                  zonetype text,
                  subpopulation text,
                  validity_start text,
                  validity_end text,
                  legal_framework text,
                  competent_authority text,
                  biosecurity_measures text,
                  control_of_vectors text,
                  control_of_wildlife_reservoir text,
                  modified_stamping_out text,
                  movement_restriction text,
                  stamping_out text,
                  surveillance text,
                  vaccination text,
                  other_measure text,
                  related text,
                  hrid text,
                  timestamp text
                );
                """)
                query = db.exec_("SELECT AddGeometryColumn('zones', 'geom', 4326, 'MULTIPOLYGON', 'XY');")
                db.close()

            QApplication.restoreOverrideCursor()
            return True
        except IOError:
            QApplication.restoreOverrideCursor()
            return False


    def createPGtables(self, db_name):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:

            cursor = self.PGcon.cursor()
            sql = """

                CREATE TABLE outbreaks_point (
                gid serial NOT NULL,
                localid character varying(254),
                code character varying(254),
                largescale character varying(254),
                disease character varying(254),
                animalno integer,
                species character varying(254),
                production character varying(254),
                year integer,
                status character varying(254),
                suspect character varying(254),
                confirmation character varying(254),
                expiration character varying(254),
                notes character varying(254),
                hrid character varying(254),
                timestamp character varying(254),
                grouping character varying(254),
                geom geometry,
                CONSTRAINT outbreaks_point_pkey PRIMARY KEY (gid),
                CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'POINT'::text OR geom IS NULL),
                CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                );
                CREATE TABLE outbreaks_area (
                gid serial NOT NULL,
                localid character varying(254),
                code character varying(254),
                largescale character varying(254),
                disease character varying(254),
                animalno integer,
                species character varying(254),
                production character varying(254),
                year integer,
                status character varying(254),
                suspect character varying(254),
                confirmation character varying(254),
                expiration character varying(254),
                notes character varying(254),
                hrid character varying(254),
                timestamp character varying(254),
                grouping character varying(254),
                geom geometry,
                CONSTRAINT outbreaks_area_pkey PRIMARY KEY (gid),
                CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                );
                CREATE TABLE pois (
                gid serial NOT NULL,
                localid character varying(254),
                code character varying(254),
                activity character varying(254),
                hrid character varying(254),
                geom geometry,
                CONSTRAINT pois_pkey PRIMARY KEY (gid),
                CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'POINT'::text OR geom IS NULL),
                CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                );
                CREATE TABLE buffers (
                gid serial NOT NULL,
                localid character varying(254),
                code character varying(254),
                largescale character varying(254),
                disease character varying(254),
                animalno integer,
                species character varying(254),
                production character varying(254),
                year integer,
                status character varying(254),
                suspect character varying(254),
                confirmation character varying(254),
                expiration character varying(254),
                notes character varying(254),
                hrid character varying(254),
                timestamp character varying(254),
                geom geometry,
                CONSTRAINT buffers_pkey PRIMARY KEY (gid),
                CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                );
                CREATE TABLE zones (
                gid serial NOT NULL,
                localid character varying(254),
                code character varying(254),
                disease character varying(254),
                zonetype character varying(254),
                subpopulation character varying(254),
                validity_start character varying(254),
                validity_end character varying(254),
                legal_framework character varying(254),
                competent_authority character varying(254),
                biosecurity_measures character varying(254),
                control_of_vectors character varying(254),
                control_of_wildlife_reservoir character varying(254),
                modified_stamping_out character varying(254),
                movement_restriction character varying(254),
                stamping_out character varying(254),
                surveillance character varying(254),
                vaccination character varying(254),
                other_measure character varying(254),
                related character varying(254),
                hrid character varying(254),
                timestamp character varying(254),
                geom geometry,
                CONSTRAINT zones_pkey PRIMARY KEY (gid),
                CONSTRAINT enforce_dims_geom CHECK (st_ndims(geom) = 2),
                CONSTRAINT enforce_geotype_geom CHECK (geometrytype(geom) = 'MULTIPOLYGON'::text OR geom IS NULL),
                CONSTRAINT enforce_srid_geom CHECK (st_srid(geom) = 4326)
                );
                CREATE TABLE xdiseases (
                id serial NOT NULL,
                disease character varying(254),
                lang character varying(254),
                enid integer, CONSTRAINT xdiseases_pkey PRIMARY KEY (id)
                );
                CREATE TABLE xpoitypes (
                id serial NOT NULL,
                poitype character varying(254),
                lang character varying(254),
                enid integer, CONSTRAINT xpoitypes_pkey PRIMARY KEY (id)
                );
                CREATE TABLE xspecies (
                id serial NOT NULL,
                species character varying(254),
                lang character varying(254),
                enid integer, CONSTRAINT xspecies_pkey PRIMARY KEY (id)
                );
                CREATE TABLE xstyles (
                id serial NOT NULL,
                ltype character varying(254),
                sld character varying(254), CONSTRAINT xstyles_pkey PRIMARY KEY (id)
                );
                """
            cursor.execute(sql)

            self.PGcon.commit()

            # uri = QgsDataSourceURI()
            # uri.setDatabase(os.path.join(os.path.join(self.plugin_dir, 'db'), 'base.sqlite'))
            db = QSqlDatabase.addDatabase('QSPATIALITE')
            # db.setDatabaseName(uri.database())
            db.setDatabaseName(os.path.join(os.path.join(self.plugin_dir, 'db'), 'base.sqlite'))

            if not db.open():
                db.open()

            sql = ''
            query = db.exec_('select * from xdiseases')
            while query.next():
                sql = sql + """insert into xdiseases (disease, lang) values('%s', '%s');""" % \
                    (query.value(1).replace("'", "''"), query.value(2))
            cursor.execute(sql)

            sql = ''
            query = db.exec_('select * from xpoitypes')
            while query.next():
                sql = sql + "insert into xpoitypes (poitype, lang) values('%s', '%s');" % \
                    (query.value(1), query.value(2))
            cursor.execute(sql)

            sql = ''
            query = db.exec_('select * from xspecies')
            while query.next():
                sql = sql + "insert into xspecies (species, lang) values('%s', '%s');" % \
                    (query.value(1), query.value(2))
            cursor.execute(sql)

            sql = ''
            query = db.exec_('select * from xstyles')
            while query.next():
                sql = sql + "insert into xstyles (ltype, sld) values('%s', '%s');" % \
                            (query.value(1), query.value(2))
            cursor.execute(sql)

            self.PGcon.commit()
            db.close()

            QApplication.restoreOverrideCursor()

            return True
        except IOError:
            QApplication.restoreOverrideCursor()
            return False




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
        dlg.textEdit.append('VetEpiGIS-Group is a part of VetEpiGIS plugin family helping veterinarian collaboration in the management of spatial data related to animal disease. It provides a set of functionalities to import/export and share data with other users, by allowing the creation of a working team (this would be based on SQLite db and/or Geoserver).\n')
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

class VetLayerType(Enum):
    OUT_PT = 1
    OUT_POLY = 2
    POI_PT = 3
    BUFFER_OUT = 4
    ZONE = 5

