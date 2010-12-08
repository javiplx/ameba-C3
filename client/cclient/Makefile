
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


CPPFLAGS = $(shell pkg-config --cflags glib-2.0)
LDFLAGS = $(shell pkg-config --libs libcurl) $(shell pkg-config --libs glib-2.0)

default:

all: ameba-updater

client.o : client.c client.h

ameba-utils.h: client.h
ameba-utils.o : ameba-utils.c ameba-utils.h

ameba-updater: ameba-updater.o ameba-utils.o client.o

clean:
	rm -f *.o

fullclean: clean
	rm -f ameba-updater
