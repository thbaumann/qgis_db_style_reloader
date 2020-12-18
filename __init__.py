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
#---------------------------------------------------------------------

from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon
from qgis.PyQt.QtXml import QDomDocument
from qgis.gui import QgsMessageBar
from qgis.core import Qgis, QgsProject
import os

def classFactory(iface):
    return DatabaseStyleLoader(iface)


class DatabaseStyleLoader:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.action =  QAction(QIcon(os.path.join(self.plugin_dir,"icon.svg")),"Style Reloader", self.iface.mainWindow())
        self.action.triggered.connect(self.load_style)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def load_style(self):
        layers = QgsProject.instance().mapLayers()

        try:
            for layer_id, layer in layers.items():
                if layer.dataProvider().name()=='postgres':
                    listedStyles = layer.listStylesInDatabase()
                    numberOfStyles = listedStyles[0]
                    defaultStyleId = listedStyles[1][0]
                    defaultStyleName = listedStyles[2][0]
                    # print(defaultStyleName)
                    # defaultStyleDate = listedStyles[3][0]
                    if numberOfStyles > 0:
                        styledoc = QDomDocument()
                        styleTuple = layer.getStyleFromDatabase(defaultStyleId)
                        styleqml = styleTuple[0]
                        styledoc.setContent(styleqml)
                        #print(styledoc.toString())
                        layer.importNamedStyle(styledoc)
                        layer.triggerRepaint()
                    
            msg=u"Stile neu geladen."
            self.showMessage(msg, Qgis.Success)
            
        except Exception as e:
            msg=u"Es ist ein Fehler aufgetreten: "+str(e)
            self.showMessage(msg, Qgis.Critical)
        


    #schicke generische showMessage Funktion von geotux (gacarrillor)
    def showMessage(self, message, level=Qgis.Info, target=None, shortmessage=None):
            """

            :param message:
            :param level:
            :param target:
            """
            if target is None:
                target = self.iface
                target.messageBar().pushMessage(message, level, self.iface.messageTimeout())
            else:
                if shortmessage is not None:
                    target.bar.pushMessage("Info", shortmessage, level=level)
                self.iface.messageBar().pushMessage(message, level, self.iface.messageTimeout())