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
	name = "amebaC3_client" ,
	version = "1.3.1" ,
	description = "AmebaC3 update agent" ,
	author = "Javier Palacios" ,
	author_email = "javiplx@gmail.com" ,
	url = "http://wiki.github.com/javiplx/ameba-C3" ,
	scripts = [ "aupd" ] ,
	package_dir = { 'amebaC3_client':"." } ,
	packages = [ "amebaC3_client" ] ,
	data_files = [
		( 'share/doc/amebaC3_client/samples' , [ "sample.conf" , "crontab.line" , "ameba-updater" ] ) ,
		( 'share/doc/amebaC3_client/externals' , [ "externals/15ameba-updater" , "externals/ameba-updater.py" ] )
		] ,
	license = "GPLv2"
	)

