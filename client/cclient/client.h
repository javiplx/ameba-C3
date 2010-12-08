
/* Copyright (C) 2010 Javier Palacios

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License Version 2
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details. */


#ifndef AMEBA_UPDATER_H
#define AMEBA_UPDATER_H


#include <curl/curl.h>


struct nodeinfo {
    char *uuid;
    char *hostname;
    char *distro;
};

typedef struct nodeinfo nodeinfo;

void free_nodeinfo( nodeinfo * );

CURL *build_webclient ( const char * );
void do_webrequest( CURL * );

void register_node( const char * , const nodeinfo * );

void login_node( const char * , const char * , char * );

void logout_node( const char * , const char * , const char *);

#endif
