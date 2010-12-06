
#ifndef AMEBA_UPDATER_UTILS_H
#define AMEBA_UPDATER_UTILS_H

#include "client.h"

#include <glib.h>

#include <stdlib.h>


#define AMEBA_UPDATER_CONFIG_FILE "/etc/aupd.conf"


GKeyFile *allocate_configuration ( void );
GKeyFile *get_configuration ( void );
void save_configuration ( GKeyFile * );
void free_configuration ( GKeyFile * );

// Default should be 1, to force verification for uuid
int check_configuration ( GKeyFile * , int );

char *get_configuration_value ( GKeyFile * , const char * );
void set_configuration_value( GKeyFile * , const char * , const char * );

nodeinfo *get_nodeinfo( const char * , const char * );

#endif
