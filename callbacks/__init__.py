
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


def register ( item ) :
    if issubclass( item , __baseclass.AbstractRegisterCallback ) :
        __callbacks__['register'].append( item )
    elif issubclass( item , __baseclass.AbstractAliveCallback ) :
        __callbacks__['alive'].append( item )
    elif issubclass( item , __baseclass.AbstractUpdateCallback ) :
        __callbacks__['update'].append( item )
    else :
        raise Exception( "Unallowed callback type for %s" % item )


for path in __path__ :
    for modname in os.listdir( path ) :
        if modname.endswith(".py") and not modname.startswith("_") :
            __all__.append( modname[:-3] )

for modname in __all__ :
    module = __import__( modname , globals() )
    for name in dir(module) :
        item = getattr( module , name )
        if type(item) == types.ClassType :
            if issubclass( item , __baseclass.BaseCallback ) :
                register( item )

