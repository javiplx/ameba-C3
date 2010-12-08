
/* Copyright (C) 2010 Javier Palacios

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License Version 2
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details. */


#ifndef AMEBA_UPDATER_UTILS_H
#define AMEBA_UPDATER_UTILS_H

#include "client.h"

#include <glib.h>

#include <stdlib.h>


GKeyFile *get_configuration ( void );
void free_configuration ( GKeyFile * );

// Default should be 1, to force verification for uuid
int check_configuration ( GKeyFile * , int );

char *get_configuration_value ( GKeyFile * , const char * );

nodeinfo *get_nodeinfo( const char * , const char * );

#endif
