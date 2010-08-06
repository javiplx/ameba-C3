#!/usr/bin/python

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

import sys

dbtypes = sys.argv[1:]
if not dbtypes :
    dbtypes = ( "fs" , "bdb" )

database.dbroot = "/tmp/amebaC3-tmp"

for type in dbtypes :
    try :
        db = database.get( type )
        if db.add_user ( "admin" , { 'password':"admin" , 'group':"admin" , 'registration_by':'__init__' } ) :
            print "Added admin"
        if db.add_user ( "nagiosadmin" , { 'password':"nagiosadmin" , 'group':"admin" , 'registration_by':'__init__' } ) :
            print "Added nagiosadmin"
        if db.add_user ( "user0" , { 'registration_by':'__init__' } ) :
            print "Added user0"
        try :
            if db.add_user ( "user0" ) :
                print "Added user0"
        except database.KeyExists , ex :
            print "Expected failure when adding user0 : %s - %s" % ( ex.__class__ , ex.message )

        print "Check user admin",db.check_user_password( "admin" , "admin" )
        print "Check user user0",db.check_user_password( "user0" , None )
        print "Check user nagiosadmin",db.check_user_password( "nagiosadmin" , None )
        print "    with password",db.check_user_password( "nagiosadmin" , "nagiosadmin" )

        print "Groups for admin",db.get_user_group( "admin" )
        print "Groups for user0",db.get_user_group( "user0" )
        print "Groups for nagiosadmin",db.get_user_group( "nagiosadmin" )

        db.close()

    except database.C3DBException , ex :
        print "Ameba DB Exception: %s" % ex.message
    except Exception , ex :
        print "Exception : %s" % ex

