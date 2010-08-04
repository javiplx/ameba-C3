
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


def authenhandler ( req ) :

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

