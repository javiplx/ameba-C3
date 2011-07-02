
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


callback_name = None

class BaseCallback :

    name = None

    def run ( self , *args , **kwargs ) :
        pass

class AbstractRegisterCallback ( BaseCallback ) :
    pass

class AbstractAliveCallback ( BaseCallback ) :
    pass

class AbstractUpdateCallback ( BaseCallback ) :
    pass


