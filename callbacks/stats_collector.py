
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

import os , sys

# Take values from configuration file
rootdir = "/var/lib/rrd"
confdir = os.path.join( rootdir , "conf" )


def getConf ( conf , mode='r') :
    lead = "H"
    if conf.find(".") != -1 :
        conf , tag = conf.split(".",1)
        lead += tag
    filename = os.path.join( confdir , conf )
    if not os.path.isfile( filename ) :
        return None , "%s " % lead
    return open( filename , mode ) , "%s " % lead

def getHosts ( conf ) :
    cfg , lead = getConf( conf )
    if cfg is None :
        return None
    hosts = []
    line = cfg.readline()
    while line :
        if line.startswith(lead) :
            hosts.extend( line[len(lead):].split() )
        line = cfg.readline()
    cfg.close()
    return hosts


class StatsCollectorAddHost ( __baseclass.AbstractRegisterCallback ) :

    def run ( self , uuid , dbvalues ) :

        if not dbvalues.has_key( 'metrics' ) :
            return

        hostname = dbvalues["hostname"]

        for metric in dbvalues['metrics'].split(',') :
            host_list = getHosts( metric )
            if host_list is None or hostname in host_list :
                continue
            outlines =  []
            unprocessed = True
            insertline , last_host = 0 , 0
            cfg , lead = getConf( metric , 'r+' )
            line = cfg.readline()
            while line :
                if not insertline and ( line.startswith("P") or line.startswith("DefGraph") ) :
                    insertline = len(outlines)
                outlines.append( line )
                # FIXME : this will produce lengthy files, some more intelligent reorganization is required
                if line.startswith("H") :
                  last_host = len(outlines)
                if line.startswith(lead) and unprocessed :
                    outlines.append( "%s%s\n" % ( lead , hostname ) )
                    unprocessed = False
                line = cfg.readline()
            # We must care about rare cases where this is the first host ??
            if unprocessed :
              if last_host :
                # FIXME : this could fail when conf ends with a host definition
                outlines.insert( last_host , "%s%s\n\n" % ( lead , hostname ) )
              else :
                # FIXME : this way to insert point might (unlikely) not handle empty files
                outlines.insert( insertline , "%s%s\n\n" % ( lead , hostname ) )
            cfg.seek(0)
            for line in outlines :
                cfg.write( line )
            cfg.close()

