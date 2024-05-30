# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StatsByPolygon
                                 A QGIS plugin
 This plugin creates statistics for raster bands based on selected polygon feature.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-05-20
        copyright            : (C) 2024 by Murat Çalışkan
        email                : caliskan.murat.20@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load StatsByPolygon class from file StatsByPolygon.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .stats_by_polygon import StatsByPolygon
    return StatsByPolygon(iface)