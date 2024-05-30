# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StatsByPolygon
                                 A QGIS plugin
 This plugin creates statistics for raster bands based on selected polygon feature.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-20
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Murat Çalışkan
        email                : caliskan.murat.20@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.utils import iface

from qgis.core import Qgis, QgsProject
from qgis.gui import QgsMapToolPan

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .stats_by_polygon_dialog import StatsByPolygonDialog
import os.path

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    mdlChck_plt = 1
except:
    mdlChck_plt = 0
    

import numpy as np
from osgeo import gdal, ogr
from .zonalstats import ZonalStatistics

class StatsByPolygon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

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
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'StatsByPolygon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Stats By Polygon')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('StatsByPolygon', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/stats_by_polygon/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Stats By Polygon'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Stats By Polygon'),
                action)
            self.iface.removeToolBarIcon(action)

    def getRasterExtent(self, raster):
        geot = raster.GetGeoTransform()
        minx = geot[0]
        maxy = geot[3]
        maxx = minx + geot[1]*raster.RasterXSize
        miny = maxy + geot[5]*raster.RasterYSize
        
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint_2D(minx, miny)
        ring.AddPoint_2D(maxx, miny)
        ring.AddPoint_2D(maxx, maxy)
        ring.AddPoint_2D(minx, maxy)
        ring.AddPoint_2D(minx, miny)
        
        gg = ogr.Geometry(ogr.wkbPolygon)
        gg.AddGeometry(ring)
        
        return gg    

    def getData(self):
        layers = QgsProject.instance().mapLayers().values()
        vector_layers = []
        raster_layers = []
        
        for lyr in layers:
            if lyr.type()== 0:
                if lyr.wkbType() in (3,6):
                    vector_layers.append(lyr.name())                
            if lyr.type()== 1:
                raster_path = lyr.source()
                raster = gdal.Open(raster_path)
                if raster:
                    raster_layers.append(lyr.name())
                    raster.FlushCache()                    
        
        self.dlg.cbRaster.clear()
        self.dlg.cbRaster.addItems(raster_layers)
        
        return vector_layers, raster_layers
    
    
    def readNewRaster(self):
        self.raster.FlushCache()
        
        del self.raster
        
        new_raster_name = self.dlg.cbRaster.currentText()
        
        raster_layers = QgsProject.instance().mapLayersByName(new_raster_name)
        
        if len(raster_layers) > 0:
            self.raster = gdal.Open(raster_layers[-1].source())
            self.raster_extent = self.getRasterExtent(self.raster)
            self.zs = ZonalStatistics(self.raster)
            
            active_layer = self.iface.activeLayer()
            if active_layer.type() == 0:
                features = active_layer.selectedFeatures()
                if len(features) > 0:
                    self.dlg.lbl_warning.setText("")
                    self.getZonalStats(features, active_layer.name())
                else:
                    self.figure.clear()
                    self.ax = self.figure.add_subplot(111)
                    self.canvas.draw()
                    
                    self.dlg.lbl_warning.setText('<html><head/><body><p><span style=" color:#ff0000;"> No Feature Selected!!! </span></p></body></html>')
                    self.dlg.lbl_layerName.setText("")
                    self.dlg.lbl_numOfFeat.setText("")
        else:
            iface.messageBar().pushMessage("Error", "No available raster layer detected." , level=Qgis.Critical, duration=10)
            return
        
    def aggToggled(self):
        sender = self.dlg.sender()
        
        if sender.objectName() == "chb_cumsum":
            self.readNewRaster()
        else:        
            if sender.isChecked():
                self.readNewRaster()
    
    def getZonalStats(self, features, lyr_name):
        geoms = [feat.geometry() for feat in features]
        wkt_list = [geom.asWkt() for geom in geoms]
        
        gdal_geoms = []
        unavailable_geoms = []
        
        for wkt in wkt_list:
            geom = ogr.CreateGeometryFromWkt(wkt)
            if self.raster_extent.Contains(geom):
                gdal_geoms.append(geom)
            else:
                unavailable_geoms.append(geom)
        
        if len(unavailable_geoms) > 0:
            QMessageBox.information(None, "WARNING", f"{len(unavailable_geoms)} of selected polygons are out of raster bound.")
            
        if len(gdal_geoms) > 0:
            res_list = self.zs.run(gdal_geoms)
            
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            for e, (band_names, arrays) in enumerate(res_list):
                if self.dlg.rb_min.isChecked():
                    arrays = np.array([np.min(i[~np.isnan(i)]) for i in arrays])
                    label = "Minimum"
                
                elif self.dlg.rb_max.isChecked():
                    arrays = np.array([np.max(i[~np.isnan(i)]) for i in arrays])
                    label = "Maximum"
                
                elif self.dlg.rb_mean.isChecked():
                    arrays = np.array([np.mean(i[~np.isnan(i)]) for i in arrays])
                    label = "Mean"
                
                elif self.dlg.rb_median.isChecked():
                    arrays = np.array([np.median(i[~np.isnan(i)]) for i in arrays])
                    label = "Median"
                
                elif self.dlg.rb_std.isChecked():
                    arrays = np.array([np.std(i[~np.isnan(i)]) for i in arrays])
                    label = "Std. Dev."
                    
                
                if self.dlg.chb_cumsum.isChecked():
                    self.ax.plot(band_names, np.cumsum(arrays), marker="o", markersize=3)
                    label = f"{label} (Cumulative)"
                else:
                    self.ax.plot(band_names, arrays, marker="o", markersize=3)
             
            self.ax.set_title(label)
            band_ticks = band_names[::int(len(band_names)/15)] if len(band_names)>15 else band_names
            self.ax.set_xticks(band_ticks)
            self.ax.set_xticklabels(band_ticks, rotation=90)
            self.ax.grid(True)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.dlg.lbl_layerName.setText(lyr_name)
            self.dlg.lbl_numOfFeat.setText(str(len(gdal_geoms)))

    def run(self):
        self.dlg = StatsByPolygonDialog()
        
        if mdlChck_plt == 0:
            iface.messageBar().pushMessage("Error", "matplotlib couldn't be impported successfully! Please install manually." , level=Qgis.Critical, duration=10)
            return
        
        vector_layers, raster_layers = self.getData()
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.dlg.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        
        if len(vector_layers) == 0:
            iface.messageBar().pushMessage("Error", "No available polygon layer detected." , level=Qgis.Critical, duration=10)
            return
        
        if len(raster_layers) > 0:
            raster_name = self.dlg.cbRaster.currentText()
            raster_lyr = QgsProject.instance().mapLayersByName(raster_name)[-1]
            self.raster = gdal.Open(raster_lyr.source())
            self.zs = ZonalStatistics(self.raster)
            self.raster_extent = self.getRasterExtent(self.raster)
            
            active_layer = self.iface.activeLayer()
            if active_layer.type() == 0:
                features = active_layer.selectedFeatures()
                if len(features) > 0:
                    self.dlg.lbl_warning.setText("")
                    self.getZonalStats(features, active_layer.name())
                else:
                    self.dlg.lbl_warning.setText('<html><head/><body><p><span style=" color:#ff0000;"> No Feature Selected!!! </span></p></body></html>')
                    self.dlg.lbl_layerName.setText("")
                    self.dlg.lbl_numOfFeat.setText("")
            
        else:
            iface.messageBar().pushMessage("Error", "No available raster layer detected." , level=Qgis.Critical, duration=10)
            return
        
        self.dlg.cbRaster.currentTextChanged.connect(self.readNewRaster)
        self.dlg.rb_min.toggled.connect(self.aggToggled)
        self.dlg.rb_max.toggled.connect(self.aggToggled)
        self.dlg.rb_mean.toggled.connect(self.aggToggled)
        self.dlg.rb_median.toggled.connect(self.aggToggled)
        self.dlg.rb_std.toggled.connect(self.aggToggled)
        self.dlg.chb_cumsum.toggled.connect(self.aggToggled)
        self.dlg.btn_refresh.clicked.connect(self.readNewRaster)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass