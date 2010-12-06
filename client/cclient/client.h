
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
