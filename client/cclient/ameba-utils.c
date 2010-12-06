
#include "ameba-utils.h"

#include <stdio.h>
#include <string.h>
#include <limits.h>


#define AMEBA_UPDATER_MAIN_SECTION "global"


// TODO : List alternatives for glib .ini library

GKeyFile *allocate_configuration( void ) {
    GKeyFile *config = g_key_file_new();
    return config;
}

GKeyFile *get_configuration ( void ) {

    GKeyFile *config = allocate_configuration();

    if ( g_key_file_load_from_file( config , AMEBA_UPDATER_CONFIG_FILE , G_KEY_FILE_KEEP_COMMENTS , NULL ) )
        return config;

    g_key_file_free( config );
    return NULL;
}

void save_configuration ( GKeyFile * config ) {
    FILE *fd;
    if ( fd = fopen( AMEBA_UPDATER_CONFIG_FILE , "w" ) ) {
        fprintf( fd , "%s" , g_key_file_to_data( config , NULL , NULL ) );
        fclose( fd );
    }
    free_configuration( config );
}

void free_configuration ( GKeyFile * config ) {
        g_key_file_free( config );
}

/* check_uuid 0 or NULL don't check presence of uuid */
int check_configuration ( GKeyFile *config , int check_uuid ) {

    if ( ! g_key_file_has_group( config , AMEBA_UPDATER_MAIN_SECTION ) )
        return 0;

    if ( ! g_key_file_has_key( config , AMEBA_UPDATER_MAIN_SECTION , "url" , NULL ) )
        return 0;

    if ( check_uuid )
        if ( ! g_key_file_has_key( config , AMEBA_UPDATER_MAIN_SECTION , "uuid" , NULL ) )
            return 0;

    return 1;
}

char *get_configuration_value ( GKeyFile *config , const char *key ) {
    return g_key_file_get_value( config , AMEBA_UPDATER_MAIN_SECTION , key , NULL );
}

void set_configuration_value( GKeyFile *config , const char *key , const char *value ) {
    g_key_file_set_value( config , AMEBA_UPDATER_MAIN_SECTION , key , value );
}


/* Create and populate the node info structure */

nodeinfo *get_nodeinfo( const char *uuid , const char *distro ) {

    if ( ! distro )
        return NULL;

    nodeinfo *nodedata = malloc( sizeof(nodeinfo) );
    memset( nodedata , '\0' , sizeof(nodeinfo) );

    nodedata->uuid = (char *) malloc( strlen(uuid) * sizeof(char) );
    strcpy( nodedata->uuid , uuid );

    nodedata->hostname = (char *) malloc( HOST_NAME_MAX * sizeof(char) );
    if ( gethostname( nodedata->hostname , HOST_NAME_MAX ) ) {
        free_nodeinfo( nodedata );
        return NULL;
        }

    nodedata->distro = (char *) malloc( strlen(distro) * sizeof(char) );
    strcpy( nodedata->distro , distro );

    return nodedata;
}

