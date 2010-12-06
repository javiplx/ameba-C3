
#include "client.h"


#include <string.h>
#include <stdlib.h>


void free_nodeinfo( nodeinfo *node ) {
    free(node-> uuid);
    free(node->hostname);
    free(node->distro);
    free(node);
}


CURL *build_webclient ( const char *url ) {
    CURL *curl;

    curl = curl_easy_init();
    if(!curl) {
        curl_easy_cleanup( curl );
        return NULL;
    }

    curl_easy_setopt( curl , CURLOPT_URL , url );
    curl_easy_setopt( curl , CURLOPT_USERAGENT , "libcurl-agent/1.0");

    return curl;
}

void do_webrequest( CURL *req ) {
    CURLcode res;
    res = curl_easy_perform( req );
    curl_easy_cleanup( req );
}

size_t null_reader( void *ptr, size_t size, size_t nmemb, void *userdata) {
    return size * nmemb;
}

size_t sessid_reader( void *ptr, size_t size, size_t nmemb, void *userdata) {
    sscanf( ptr , "ID %s" , userdata );
    return size * nmemb;
}

void register_node( const char *server_url , const nodeinfo *nodedata ) {
    size_t url_len = strlen(server_url) + 10;
    char *url = malloc( url_len * sizeof(char) );
    snprintf( url , url_len , "%s/register", server_url ); 

    CURL *request = build_webclient( url );

    char *postdata = malloc( 256 * sizeof(char*) );
    snprintf( postdata , 256 , "UUID=%s&HOSTNAME=%s&DISTRO=%s", nodedata->uuid , nodedata->hostname , nodedata->distro ); 
    curl_easy_setopt( request , CURLOPT_POSTFIELDS , postdata);

    curl_easy_setopt( request , CURLOPT_WRITEFUNCTION , null_reader );

    do_webrequest( request );

    free( postdata );
    free( url );
}

void login_node( const char *server_url , const char *uuid , char *sessid) {
    size_t url_len = strlen(server_url) + 7;
    char *url = malloc( url_len * sizeof(char) );
    snprintf( url , url_len , "%s/login", server_url );  

    CURL *request = build_webclient( url );

    char *authorization = (char *) malloc( 256 * sizeof(char) );
    snprintf( authorization , 256 , "Authorization: UUID %s", uuid ); 

    struct curl_slist *chunk = NULL;
    chunk = curl_slist_append( chunk , authorization );
    curl_easy_setopt( request , CURLOPT_HTTPHEADER , chunk );

    curl_easy_setopt( request , CURLOPT_WRITEFUNCTION , sessid_reader );
    curl_easy_setopt( request , CURLOPT_WRITEDATA , sessid );

    do_webrequest( request );
    curl_slist_free_all(chunk);

    free( authorization );
    free( url );
}

void logout_node( const char *server_url , const char *sessid , const char *status) {
    size_t url_len = strlen(server_url) + 8;
    char *url = malloc( url_len * sizeof(char) );
    snprintf( url , url_len , "%s/logoff", server_url );  

    CURL *request = build_webclient( url );

    char *cookie = (char *) malloc( 256 * sizeof(char) );
    snprintf( cookie , 256 , "pysid=%s", sessid ); 
    curl_easy_setopt( request , CURLOPT_COOKIE , cookie );

    char *ameba_status = NULL;
    struct curl_slist *chunk = NULL;
    if ( status ) {
        char *ameba_status = (char *) malloc( ( strlen(status) + 16 ) * sizeof(char) );
        snprintf( ameba_status , 256 , "X-AmebaStatus: %s", status ); 

        chunk = curl_slist_append( chunk , ameba_status );
        curl_easy_setopt( request , CURLOPT_HTTPHEADER , chunk );
    }

    curl_easy_setopt( request , CURLOPT_WRITEFUNCTION , null_reader );

    do_webrequest( request );
    if ( chunk ) {
        curl_slist_free_all(chunk);
        free( ameba_status );
    }

    free( cookie );
    free( url );
}
