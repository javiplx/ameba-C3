
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


import database

from mod_python import apache
from mod_python import Session


default_session_timeout = 60


def handler ( req ) :

    if not req.subprocess_env.has_key('sessid') :
        req.log_error( "handler : session information missing in environment" , apache.APLOG_EMERG )
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        return apache.DONE

    req.content_type = "text/plain"
    req.write( "ID %s" % req.subprocess_env['sessid'] )

    return apache.OK


def authenhandler ( req ) :

    if req.headers_in.has_key( "Authorization" ) :

        try :
            type , uuid = req.headers_in["Authorization"].split(" ",1)
        except ValueError , ex :
            req.log_error( "authenhandler : Malformed Authorization header '%s'" % req.headers_in["Authorization"] )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE
        if type == "Basic" :
            db = database.get( database.dbtype )
            if not db.check_user_password( req.user , req.get_basic_auth_pw() ) :
                req.log_error( "authenhandler : Wrong password for user %s" % req.user )
                # NOTE : This is a browser response, so we can perform a hard return
                return apache.HTTP_UNAUTHORIZED

            req.log_error( "authenhandler : user '%s' from Basic Authentication" % req.user , apache.APLOG_INFO )
            if db.get_user_group( req.user ) == "nagiosadmin" :
                req.user = "nagiosadmin"
            else :
                req.user = "guest"
            db.close()
            return apache.OK
        elif type == "UUID" :
            if uuid.find(" ") != -1 :
                req.log_error( "authenhandler : Malformed Authorization UUID %s" % uuid )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            req.log_error( "authenhandler : user '%s' from headers" % uuid , apache.APLOG_INFO )
            req.user = uuid
        else :
            req.log_error( "authenhandler : Unknown Authorization type '%s'" % type )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE

    # FIXME : Implement session based authentication. Does require explicit declaration in apacheconf ?
    sess = Session.Session( req )
    if sess.is_new() :
        # Proper expiration time is not set on the cookie, even specifying at instantiation
        sess.set_timeout( default_session_timeout )
        if not req.user :
            sess.invalidate()
            req.log_error( "authenhandler : Trying to access with an obsolete session" )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE
        sess['UUID'] = req.user
        sess.save()
    else :
        if req.user :
            if req.user != sess['UUID'] :
                sess.invalidate()
                req.log_error( "authenhandler : Requested reauthentication for '%s' with session from '%s'" % ( req.user , sess['UUID'] ) )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            # FIXME : Refresh the session to increase timeout ???
            req.log_error( "authenhandler : Requested reauthentication for '%s'" % req.user , apache.APLOG_INFO )
        else :
            req.log_error( "authenhandler : Setting user '%s' from session" % sess['UUID'] , apache.APLOG_INFO )
            req.user = sess['UUID']

    # NOTE : Stopping here with DONE will not work, so we require the content handler phase
    req.subprocess_env['sessid'] = sess.id()

    req.log_error( "authenhandler : Going auth with user '%s'" % req.user , apache.APLOG_INFO )
    return apache.OK

