
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


version = 1.0


import urllib , urllib2

import subprocess
import time


errmsg = []

def has_errmsg () :
    if errmsg :
        return True
    return False

def get_errmsg () :
    return errmsg.pop(0)

def get_all_errmsg () :
    msgs = []
    while has_errmsg() :
        msgs.append( get_errmsg() )
    return msgs



def register ( url , data ) :

    try :
        res = urllib2.urlopen( "%s/register" % url , urllib.urlencode( data ) )
    except urllib2.HTTPError , res :
        errmsg.append( res.msg )
        errmsg.extend( res.readlines() )
    else :
        firstline = res.readline()
        if firstline != "OK" :
            errmsg.append( firstline )
            errmsg.extend( res.readlines() )
        return True

    return False


def login ( url , uuid ) :

    req = urllib2.Request( "%s/login" % url )
    req.add_header( "Authorization" , "UUID %s" % uuid )

    sessid , delay = None , 0

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        errmsg.append( res.msg )
        errmsg.extend( res.readlines() )
    else :
        firstline = res.readline().split()
        if firstline[0] == "ID" and len(firstline) == 2 :
            sessid = firstline[1]
            delay = float( res.headers.get( 'X-AmebaDelay' , "0" ) )
        else :
            # NOTE : login warnings could appear mixed with errors on combined operations
            errmsg.append( firstline )
            errmsg.append( res.readlines() )

    return sessid , delay


def logout ( url , sessid , failed=False ) :

    req = urllib2.Request( "%s/logoff" % url )
    req.add_header( "Cookie" , "pysid=%s" % sessid )
    if failed is True :
        req.add_header( "X-AmebaStatus" , "FAIL" )
    elif failed :
        req.add_header( "X-AmebaStatus" , "%s" % failed )

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        errmsg.append( res.msg )
        errmsg.extend( res.readlines() )
    else :
        firstline = res.readline().split()
        if firstline[0] != "ID" or len(firstline) != 2 :
            errmsg.append( firstline )
            errmsg.extend( res.readlines() )
        return True

    return False


def pull ( url , uuid , cmds , avail_pkgs_retcode ) :

    sessid , delay = login( url , uuid )

    if not sessid : 
        errmsg.append( "Login failed" )
        return False

    if delay : 
        # NOTE : this message will be reported along subsequent errors
        errmsg.append( "sleping %s secs until session gets active" % delay )
        time.sleep( delay )

    # NOTE : As we are using external updaters, we need to use loginout instead of logout to end session
    for cmdline in cmds :
        null = open( "/dev/null" , 'a' )
        command = subprocess.Popen( cmdline.strip('!').strip().split() , stdout=null , stderr=subprocess.STDOUT )
        null.close()
        command.wait()
        if cmdline.startswith('!') :
          if command.returncode == 0 :
            errmsg.append( "outdate at %s" % cmdline.strip() )
            loginout ( url , uuid , "WARNING" )
            break
        else :
          if command.returncode != 0 :
            if avail_pkgs_retcode == command.returncode :
                errmsg.append( "outdate at %s" % cmdline.strip() )
                loginout ( url , uuid , "WARNING" )
            else :
                errmsg.append( "failed at %s" % cmdline.strip() )
                loginout ( url , uuid , True )
            break
    else :
        # NOTE : If loginout fails here, we get an updated system failed telling to AmebaC3.
        # NOTE :     Do we actually want to return this as error?
        return loginout ( url , uuid )

    return False


def loginout ( url , uuid , failed=False ) :

    sessid , delay = login( url , uuid )

    if not sessid : 
        errmsg.append( "Login failed" )
        return False

    return logout ( url , sessid , failed )


