
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


__version__ = 1.0


import urllib , urllib2


import logging
logger = logging.getLogger()


def register ( url , data ) :

    ret = False

    try :
        res = urllib2.urlopen( "%s/register" % url , urllib.urlencode( data ) )
    except urllib2.HTTPError , res :
        logger.error( res.msg )
        map( logger.error , res.readlines() )
    else :
        firstline = res.readline().splitlines()[0]
        if firstline == "OK" :
            ret = True
            secondline = res.readline().splitlines()[0]
            if secondline :
                response = secondline.split()
                if response[0] == "UUID" and len(response) == 2 :
                    ret = response[1]
                else :
                    logger.error( secondline )
                map( logger.warning , res.readlines() )
        else :
            logger.error( firstline )
            map( logger.error , res.readlines() )

    return ret


def login ( url , uuid ) :

    req = urllib2.Request( "%s/login" % url )
    req.add_header( "Authorization" , "UUID %s" % uuid )

    sessid , delay = None , 0

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        logger.error( res.msg )
        map( logger.error , res.readlines() )
    else :
        firstline = res.readline().splitlines()[0].split()
        if firstline and firstline[0] == "ID" and len(firstline) == 2 :
            sessid = firstline[1]
            delay = float( res.headers.get( 'X-AmebaDelay' , "0" ) )
        else :
            # NOTE : login warnings could appear mixed with errors on combined operations
            if firstline :
                logger.error( firstline )
                map( logger.error , res.readlines() )

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
        logger.error( res.msg )
        map( logger.error , res.readlines() )
    else :
        firstline = res.readline().splitlines()[0].split()
        if firstline and firstline[0] == "ID" and len(firstline) == 2 :
            return True
        logger.error( "Logout failed" )
        if firstline :
            logger.error( firstline )
            map( logger.error , res.readlines() )

    return False


def loginout ( url , uuid , failed=False ) :

    sessid , delay = login( url , uuid )
    # NOTE : login warnings will appear mixed with errors from later stages

    if not sessid : 
        logger.error( "Login failed" )
        return False

    return logout ( url , sessid , failed )


import subprocess
import time

def pull ( url , uuid , cmds , avail_pkgs_retcode ) :

    # NOTE : This initial login serves just to check server availability
    sessid , delay = login( url , uuid )

    if not sessid : 
        logger.error( "Login failed" )
        return False

    if delay : 
        # NOTE : this message will be reported along subsequent errors
        logger.warning( "sleping %s secs until session gets active" % delay )
        time.sleep( delay )

    # NOTE : As we are using external updaters, we need to use loginout instead of logout to end session
    for _cmdline in cmds :
        cmdline = _cmdline.strip()
        null = open( "/dev/null" , 'a' )
        if cmdline.count('|') == 1 :
            cmdline0 , cmdline1 = cmdline.split('|',1)
            command0 = subprocess.Popen( cmdline0.strip(' !').split() , stdout=subprocess.PIPE , stderr=null )
            command = subprocess.Popen( cmdline1.strip(' !').split() , stdin=command0.stdout , stdout=null , stderr=subprocess.STDOUT )
        else :
            command = subprocess.Popen( cmdline.strip(' !').split() , stdout=null , stderr=subprocess.STDOUT )
        null.close()
        command.wait()
        if cmdline.startswith('!') :
          if command.returncode == 0 :
            logger.error( "outdate at %s" % cmdline )
            loginout ( url , uuid , "WARNING" )
            break
        else :
          if command.returncode != 0 :
            if avail_pkgs_retcode == command.returncode :
                logger.error( "outdate at %s" % cmdline )
                loginout ( url , uuid , "WARNING" )
            else :
                logger.error( "failed at %s" % cmdline )
                loginout ( url , uuid , True )
            break
    else :
        # NOTE : If loginout fails here, we get an updated system failed telling to AmebaC3.
        # NOTE :     Do we actually want to return this as error?
        return loginout ( url , uuid )

    return False


