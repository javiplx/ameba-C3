
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
import callbacks

from mod_python import apache
from mod_python import Session , Cookie

import os


# Set the timeout in seconds for the login sessions
default_session_timeout = 60

# Allow sessions to be refreshed on every connection. Default is to refresh only when Authentication headers are included
allow_session_refresh = False

# Match any channel if '*' or undefined. Empty channel list disables access
allow_wildcard_channel = True


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
        # If authorization is sent either req.user is set or an error response is produced

        try :
            type , uuid = req.headers_in["Authorization"].split(" ",1)
        except ValueError , ex :
            req.log_error( "authenhandler : Malformed Authorization header '%s'" % req.headers_in["Authorization"] )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE

        # NOTE : nagios http configuration will not go through response handler
        if type == "Basic" :
            db = database.get()
            if not db.check_user_password( req.user , req.get_basic_auth_pw() ) :
                db.close()
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
                req.log_error( "authenhandler : Malformed Authorization UUID '%s'" % uuid )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE

            req.user = uuid
            db = database.get()
            node = db.get_node( uuid )
            db.close()
            if not node :
                req.log_error( "authenhandler : Node '%s' is not registered" % uuid )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            req.log_error( "authenhandler : user '%s' from UUID Authentication" % uuid , apache.APLOG_INFO )

        else :
            req.log_error( "authenhandler : Unknown Authorization type '%s'" % type )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE


    run_update = False
    if req.path_info == "/logoff" :
        run_update = True
    elif os.path.split( req.parsed_uri[apache.URI_PATH] )[1] == "logoff" :
        run_update = True

    sess = Session.Session( req )
    req.subprocess_env['sessid'] = sess.id()
    if sess.is_new() :
        if req.user :
            # NOTE : proper expiration time is not set on the cookie
            sess.set_timeout( default_session_timeout )
            sess['UUID'] = req.user
            sess['HOSTNAME'] = node['hostname']
            sess['DISTRO'] = node['distro']
            sess['CHANNELS'] = node.get( "channels" , "*" )
            sess.save()
            callbacks.run_stage( "alive" , req , ( sess ,) )
        else :
            sess.invalidate()
            cookies = Cookie.get_cookies( req )
            if cookies.get( "pysid" ) :
                req.log_error( "authenhandler : Trying to access with an obsolete session %s" % cookies["pysid"] )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE
    else :
        if req.user :
            # A double authentication (header + session) is attempted
            if req.user != sess['UUID'] :
                sess.invalidate()
                req.log_error( "authenhandler : Requested reauthentication for '%s' with session from '%s'" % ( req.user , sess['UUID'] ) )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            req.log_error( "authenhandler : Requested reauthentication for '%s'" % req.user , apache.APLOG_INFO )
            sess.save()
            nagios.nodealive( sess )
        else :
            req.user = sess['UUID']
            if run_update :
                callbacks.run_stage( "update" , req , ( sess , req.headers_in.get( "X-AmebaStatus" , "OK" ) ) )
                sess.invalidate()
                req.log_error( "authenhandler : user '%s' ended session %s" % ( req.user , req.subprocess_env['sessid'] ) , apache.APLOG_INFO )
            else :
                req.log_error( "authenhandler : user '%s' from session" % req.user , apache.APLOG_INFO )
                if allow_session_refresh :
                    sess.save()

    # NOTE : we should search and remove any other existing session for this uuid

    # NOTE : Stopping here with DONE will not work, so we require the content handler phase for login requests

    return apache.OK

# NOTE : Untested !!!
def authzhandler ( req ) :

    # FIXME : use a serialezed node on apache notes instead of reopening the database
    db = database.get()
    node = db.get_node( req.user )
    db.close()

    if not node :
        req.log_error( "authzhandler : stored session for nonexisting node %s" % req.user , apache.APLOG_EMERG )
        sess = Session.Session( req )
        sess.invalidate()
        req.status = apache.HTTP_INTERNAL_SERVER_ERROR
        return apache.DONE

    if allow_wildcard_channel and node.get('channels',"*") == "*" :
        req.log_error( "authzhandler : granted wildcard for user '%s'" % req.user , apache.APLOG_INFO )
        return apache.OK

    path , fname = os.path.split( req.uri )
    channel = os.path.basename( path )
    if channel in node.get('channels').split() :
        req.log_error( "authzhandler : granted access to '%s' from %s for user '%s'" % ( channel , node.get('channels') , req.user ) , apache.APLOG_INFO )
        return apache.OK

    req.log_error( "authzhandler : channel %s not authorized for %s" % ( channel , req.user ) )
    return apache.HTTP_UNAUTHORIZED

