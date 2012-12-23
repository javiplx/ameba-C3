
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


__version__ = "1.1"


import urllib , urllib2


import logging
logger = logging.getLogger()


def register ( url , data ) :

    req = urllib2.Request( "%s/register" % url , data=urllib.urlencode( data ) )
    req.add_header( "User-Agent" , "AmebaC3-Agent/%s" % __version__ )

    ret = False

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        logger.error( res.msg )
        map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )
    except urllib2.URLError , ex :
        logger.error( "%s : %s" % ( ex.reason[0] , ex.reason[1] ) )
    except Exception , ex :
        logger.error( 'Unexpected exception %s' % ex )
    else :
        firstline = res.readline().rstrip('\n')
        if firstline == "OK" :
            ret = True
            secondline = res.readline().rstrip('\n')
            if secondline :
                response = secondline.split()
                if len(response) == 2 and response[0] == "UUID" :
                    ret = response[1]
                    map( logger.warning , map( lambda x : x.rstrip('\n') , res.readlines() ) )
                else :
                    logger.error( secondline )
                    map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )
        else :
            logger.error( firstline )
            map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )

    return ret


def login ( url , uuid ) :

    req = urllib2.Request( "%s/login" % url )
    req.add_header( "User-Agent" , "AmebaC3-Agent/%s" % __version__ )
    req.add_header( "Authorization" , "UUID %s" % uuid )

    sessid , delay = None , 0

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        logger.error( res.msg )
        map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )
    except urllib2.URLError , ex :
        logger.error( "%s : %s" % ( ex.reason[0] , ex.reason[1] ) )
    except Exception , ex :
        logger.error( 'Unexpected exception %s' % ex )
    else :
        firstline = res.readline().rstrip('\n').split()
        if len(firstline) == 2 and firstline[0] == "ID" :
            sessid = firstline[1]
            delay = float( res.headers.get( 'X-AmebaDelay' , "0" ) )
        elif firstline :
            # NOTE : login warnings could appear mixed with errors on combined operations
            logger.error( " ".join(firstline) )
            map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )

    return sessid , delay


def logout ( url , sessid , failed=False ) :

    req = urllib2.Request( "%s/logoff" % url )
    req.add_header( "User-Agent" , "AmebaC3-Agent/%s" % __version__ )
    req.add_header( "Cookie" , "pysid=%s" % sessid )
    if failed is True :
        req.add_header( "X-AmebaStatus" , "FAIL" )
    elif failed :
        req.add_header( "X-AmebaStatus" , "%s" % failed )

    ret = False

    try :
        res = urllib2.urlopen( req )
    except urllib2.HTTPError , res :
        logger.error( res.msg )
        map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )
    except urllib2.URLError , ex :
        logger.error( "%s : %s" % ( ex.reason[0] , ex.reason[1] ) )
    except Exception , ex :
        logger.error( 'Unexpected exception %s' % ex )
    else :
        firstline = res.readline().rstrip('\n').split()
        if len(firstline) == 2 and firstline[0] == "ID" :
            ret = True
        else :
            logger.error( "Logout failed" )
            if firstline :
                logger.error( " ".join(firstline) )
                map( logger.error , map( lambda x : x.rstrip('\n') , res.readlines() ) )

    return ret


def loginout ( url , uuid , failed=False ) :

    sessid , delay = login( url , uuid )
    # NOTE : login warnings will appear mixed with errors from later stages

    if not sessid : 
        logger.error( "Login failed" )
        return False

    if delay : 
        logger.info( "sleeping %s secs until session gets active" % delay )
        time.sleep( delay )

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
        logger.info( "sleeping %s secs until session gets active" % delay )
        time.sleep( delay )

    ret = False

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
        ret = loginout ( url , uuid )

    return ret


