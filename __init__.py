# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DB Style Reloader
                                 A QGIS plugin
Load default styles which are saved in the postgresql DB
#-----------------------------------------------------------
# Copyright (C) 2020 Thomas Baumann
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# loading by Fahmihorizon from the Noun Project
# palette by Markus from the Noun Project
# Grundidee des Reloadens: https://gis.stackexchange.com/a/371589/67477 
#---------------------------------------------------------------------"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DatabaseStyleLoader class from file db_style_reloader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .db_style_reloader import DatabaseStyleLoader
    return DatabaseStyleLoader(iface)
