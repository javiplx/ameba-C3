
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

    def get_record( self , uuid , record_type ) :

        try :
            record = self.retrieve( uuid )
            if record.get( 'type' ) == record_type :
                return record
        except KeyNotFound , ex :
            pass

        return None


    # This block corresponds only to simple-sting based storages (file, bdb, ...)

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

        dbvalues = {}

        if kwargs :
            dbvalues.update( kwargs )

        dbvalues['type'] = "user"
        dbvalues['registration_date'] = time.mktime(time.gmtime())

        field_names = ( "password" ,
                        "group" ,
                        "username"
                        ) + self.field_names

        for key in dbvalues :
            if key not in field_names :
                raise UnknownField( key )

        self.add_record( uuid , dbvalues )

        return dbvalues

    # NOTE : This function does not fit very well on a database-alike interface
    def check_user_password( self , uuid , password ) :

        # NOTE : This prevents emtpy passwords as well as matching records without password
        # NOTE2 : Sure ?? What about the logic behind 'is None' ??
        if password is None :
            return False

        record = self.get_record( uuid , "user" )

        if record :
            if record.get( 'password' ) == password or record.get( 'password' ) == "*" :
                return True

        return False

    def get_user_group( self , uuid ) :

        record = self.get_record( uuid , "user" )

        if record :
            return record.get( 'group' )

        return None


    def add_node ( self , args , req=None ) :
        uuid = args['UUID']

        dbvalues = { 'type':"node" ,
                     'distro':args['DISTRO'] ,
                     'hostname':args['HOSTNAME'] ,
                     'registration_date':time.mktime(time.gmtime())
                     }

        if args.has_key( 'METRICS' ) :
            dbvalues[ "metrics" ] = args['METRICS']

        if args.has_key( 'SERVICES' ) :
            dbvalues[ "services" ] = args['SERVICES']

        if req :
            dbvalues[ "hostaddress" ] = req.get_remote_host()
            dbvalues[ "registration_date" ] = req.request_time
            dbvalues[ "registration_by" ] = "__self__"

        field_names = ( "distro" ,
                        "channels" ,
                        "metrics" ,
                        "services" ,
                        "hostname" ,
                        "hostaddress"
                        ) + self.field_names

        for key in dbvalues :
            if key not in field_names :
                raise UnknownField( key )

        self.add_record( uuid , dbvalues )

        return dbvalues

    def get_node( self , uuid ) :

        return self.get_record( uuid , "node" )

