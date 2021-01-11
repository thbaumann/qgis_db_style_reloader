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

from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QSettings, QLocale, QTranslator, QCoreApplication
from qgis.PyQt.QtXml import QDomDocument
from qgis.gui import QgsMessageBar

import os

def classFactory(iface):
    return DatabaseStyleLoader(iface)


class DatabaseStyleLoader:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        qgis_locale_id = str(QSettings().value('locale/userLocale'))
        qgis_locale = QLocale(qgis_locale_id)
        locale_path = os.path.join(self.plugin_dir, 'i18n')
        self.translator = QTranslator()
        self.translator.load(qgis_locale, 'db_style_reloader', '_', locale_path)
        QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DatabaseStyleLoader', message)

    def initGui(self):
        self.action =  QAction(QIcon(os.path.join(self.plugin_dir,"icon.svg")),"Style Reloader", self.iface.mainWindow())
        self.action.triggered.connect(self.load_style)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def load_style(self):
        layers = QgsProject.instance().mapLayers()

        try:
            layer_with_db_styles=0
            updateable_layer_styles={}

            for layer_id, layer in layers.items():
                if layer.dataProvider().name()=='postgres':
                    listedStyles = layer.listStylesInDatabase()
                    #print(listedStyles)
                    numberOfStyles = listedStyles[0]
                    if numberOfStyles<1:
                        pass
                    else:
                        layer_with_db_styles+=1
                        defaultStyleId = listedStyles[1][0]
                        defaultStyleName = listedStyles[2][0]
                        # defaultStyleDate = listedStyles[3][0]
                        styledoc = QDomDocument()
                        styleTuple = layer.getStyleFromDatabase(defaultStyleId)
                        styleqml = styleTuple[0]
                        styledoc.setContent(styleqml)
                        updateable_layer_styles[layer]=styledoc
                        #layer.importNamedStyle(styledoc)
                        #layer.triggerRepaint()
            



            if layer_with_db_styles>0:
                number_updateble_layers=str(layer_with_db_styles)
                if layer_with_db_styles<2:
                    question_string=self.tr(u"Do you want to update {} layerstyle?\n" \
                 "The current layerstyles of the project will be overwritten!\n" \
                 "Consider saving the project before you proceed.")
                else:
                    question_string=self.tr(u"Do you want to update {} layerstyles?\n" \
                 "The current layerstyles of the project will be overwritten!\n" \
                 "Consider saving the project before you proceed.")

                qmb_question=question_string.format(number_updateble_layers)
                reply = QMessageBox.question(self.iface.mainWindow(), self.tr('Proceed?'), qmb_question, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    for layer, styledoc in updateable_layer_styles.items():
                        # we also could check if the style is still up to date but at the moment QGIS writes different XML when writing to DB or export with "exportNamedStyle"
                        # d = QDomDocument()
                        # layer.exportNamedStyle(d)
                        # s = d.toString()
                        # if s==styledoc.toString():
                        #     print(layer.name()+" Stil weiter aktuell!")

                        layer.importNamedStyle(styledoc)
                        layer.triggerRepaint()

                    if layer_with_db_styles<2:
                        msg=number_updateble_layers+self.tr(u" style reloaded.")
                    else:
                        msg=number_updateble_layers+self.tr(u" styles reloaded.")
                    self.showMessage(msg, Qgis.Success)
                else:
                    msg=self.tr(u"No styles reloaded.")
                    self.showMessage(msg, Qgis.Info)



            else:
                msg=self.tr(u"No stiles available in the database for reloading.")
                self.showMessage(msg, Qgis.Warning)
            
        except Exception as e:
            msg=self.tr(u"An Error occured: ")+str(e)
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