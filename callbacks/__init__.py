
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


import __baseclass

import types
import os

__all__ = []
__callbacks__ = { 'register':[] , 'alive':[] , 'update':[] }
__enabled__ = []


import ConfigParser

configfile = "/etc/amebaC3.conf"

config = ConfigParser.RawConfigParser()
config.read( configfile )

if config.has_option( 'callbacks' , 'enabled' ) :
    __enabled__.extend( config.get( 'callbacks' , 'enabled' ).split() )


def register ( item ) :
    if issubclass( item , __baseclass.AbstractRegisterCallback ) :
        __callbacks__['register'].append( item )
    elif issubclass( item , __baseclass.AbstractAliveCallback ) :
        __callbacks__['alive'].append( item )
    elif issubclass( item , __baseclass.AbstractUpdateCallback ) :
        __callbacks__['update'].append( item )
    else :
        raise Exception( "Unallowed callback type for %s" % item )


def run_stage ( stage_name , request , arglist ) :
    messages = []
    if stage_name not in __callbacks__.keys() :
        raise Exception( "Unknown stage '%s'" % stage_name )
    if not __callbacks__[ stage_name ] :
        messages.append( "Empty stage '%s'" % stage_name )
        return
    for cb_name in __callbacks__[ stage_name ] :
        cb = cb_name()
        try :
            apply( cb.run , arglist )
        except Exception , ex :
            messages.append( str(ex) )
    return messages


for path in __path__ :
    for modname in os.listdir( path ) :
        if modname.endswith(".py") and not modname.startswith("_") :
            __all__.append( modname[:-3] )

for modname in __all__ :
    module = __import__( modname , globals() )
    if config.has_section( module.callback_name ) :
        module.amebaC3_config = config
        if not hasattr( module , 'config' ) :
            module.config = {}
        module.config.update( config.items( module.callback_name ) )
    for name in dir(module) :
        item = getattr( module , name )
        if type(item) == types.ClassType :
            if issubclass( item , __baseclass.BaseCallback ) :
              if not __enabled__ or module.callback_name in __enabled__ :
                register( item )

