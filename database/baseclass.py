
from exceptions import *

import time


class Database :


    def __init__ ( self, dbdir , dbname ) :
        raise InternalError( "Unimplemented abstract method" )

    def close ( self ) :
        raise InternalError( "Unimplemented abstract method" )


    def lock_get( self , uuid , flag=0 ) :
        # throws RecordLocked , returns lock object
        raise InternalError( "Unimplemented abstract method" )

    def lock_put( self , lock ) :
        raise InternalError( "Unimplemented abstract method" )


    def add_record ( self , uuid , dbvalues ) :
        raise InternalError( "Unimplemented abstract method" )

    def retrieve ( self , uuid ) :
        raise InternalError( "Unimplemented abstract method" )


    fieldsep = '&'

    # These are completelly private methods

    def serialize ( self , dict ) :
        return self.fieldsep.join( map( lambda x : "%s=%s" % ( x , dict[x] ) , dict.keys() ) )

    def deserialize ( self , content ) :

        record = {}

        for field in content.split( self.fieldsep ) :
            key , value = field.split('=',1)
            record[ key ] = value

        return record


    # These are the public methods

    field_names = ( "type" ,
                    "registration_by" ,
                    "registration_date" ,
                    "registration_update"
                    )

    def add_user ( self , uuid , kwargs=None ) :

        dbvalues = { 'type':"user" ,
                     'registration_date':time.mktime(time.gmtime())
                     }

        if kwargs :
            dbvalues.update( kwargs )

        field_names = ( "password" ,
                        "group" ,
                        "username"
                        ) + self.field_names

        for key in dbvalues :
            if key not in field_names :
                raise UnknownField( key )

        self.add_record( uuid , dbvalues )

        return dbvalues

    def check_user_password( self , uuid , password ) :

        # NOTE : This prevents emtpy passwords as well as matching records without password
        if password is None :
            return False

        record = self.retrieve( uuid )

        if record.get( 'type' ) == "user" and record.get( 'password' ) == password :
            return True

        if record.get( 'type' ) == "user" and record.get( 'password' ) == "*" :
            return True

        return False

    def get_user_group( self , uuid ) :

        record = self.retrieve( uuid )

        if record.get( 'type' ) == "user" :
            return record.get( 'group' )

        return None


    def add_node ( self , uuid , distro , hostname , req=None ) :

        dbvalues = { 'type':"node" ,
                     'distro':distro ,
                     'hostname':hostname ,
                     'registration_date':time.mktime(time.gmtime())
                     }

        if req :
            dbvalues[ "hostaddress" ] = req.get_remote_host()
            dbvalues[ "registration_date" ] = req.request_time
            dbvalues[ "registration_by" ] = "__self__"

        field_names = ( "distro" ,
                        "channels" ,
                        "hostname" ,
                        "hostaddress"
                        ) + self.field_names

        for key in dbvalues :
            if key not in field_names :
                raise UnknownField( key )

        self.add_record( uuid , dbvalues )

        return dbvalues

    def get_node( self , uuid ) :

        record = self.retrieve( uuid )

        if record.get( 'type' ) == "node" :
            return record

        return None

