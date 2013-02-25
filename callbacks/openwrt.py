
# Copyright (C) 2010 Javier Palacios
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License Version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


import __baseclass
callback_name = "openwrt"


import xml.dom.minidom
import base64
import os


datadir = "/var/www/html/dashboard"
networkname = "javiplx"


wlan_mac = "00:25:9C:CF:F7:66"
eth_mac = "00:25:9C:CF:F7:64"

nodesfile = os.path.join( datadir , "data" , "%s_nodes.xml" % networkname )
macfile = os.path.join( datadir , "data/mac2net" , "%s.txt" % base64.encodestring(wlan_mac)[:-1] )

class DashboardCheckin ( __baseclass.AbstractRegisterCallback ) :

    name = callback_name

    def run ( self , uuid , dbvalues ) :
        # Create nodesfile if does not exists
        # If macfile exists, check network
        # Else,
        # Input params :
        #  - location:"(lat,lon)" or lat+lon
        #  - name
        #  - notes
        #  - mac
        # IP is not a param, but assigned by the dashboard checkin
        # add node to nodesfile
        # create macfile

