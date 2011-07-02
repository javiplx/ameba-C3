
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
callback_name = "cobbler"

import xmlrpclib


# Take values from configuration file
cobbler_server = "http://localhost/cobbler_api"
cobbler_user = "admin"
cobbler_pass = "admin"


class CobblerAddHost ( __baseclass.AbstractRegisterCallback ) :

    name = callback_name

    def run ( self , uuid , dbvalues ) :

        conn = xmlrpclib.ServerProxy( cobbler_server )
        token = conn.login( cobbler_user , cobbler_pass )

        if conn.get_distro( dbvalues["distro"] ) == "~" :
            itemdistro = conn.new_distro( token )
            conn.modify_distro( item , "name" , dbvalues["distro"] , token )
            conn.modify_distro( item , "breed" , dbvalues["distro"] , token )
            conn.modify_distro( item , "os_version" , dbvalues["distro"] , token )
            conn.modify_distro( item , "arch" , "i386" , token )
            conn.modify_distro( item , "owners" , "amebaC3" , token )
            conn.modify_distro( item , "kernel" , "/tmp/cobbler.fake" , token )
            conn.modify_distro( item , "initrd" , "/tmp/cobbler.fake" , token )
            if not conn.save_distro( item , token ) :
                return

        if conn.get_profile( dbvalues["distro"] ) == "~" :
            itemdistro = conn.new_profile( token )
            conn.modify_profile( item , "name" , dbvalues["distro"] , token )
            conn.modify_profile( item , "profile" , dbvalues["distro"] , token )
            conn.modify_profile( item , "owners" , "amebaC3" , token )
            if not conn.save_profile( item , token ) :
                return

        item = conn.new_system( token )
        conn.modify_system( item , "name" , dbvalues["uuid"] , token )
        conn.modify_system( item , "hostname" , dbvalues["hostname"] , token )
        conn.modify_system( item , "ctime" , float(dbvalues["registration_date"]) , token )
        conn.modify_system( item , "owner" , dbvalues["registration_by"] , token )
        conn.modify_system( item , "ipaddress" , dbvalues["hostaddress"] , token )
        conn.modify_system( item , "profile" , dbvalues["distro"] , token )
        conn.save_system( item , token )

