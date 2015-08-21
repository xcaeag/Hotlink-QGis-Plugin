# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : Hotlink plugin
Description          : Triggers actions on single click
Date                 : 24/Jun/11 
copyright            : (C) 2011 by AEAG
email                : xavier.culos@eau-adour-garonne.fr 
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
def classFactory(iface): 
  # load Hotlink class from file Hotlink
  from Hotlink import Hotlink 
  return Hotlink(iface)

