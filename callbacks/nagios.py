
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

import time
import os

restart_allowed = True

cfg_dir = "/etc/nagios/amebaC3"
commandfile = "/var/spool/nagios/cmd/nagios.cmd"

node_template = """define host{
        use                     ameba-node
        host_name               %(hostname)s
        alias                   %(uuid)s
        address                 %(hostaddress)s
        hostgroups              %(distro)s
        }

define service{
        use                             ameba-service
        host_name                       %(hostname)s
        service_description             ameba updater
        }
"""

group_template = """define hostgroup{
        hostgroup_name  %(distro)s
        alias           %(distro)s nodes
        }
"""


class NagiosAddHost ( __baseclass.AbstractRegisterCallback ) :

    def run ( self , uuid , dbvalues ) :

        _dbvalues = { 'uuid':uuid }
        _dbvalues.update( dbvalues )

        fname = os.path.join( cfg_dir , "%s.cfg" % uuid )
        # FIXME : Exception if exists? Is truncate is enough?
        # FIXME : Permissions
        fd = open( fname , 'w' )
        fd.write( node_template % _dbvalues )
        fd.close()

        coso = []
        fname = os.path.join( cfg_dir , "%s.cfg" % _dbvalues['distro'] )
        if not os.path.exists( fname ) :
            fd = open( fname , 'w' )
            fd.write( group_template % _dbvalues )
            fd.close()

        if restart_allowed :
            fd = open( commandfile , 'a' )
            fd.write( "[%lu] RESTART_PROGRAM\n" % time.time() )
            fd.close()


class NagiosHostUpdate ( __baseclass.AbstractAliveCallback ) :

    def run ( self , sess ) :
        fd = open( commandfile , 'a' )
        fd.write( "[%lu] PROCESS_HOST_CHECK_RESULT;%s;0;Ameba C3 - Logged in\n" % ( time.time() , sess['HOSTNAME'] ) )
        fd.close()


class NagiosServiceUpdate ( __baseclass.AbstractUpdateCallback ) :

    def run( self , sess , status ) :
        fd = open( commandfile , 'a' )
        if status == "OK" :
            fd.write( "[%lu] PROCESS_SERVICE_CHECK_RESULT;%s;ameba updater;0;Ameba C3 - Up to date\n" % ( time.time() , sess['HOSTNAME'] ) )
        elif status == "WARNING" :
            fd.write( "[%lu] PROCESS_SERVICE_CHECK_RESULT;%s;ameba updater;1;Ameba C3 - Updates for packages available\n" % ( time.time() , sess['HOSTNAME'] ) )
        else :
            fd.write( "[%lu] PROCESS_SERVICE_CHECK_RESULT;%s;ameba updater;2;Ameba C3 - Failed update\n" % ( time.time() , sess['HOSTNAME'] ) )
        fd.close()

