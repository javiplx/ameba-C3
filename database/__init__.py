
from exceptions import *
import fs_backend , bdb_backend

import os


# FIXME : Replace hardcoded values with variables from a .ini file
dbroot = "/var/lib/amebaC3"
dbname = "ameba"
dbtype = "fs"


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


