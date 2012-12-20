
from exceptions import *
from baseclass import *

import fs_backend , bdb_backend

import time
import os

import ConfigParser


configfile = "/etc/amebaC3.conf"


def get ( cfgfile=configfile ) :

    dbconfig = {
        'root': "/var/lib/amebaC3" ,
        'name': "amebaC3-fs"
        }

    config = ConfigParser.RawConfigParser( dbconfig )
    config.read( cfgfile )

    if config.has_section( 'database' ) :
        dbconfig.update( dict( config.items( 'database' ) ) )

    if not dbconfig.has_key( 'type' ) :
        raise InternalError( "No database type configured" )

    if not os.path.isdir( dbconfig['root'] ) :
        raise InternalError( "Directory %s does not exists" % dbconfig['root'] )

    #FIXME : Check for owner and permissions

    if dbconfig['type'] == "fs" :
        return fs_backend.Database( dbconfig['root'] , dbconfig['name'] )
    elif dbconfig['type'] == "bdb" :
        return bdb_backend.Database( dbconfig['root'] , dbconfig['name'] )

    raise InternalError( "Uknown database type '%s'" % dbconfig['type'] )


def initialize ( cfgfile ) :
    db = get( cfgfile )
    db.add_user ( "nagiosadmin" , { 'registration_by':'__init__' , 'password':"nagiosadmin" , 'group':"nagiosadmin" } )
    db.add_user ( "guest" , { 'registration_by':'__init__' , 'password':"*" } )


