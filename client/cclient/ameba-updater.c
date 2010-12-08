
/* Copyright (C) 2010 Javier Palacios

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License Version 2
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details. */


#include "ameba-utils.h"

#include <getopt.h>

#include <string.h> // For memset


void print_usage ( char * prog ) {
    printf( "%s [--requestuuid] [--distro distroname] register url [uuid]\n"
            "%s [--random-wait seconds] [--check-only|--force-upgrade] pull\n"
            "%s login\n"
            "%s loginout\n" , prog , prog , prog , prog );
}


static struct option long_options[] = {
    {"distro",  required_argument, 0, 'd'},
    {0, 0, 0, 0}
    };


int main ( int argc, char* argv[] ) {

    char *distroname = NULL;
    int valid_args , c;

    while (1) {
        int option_index = 0;

        c = getopt_long_only( argc , argv , "d:" , long_options , &option_index );
        if (c == -1)
            break;
     
        switch (c) {

            case 'd':
                distroname = malloc( strlen(optarg) * sizeof(char) );
                strcpy( distroname , optarg );
                break;
     
        }
    }

    valid_args = argc - ( optind - 1 );

    if ( valid_args < 2 ) {
        print_usage( argv[0] );
        exit(1);
    }

    if ( strcmp( argv[optind] , "register" ) == 0 ) {
        if ( valid_args != 4 ) {
            printf( "Usage register\n" );
            exit(1);
        }
    }

    if ( strcmp( argv[optind] , "login" ) == 0 ) {
        if ( valid_args != 2 ) {
            printf( "Usage login\n" );
            exit(1);
        }
    }

    if ( strcmp( argv[optind] , "loginout" ) == 0 ) {
        if ( valid_args != 3 ) {
            printf( "Usage logout\n" );
            exit(1);
        }
    }

    // TODO : Use a define instead of 256 AMEBA_SESSID_MAX_LENGTH
    char *sessid = malloc( 256 * sizeof(char) );
    memset( sessid , '\0' , 256 );

    if ( strncmp( argv[optind] , "login" , 5 ) == 0 ) {

        GKeyFile *config = get_configuration();

        if ( ! check_configuration( config , 1 ) ) {
            printf("No valid configuration exists\n");
            free_configuration( config );
            exit(2);
        }

        login_node( get_configuration_value( config , "url" ) , get_configuration_value( config , "uuid" ) , sessid );

        free_configuration( config );
    }

    if ( strcmp( argv[optind] , "loginout" ) == 0 ) {

        GKeyFile *config = get_configuration();

        if ( ! check_configuration( config , 1 ) ) {
            printf("No valid configuration exists\n");
            free_configuration( config );
            exit(2);
        }

        logout_node( get_configuration_value( config , "url" ) , sessid , argv[optind+1] );

        free_configuration( config );
    }

    if ( strcmp( argv[optind] , "register" ) == 0 ) {

        nodeinfo *nodedata = get_nodeinfo( argv[optind+2] , distroname );
        if ( ! nodedata ) {
            exit(-255);
            }

        register_node( argv[optind+1] , nodedata );

        free_nodeinfo( nodedata );
    }

    free(sessid);
    exit(0);
}


