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
	name = "amebaC3_database" ,
	version = "1.0" ,
	description = "AmebaC3 database backend" ,
	author = "Javier Palacios" ,
	author_email = "javiplx@gmail.com" ,
	url = "http://wiki.github.com/javiplx/ameba-C3" ,
	package_dir = { 'amebaC3_database':"" } ,
	packages = [ "amebaC3_database" ] ,
	license = "GPLv2"
	)

