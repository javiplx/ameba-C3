
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


def addChild ( node , tagname , value=None ) :
    doc = node.ownerDocument
    child = node.appendChild( doc.createElement( tagname ) )
    if value :
        child.appendChild( doc.createTextNode( value ) )

class DashboardCheckin ( __baseclass.AbstractRegisterCallback ) :

    name = callback_name

    def run ( self , uuid , dbvalues ) :
        macaddr = dbvalues['macaddress']
        # Create nodesfile if does not exists
        macfile = os.path.join( datadir , "data/mac2net" , "%s.txt" % base64.encodestring(macaddr)[:-1] )
        # If macfile exists, check network

        if os.path.exists( nodesfile ) :
            doc = xml.dom.minidom.parse( nodesfile )
        else :
            doc = xml.dom.minidom.parseString( '<network />' )

        for node in doc.getElementsByTagName('node') :
            if macaddr == node.getElementsByTagName('mac')[0].firstChild.nodeValue :
                print "Node %s already registered" % macaddr
        else :
            newnode = doc.createElement( 'node' )
            doc.documentElement.appendChild( newnode )
            addChild( newnode , 'name' , dbvalues['hostname'] )
            addChild( newnode , 'notes' )
            addChild( newnode , 'mac' , macaddr )
        # IP is not a param, but assigned by the dashboard checkin
            addChild( newnode , 'ip' , dbvalues['hostaddress'] )
        # location:"(lat,lon)" or lat+lon
            addChild( newnode , 'lat' )
            addChild( newnode , 'long' )
        # create macfile
            doc.writexml( open( nodesfile , 'w' ) )

