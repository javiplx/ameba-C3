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

setup(
	name = "AmebaC3 updater" ,
	version = "1.1" ,
	description = "AmebaC3 update agent" ,
	author = "Javier Palacios" ,
	author_email = "javiplx@gmail.com" ,
	scripts = [ "aupd" ] ,
	package_dir = { 'amebaC3_client':"" } ,
	packages = [ "amebaC3_client" ] ,
#	package_data = { 'amebaC3_client': [ "externals/15ameba-updater" , "externals/ameba-updater.py" ] } ,
	license = "GPLv2"
	)

