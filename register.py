
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


import database , callbacks

from mod_python import apache , util 

import time

def handler ( req ) :

    # FIXME : reuse code to get unique UUID on args

    error_msg = None
    if req.args or req.method == "POST" :
        args = util.FieldStorage(req)
        missing = []
        for required in ( 'UUID' , 'DISTRO' , 'HOSTNAME' ) :
            if not args.has_key( required ) :
                missing.append( required )
        if missing :
            error_msg = "%s missing" % ",".join(missing)
    else :
        error_msg = "Malformed request"

    if error_msg :
        req.log_error( "handler : %s" % error_msg )
        req.status = apache.HTTP_BAD_REQUEST
        req.content_type = "text/plain"
        req.write( error_msg )
        return apache.OK

    db = database.get( database.dbtype )
    try :
        dbvalues = db.add_node( args['UUID'] , args['DISTRO'] , args['HOSTNAME'] , req )
        db.close()
        callbacks.run_stage( "register" , ( args['UUID'] , dbvalues ) )
    except database.KeyExists , ex :
        dbvalues = db.get_node( args['UUID'] )
        db.close()
        if dbvalues['hostname'] == args['HOSTNAME'] :
            # FIXME : Implement update record code
            error_msg = "System already registered"
            req.log_error( "handler : %s" % error_msg , apache.APLOG_INFO )
        else :
            error_msg = "node '%s' has UUID %s" % ( dbvalues['hostname'] , ex.message )
            req.log_error( "handler : %s" % error_msg )
            req.status = apache.HTTP_BAD_REQUEST 
    except database.C3DBException , ex :
        db.close()
        req.log_error( "handler : Unexpected exception '%s' while adding node %s with %s" % ( ex.type , args['HOSTNAME'] , args['UUID'] ) , apache.APLOG_EMERG )
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        return apache.OK

    req.content_type = "text/plain"
    if req.status != apache.HTTP_BAD_REQUEST :
        req.write( "OK" )
    if error_msg :
        req.write( error_msg )
    return apache.OK

