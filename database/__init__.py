
from exceptions import *
from baseclass import *

import fs_backend , bdb_backend

import time
import os


import ConfigParser

configfile = "/etc/amebaC3.conf"

dbvalues = {
    'dbroot': "/var/lib/amebaC3" ,
    'dbname': "amebaC3-fs" ,
    'dbtype': "fs"
    }

config = ConfigParser.RawConfigParser( dbvalues )
config.read( configfile )

if config.has_section( 'database' ) :
    dbvalues = dict( config.items( 'database' ) )


def get ( _type ) :

    if not os.path.isdir( dbvalues['dbroot'] ) :
        raise InternalError( "Directory %s does not exists" % dbroot )

    #FIXME : Check for owner and permissions

    if _type == "fs" :
        return fs_backend.Database( dbvalues['dbroot'] , dbvalues['dbname'] )
    elif _type == "bdb" :
        return bdb_backend.Database( dbvalues['dbroot'] , dbvalues['dbname'] )

    raise InternalError( "Uknown database type '%s'" % _type )


def initialize ( db ) :

    db.add_user ( "nagiosadmin" , { 'registration_by':'__init__' , 'password':"nagiosadmin" , 'group':"nagiosadmin" } )
    db.add_user ( "guest" , { 'registration_by':'__init__' , 'password':"*" } )


