
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

from yum.plugins import TYPE_CORE

requires_api_version = '2.5'
plugin_type = (TYPE_CORE,)

import ConfigParser
import urllib2

config = ConfigParser.RawConfigParser()

def init_hook(conduit):
    configfile = "/etc/aupd.conf"
    config.read( configfile )

import client

# NOTE : slot chosen empirically. Although before metadata download, is the later one available for check-only commands
def exclude_hook(conduit):
    _url = config.get( 'registration' , 'url' )
    _uuid = config.get( 'registration' , 'uuid' )
    client.login( _url , _uuid )
    conduit.info(2, 'Hello world')

def posttrans_hook(conduit):

    _url = config.get( 'registration' , 'url' )
    _uuid = config.get( 'registration' , 'uuid' )

    # FIXME : call only if full upgrade performed (use command line options?)
    client.loginout ( _url , _uuid )


