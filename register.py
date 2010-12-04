
import database
import callbacks

from mod_python import apache
from mod_python import util

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
    except database.KeyExists , ex :
        dbvalues = db.get_node( args['UUID'] )
        db.close()
        if dbvalues['hostname'] == args['HOSTNAME'] :
            # FIXME : Implement update record code
            msg = "OK\nSystem already registered"
            req.log_error( "handler : %s" % msg , apache.APLOG_INFO )
        else :
            msg = "node '%s' has UUID %s" % ( dbvalues['hostname'] , ex.message )
            req.log_error( "handler : %s" % msg )
            req.status = apache.HTTP_BAD_REQUEST 
        req.content_type = "text/plain"
        req.write( msg )
        return apache.OK
    except database.C3DBException , ex :
        req.log_error( "handler : Unexpected exception '%s' while adding node %s with %s" % ( ex.type , args['HOSTNAME'] , args['UUID'] ) , apache.APLOG_EMERG )
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        return apache.OK

    callbacks.run_stage( "register" , ( args['UUID'] , dbvalues ) )

    req.content_type = "text/plain"
    req.write( "OK" )
    return apache.OK

