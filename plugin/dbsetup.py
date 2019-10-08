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

from .dbsetup_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):
    def __init__(self):
        """Constructor for the dialog.

        """

        QDialog.__init__(self)

        self.setupUi(self)
        self.plugin_dir = ''
        self.settings = ''

        # self.comboBox.currentIndexChanged.connect(self.seltype)
        self.commandLinkButton.clicked.connect(self.createNewSLdb)
        self.toolButton.clicked.connect(self.dbSource)

        self.groupBox.clicked.connect(self.seltype)
        self.groupBox_2.clicked.connect(self.seltype)

        self.commandLinkButton_2.clicked.connect(self.createPGtables)

        # self.lineEdit.setText('/home/sn/dev/QGISplugins/VetEpiGIS/groupdata/c.sqlite')


    def dbSource(self):
        dbpath = QFileDialog.getOpenFileName(self, 'Select file', QDir.currentPath(), 'SpatiaLite file (*.sqlite *.*)')
        dbpath = dbpath[0]
        if os.path.isfile(dbpath):
            self.lineEdit.setText(dbpath)


    def seltype(self):
        if self.groupBox.isChecked():
            self.groupBox_2.setChecked(False)
            self.groupBox.setChecked(True)

        if self.groupBox_2.isChecked():
            self.groupBox.setChecked(False)
            self.groupBox_2.setChecked(True)

                # self.tabWidget.setCurrentIndex(self.comboBox.currentIndex())
        # if self.comboBox.currentText()=='SpatiaLite':
        #     self.tabWidget.setCurrentIndex(0)
        # else:
        #     self.tabWidget.setCurrentIndex(1)


    def createNewSLdb(self):
        fileName = QFileDialog.getSaveFileName(self, caption='Create new SpatiaLite database')
        fileName = fileName[0]
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            file = QFile(fileName + '.sqlite')
            dbpath = QFileInfo(file).absoluteFilePath()
            dbfold = os.path.join(self.plugin_dir, 'db')
            if not os.path.isfile(dbpath):
                shutil.copy(os.path.join(dbfold, 'base.sqlite'), dbpath)
                self.lineEdit.setText(dbpath)

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
        except IOError:
            return False


    def createPGtables(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.settings.beginGroup('PostgreSQL/connections/' + self.comboBox.currentText())
        PGhost = self.settings.value('host', '')
        PGport = self.settings.value('port', '')
        PGdatabase = self.settings.value('database', '')
        PGusername = self.settings.value('username', '')
        PGpassword = self.settings.value('password', '')
        self.settings.endGroup()

        try:
            PGcon = psycopg2.connect(host=PGhost, port=PGport, database=PGdatabase, user=PGusername, password=PGpassword)
        except TypeError:
            PGcon = psycopg2.connect(host=PGhost, database=PGdatabase, user=PGusername, password=PGpassword)

        cursor = PGcon.cursor()
        sql = """
            --DROP TABLE IF EXISTS xdiseases, xpoitypes, xspecies, xstyles, pois, outbreaks_point, outbreaks_area, buffers, zones;
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

        PGcon.commit()

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

        PGcon.commit()
        db.close()

        # result = cursor.fetchone()

        # self.lineEdit.setText(sql)

        QApplication.restoreOverrideCursor()


