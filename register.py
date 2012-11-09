
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

def send_error ( req , error_msgs ) :
    req.status = apache.HTTP_BAD_REQUEST
    req.content_type = "text/plain"
    map( lambda x : req.log_error( "handler : %s" % x ) , error_msgs )
    req.write( "\n".join( error_msgs ) )
    return apache.OK

def handler ( req ) :

    # FIXME : reuse code to get unique UUID on args

    error_msg = []
    if req.args or req.method == "POST" :
        _args = util.FieldStorage(req)
        args = dict( map( lambda  x:  tuple ( ( x , _args.get(x,None) ) ) , _args.keys() ) )
        missing = []
        for required in ( 'UUID' , 'DISTRO' , 'HOSTNAME' ) :
            if not args.has_key( required ) :
                missing.append( required )
        if missing :
            return send_error( req , "%s missing" % ", ".join(missing) )
    else :
        return send_error( req , "Malformed request" )

    db = database.get( database.dbtype )
    try :
        if args['UUID'] == "__REQUEST__" :
            import uuid
            args['UUID'] = "%s" % uuid.uuid4()
            error_msg.append( "UUID %s" % args['UUID'] )
        dbvalues = db.add_node( args , req )
        db.close()
        callbacks.run_stage( "register" , req , ( args['UUID'] , dbvalues ) )
    except ImportError , ex :
        db.close()
        error_msg.append( "UUID cannot be returned" )
        req.log_error( "handler : uuid module not available to fulfill __REQUEST__ petition from %s" % args['HOSTNAME'] , apache.APLOG_CRIT )
        # NOTE : this is actually a protocol mismatch
        req.status = apache.HTTP_BAD_REQUEST 
    except database.KeyExists , ex :
        dbvalues = db.get_node( args['UUID'] )
        db.close()
        if dbvalues['hostname'] == args['HOSTNAME'] :
            # FIXME : Implement update record code
            error_msg.append( "System already registered" )
            map( lambda x : req.log_error( "handler : %s" % x , apache.APLOG_INFO ) , error_msg )
        else :
            error_msg.append( "node '%s' has UUID %s" % ( dbvalues['hostname'] , ex.message ) )
            map( lambda x : req.log_error( "handler : %s" % x ) , error_msg )
            req.status = apache.HTTP_BAD_REQUEST 
    except database.C3DBException , ex :
        db.close()
        req.log_error( "handler : Unexpected exception '%s' while adding node %s with %s" % ( ex.type , args['HOSTNAME'] , args['UUID'] ) , apache.APLOG_EMERG )
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        return apache.OK

    req.content_type = "text/plain"
    if req.status != apache.HTTP_BAD_REQUEST :
        error_msg.insert( 0 , "OK" )
    req.write( "\n".join( error_msg ) )
    return apache.OK

