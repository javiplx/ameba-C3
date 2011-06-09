
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

# Take values also from configuration file
cfg_dir = "/etc/nagios/amebaC3"
commandfile = "/var/spool/nagios/cmd/nagios.cmd"

node_template = """define host{
        use                     ameba-node
        host_name               %(hostname)s
        alias                   %(hostname)s
        address                 %(hostaddress)s
        hostgroups              %(distro)s
        }

define hostextinfo{
        host_name     %(hostname)s
        notes         %(uuid)s
        }

define service{
        use                             ameba-service
        host_name                       %(hostname)s
        service_description             ameba updater
;       servicegroups                   servicegroup_names
        }
"""

group_template = """define hostgroup{
        hostgroup_name  %(distro)s
        alias           %(distro)s nodes
        }
"""


services_list = {}
services_list['ping'] = { 'template':"local-service" , 'check_command':"check_ping!100.0,20%!500.0,60%" }
services_list['webserver'] = { 'template':"local-service" , 'check_command':"check_http" }

service_template = """define service{
        use			%(template)s
        host_name		%(hostname)s
        service_description	%(service)s
        check_command		%(check_command)s
        }
"""


def send_command ( command , hostname=None , msg=None ) :
    fd = open( commandfile , 'a' )
    if hostname or msg :
        fd.write( "[%lu] %s;%s;%s\n" % ( time.time() , command , hostname , msg ) )
    else :
        fd.write( "[%lu] %s\n" % ( time.time() , command ) )
    fd.close()

# FIXME : Permissions
def write_conf ( filename , template , values , extra=None ) :
    name = os.path.join( cfg_dir , "%s.cfg" % filename )
    if extra :
        values.update( extra )
    fd = open( name , 'w' )
    fd.write( template % values )
    fd.close()


class NagiosAddHost ( __baseclass.AbstractRegisterCallback ) :

    def run ( self , uuid , dbvalues ) :

        _dbvalues = { 'uuid':uuid }
        _dbvalues.update( dbvalues )

        # FIXME : Exception if exists?
        write_conf( uuid , node_template , _dbvalues )

        write_conf( _dbvalues['distro'].replace("/"," ") , group_template , _dbvalues )

        if _dbvalues.get( 'services' ) :
            for service in _dbvalues['services'].split(',') :
                services_list[service]['service'] = service
                write_conf( "%s-%s" % ( uuid , service ) , service_template , _dbvalues , services_list[service] )

        if restart_allowed :
            send_command( "RESTART_PROGRAM" )


class NagiosHostUpdate ( __baseclass.AbstractAliveCallback ) :

    def run ( self , sess ) :
        send_command( "PROCESS_HOST_CHECK_RESULT" , sess['HOSTNAME'] , "0;Ameba C3 - Logged in" )


class NagiosServiceUpdate ( __baseclass.AbstractUpdateCallback ) :

    def run( self , sess , status ) :
        if status == "OK" :
            msg = "ameba updater;0;Ameba C3 - Up to date"
        elif status == "WARNING" :
            msg = "ameba updater;1;Ameba C3 - Updates for packages available"
        else :
            msg = "ameba updater;2;Ameba C3 - Failed update"
        send_command( "PROCESS_SERVICE_CHECK_RESULT" , sess['HOSTNAME'] , msg )

