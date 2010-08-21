
from exceptions import *
from baseclass import *

import fs_backend , bdb_backend

import time
import os


import ConfigParser

configfile = "/etc/amebaC3.conf"

config = ConfigParser.RawConfigParser()
config.read( configfile )

dbroot = "/var/lib/amebaC3"
dbname = "ameba"
dbtype = "fs"

if config.has_option( 'database' , 'dbroot' ) :
    dbroot = config.get( 'database' , 'dbroot' )
if config.has_option( 'database' , 'dbname' ) :
    dbname = config.get( 'database' , 'dbname' )
if config.has_option( 'database' , 'type' ) :
    type = config.get( 'database' , 'type' )


def get ( type ) :

    if not os.path.isdir( dbroot ) :
        raise InternalError( "Directory %s does not exists" % dbroot )

    #FIXME : Check for owner and permissions

    if type == "fs" :
        return fs_backend.Database( dbroot , dbname )
    elif type == "bdb" :
        return bdb_backend.Database( dbroot , dbname )

    raise InternalError( "Uknown database type '%s'" % type )


def initialize ( db ) :

    db.add_user ( "nagiosadmin" , { 'registration_by':'__init__' , 'password':"nagiosadmin" , 'group':"nagiosadmin" } )
    db.add_user ( "guest" , { 'registration_by':'__init__' , 'password':"*" } )


