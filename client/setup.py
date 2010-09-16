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


from distutils.core import setup

script_name = "aupd"
#import imp , os
#aupd = imp.load_source( script_name , script_name )
#os.unlink( "%sc" % script_name )

setup(
	name = "amebaC3_client" ,
#	version = aupd.__version__ ,
	version = "1.3" ,
	description = "AmebaC3 update agent" ,
	author = "Javier Palacios" ,
	author_email = "javiplx@gmail.com" ,
	url = "http://wiki.github.com/javiplx/ameba-C3" ,
	scripts = [ script_name ] ,
	package_dir = { 'amebaC3_client':"" } ,
	packages = [ "amebaC3_client" ] ,
#	package_data = { 'amebaC3_client': [ "externals/15ameba-updater" , "externals/ameba-updater.py" ] } ,
	license = "GPLv2"
	)

