# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Wtyczka
                                 A QGIS plugin
 Pogoda dla Polski
                              -------------------
        begin                : 2015-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Aleskandra Zadka
        email                : aleksandra.zadka@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QVariant
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from wtyczka_dialog import WtyczkaDialog
import os
from qgis.gui import QgsMessageBar
import os.path
from qgis.core import QgsField,QgsCoordinateReferenceSystem,QgsFeature
from qgis.core import QgsVectorLayer,QgsPoint,QgsMapLayerRegistry,QgsGeometry
import qgis.core
import qgis.utils
import qgis.gui
import urllib
import json 
import time
from pprint import pprint 
from datetime import  datetime
from datetime import timedelta






class Wtyczka:
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
            'Wtyczka_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = WtyczkaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pogoda')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Wtyczka')
        self.toolbar.setObjectName(u'Wtyczka')

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
        return QCoreApplication.translate('Wtyczka', message)


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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Wtyczka/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Pogoda'),
            callback=self.run,
            parent=self.iface.mainWindow())
        

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogoda'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop

        
        fi=os.path.exists("D:\danee.json")
        if fi==True:
            urlreq="http://api.openweathermap.org/data/2.5/group?id=3085978,3080101,3103261,3082587,3104132,3103709,3093133,3093066,3088972,3080414,3081496,3082197,3082176,3082801,3082945,3083788,759123,7302565,3087497,3089578,3095413&units=metric"
            czasutw=os.stat("D:\danee.json").st_mtime
            print("Czas utworzenia pliku: " + time.ctime(czasutw))
            czasob=time.time()
            print("Obecny czas: " + time.ctime(czasob))
            dczas= timedelta(seconds=czasob)-timedelta(seconds=czasutw)
            if dczas >=timedelta(seconds=600):
                print( dczas)
                urllib.urlretrieve(urlreq,"D:\danee.json")
                plikpog=open("D:\danee.json","r")
                for linia in plikpog:
                    to=json.loads(linia)
            else:
                plikpog=open("D:\danee.json","r")
                for linia in plikpog:
                    to=json.loads(linia)
                    #plikpog.close()
                qgis.utils.iface.messageBar().pushMessage("Informacja","Parametry",level=QgsMessageBar.INFO,duration=10)
        else: 
            
            plikpog=urllib2.urlopen(urlreq);
            global to
            to = json.loads(plikpog.read())
            qgis.utils.iface.messageBar().pushMessage("Informacja","Plik juz istnieje",level=QgsMessageBar.INFO,duration=10)
           
        result = self.dlg.exec_()
        if result:
        # See if OK was pressed
            
            aw=to['list']
            r=int(to['cnt'])
            k=int(0)
            parametryy=[]
            longg=[]
            latt=[]
            for k in xrange(0,r,1):
                temp=to['list'][k]['main']['temp']
                tempmin=to['list'][k]['main']['temp_min']
                tempmax=to['list'][k]['main']['temp_max']
                cisnienie=to['list'][k]['main']['pressure']
                wilgotnosc=to['list'][k]['main']['humidity']
                predwiatru=to['list'][k]['wind']['speed']
                kierwiatru=to['list'][k]['wind']['deg']
                chmury=to['list'][k]['clouds']['all']
                miastoname=to['list'][k]['name']
                long=to['list'][k]['coord']['lon']
                lat=to['list'][k]['coord']['lat']
                parametry=[temp,tempmax,tempmin,cisnienie,wilgotnosc,predwiatru,kierwiatru,chmury,miastoname]
                longg.append(long)
                latt.append(lat)
                parametryy.append(parametry)
            wojew=QgsVectorLayer("C:\Users\Alex\.qgis2\python\plugins\Wtyczka\wojlodzkie.shp","lodzkie","ogr")   
            QgsMapLayerRegistry.instance().addMapLayer(wojew)
            
            pogod=QgsVectorLayer("Point", "Pogoda", "memory")
            pogod.setCrs( QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId) )
            pogod.startEditing()
            atrybuty=["TEMP","TEMP_MAX","TEMP_MIN", "PRESSURE","HUMIDITY","WIND_SPEED","WIND_ANGLE","CLOUDS","CITY_NAME"]
            for i in atrybuty:
                if pogod.dataProvider().fieldNameIndex(i)==-1:
                    pogod.dataProvider().addAttributes([QgsField(i,QVariant.Double)])
            pogod.updateFields() 
            pogod.commitChanges()
            
            QgsMapLayerRegistry.instance().addMapLayer(pogod)

            for k in xrange(0,r,1):
                wer=QgsFeature()
                wer.setGeometry(QgsGeometry.fromPoint(QgsPoint(longg[k],latt[k])))
                wer.setAttributes(parametryy[k])
                print(wer)
                pogod.startEditing()
                pogod.addFeature(wer,True)
            pogod.commitChanges()
            pogod.updateExtents()


    pass
