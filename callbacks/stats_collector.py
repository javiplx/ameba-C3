
# Copyright (C) 2011 Javier Palacios
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License Version 2
# as published by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


import __baseclass
callback_name = "stats-collector"

from rrdutils import confdir , getHosts
import os , sys
import re

def getConf ( conf , mode='r') :
    if conf.find(".") != -1 :
        conf , tag = conf.split(".",1)
    else :
       tag = ""
    filename = os.path.join( confdir , conf )
    if not os.path.isfile( filename ) :
        return False , None
    return tag , open( filename , mode )


class StatsCollectorAddHost ( __baseclass.AbstractRegisterCallback ) :

    name = callback_name

    def run ( self , uuid , dbvalues ) :

        if not dbvalues.has_key( 'metrics' ) :
            return

        hostname = dbvalues["hostname"]

        # FIXME : add errors to continues
        for metric in dbvalues['metrics'].split(',') :
            host_list = getHosts( metric )
            if not host_list or hostname in host_list :
                continue
            outlines =  []
            unprocessed = True
            insertline , last_host = 0 , 0
            tagname , cfg = getConf( metric , 'r+' )
            if tagname is False :
                continue
            line = cfg.readline()
            while line :
                if not insertline and ( line.startswith("P") or line.startswith("DefGraph") ) :
                    insertline = len(outlines)
                outlines.append( line )
                # FIXME : this will produce lengthy files, some more intelligent reorganization is required
                if line.startswith("H") :
                  last_host = len(outlines)
                match = re.match( "H%s\s+" % tagname , line )
                if match and unprocessed :
                    outlines.append( "H%s %s\n" % ( tagname , hostname ) )
                    unprocessed = False
                line = cfg.readline()
            # We must care about rare cases where this is the first host ??
            if unprocessed :
              if last_host :
                # FIXME : this could fail when conf ends with a host definition
                outlines.insert( last_host , "H%s %s\n\n" % ( tagname , hostname ) )
              else :
                # FIXME : this way to insert point might (unlikely) not handle empty files
                outlines.insert( insertline , "H%s %s\n\n" % ( tagname , hostname ) )
            cfg.seek(0)
            for line in outlines :
                cfg.write( line )
            cfg.close()
            os.system( "RRDcreator %s %s" % ( metric , hostname ) )

