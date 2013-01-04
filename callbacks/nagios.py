
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
callback_name = "nagios"

import time
import os


config = {
    'restart_allowed': True ,
    'cfg_dir': "/etc/nagios/amebaC3" ,
    'commandfile': "/var/spool/nagios/cmd/nagios.cmd"
    }

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
        %(extra)s}

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


service_template = """define service{
        use			%(template)s
        host_name		%(hostname)s
        service_description	%(service)s
        check_command		%(command)s
        }
"""


class AbstractNagios :

    def send_command ( self , command , hostname=None , msg=None ) :
        fd = open( config['commandfile'] , 'a' )
        if hostname or msg :
            fd.write( "[%lu] %s;%s;%s\n" % ( time.time() , command , hostname , msg ) )
        else :
            fd.write( "[%lu] %s\n" % ( time.time() , command ) )
        fd.close()

    # FIXME : Permissions
    def write_conf ( self , filename , template , values , extra=None ) :
        name = os.path.join( config['cfg_dir'] , "%s.cfg" % filename )
        if extra :
            values.update( extra )
        fd = open( name , 'w' )
        fd.write( template % values )
        fd.close()


class NagiosAddHost ( __baseclass.AbstractRegisterCallback , AbstractNagios ) :

    name = callback_name

    def __init__ ( self ) :
        self.services = {}
        if config.has_key( 'services' ) :
            for service in config['services'].split() :
                serv = {}
                if config.has_key( 'service-template' ) :
                    serv['template'] = config['service-template']
                if not amebaC3_config.has_section( service ) :
                    raise Exception( "Service '%s' not present on configuration" % service )
                serv.update( dict( amebaC3_config.items(service) ) )
                self.services[service] = serv

    def run ( self , uuid , dbvalues ) :

        _dbvalues = { 'uuid':uuid ,'extra':''}
        _dbvalues.update( dbvalues )

        if dbvalues.has_key( 'metrics' ) and config.has_key( 'metrics_url' ) :
            _dbvalues['extra'] = "notes_url     %s/%s\n        " % ( config['metrics_url'] , _dbvalues['hostname'] )

        # FIXME : Exception if exists?
        self.write_conf( uuid , node_template , _dbvalues )

        self.write_conf( _dbvalues['distro'].replace("/"," ") , group_template , _dbvalues )

        if _dbvalues.get( 'services' ) :
            for service in _dbvalues['services'].split(',') :
                if not self.services.has_key(service) :
                    raise Exception( "No service '%s' known to the server" % service )
                self.services[service]['service'] = service
                self.write_conf( "%s-%s" % ( uuid , service ) , service_template , _dbvalues , self.services[service] )

        if config['restart_allowed'] :
            self.send_command( "RESTART_PROGRAM" )


class NagiosHostUpdate ( __baseclass.AbstractAliveCallback , AbstractNagios ) :

    name = callback_name

    def run ( self , sess ) :
        self.send_command( "PROCESS_HOST_CHECK_RESULT" , sess['HOSTNAME'] , "0;Ameba C3 - Logged in" )


class NagiosServiceUpdate ( __baseclass.AbstractUpdateCallback , AbstractNagios ) :

    name = callback_name

    def run( self , sess , status ) :
        if status == "OK" :
            msg = "ameba updater;0;Ameba C3 - Up to date"
        elif status == "WARNING" :
            msg = "ameba updater;1;Ameba C3 - Updates for packages available"
        else :
            msg = "ameba updater;2;Ameba C3 - Failed update"
        self.send_command( "PROCESS_SERVICE_CHECK_RESULT" , sess['HOSTNAME'] , msg )

