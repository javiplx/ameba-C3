
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


import amebaC3_database as database

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
            db = database.get( database.dbtype )
            node = db.get_node( uuid )
            db.close()
            if not node :
                req.log_error( "authenhandler : Node '%s' is not registered" % uuid )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            req.log_error( "authenhandler : user '%s' from UUID Authentication" % uuid , apache.APLOG_INFO )
            req.user = uuid
        else :
            req.log_error( "authenhandler : Unknown Authorization type '%s'" % type )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE


    sess = Session.Session( req )
    if sess.is_new() :
        if not req.user :
            sess.invalidate()
            cookies = Cookie.get_cookies( req )
            if cookies.get( "pysid" ) :
                req.log_error( "authenhandler : Trying to access with an obsolete session %s" % cookies["pysid"] )
            req.status = apache.HTTP_UNAUTHORIZED
            return apache.DONE
        # NOTE : proper expiration time is not set on the cookie
        sess.set_timeout( default_session_timeout )
        sess['UUID'] = req.user
        sess['HOSTNAME'] = node['hostname']
        sess['DISTRO'] = node['distro']
        sess['CHANNELS'] = node.get( "channels" , "*" )
        sess.save()
        cb = callbacks.nagios.NagiosHostUpdate()
        cb.run( sess )
    else :
        if req.user :
            if req.user != sess['UUID'] :
                sess.invalidate()
                req.log_error( "authenhandler : Requested reauthentication for '%s' with session from '%s'" % ( req.user , sess['UUID'] ) )
                req.status = apache.HTTP_UNAUTHORIZED
                return apache.DONE
            req.log_error( "authenhandler : Requested reauthentication for '%s'" % req.user , apache.APLOG_INFO )
            sess.save()
            nagios.nodealive( sess )
        else :
            if req.path_info == "/logoff" :
                cb = callbacks.nagios.NagiosServiceUpdate()
                cb.run( sess , req.headers_in.get( "X-AmebaStatus" , "OK" ) )
                req.log_error( "authenhandler : user '%s' ended session %s" % ( sess['UUID'] , sess.id() ) , apache.APLOG_INFO )
                req.user = sess['UUID']
                req.subprocess_env['sessid'] = sess.id()
                sess.invalidate()
                return apache.OK
            req.log_error( "authenhandler : user '%s' from session" % sess['UUID'] , apache.APLOG_INFO )
            if allow_session_refresh :
                sess.save()
            req.user = sess['UUID']

    # NOTE : Stopping here with DONE will not work, so we require the content handler phase for login requests
    req.subprocess_env['sessid'] = sess.id()

    return apache.OK

def authzhandler ( req ) :

    db = database.get( database.dbtype )
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

