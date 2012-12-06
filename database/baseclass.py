
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


    def put ( self , uuid , dbvalues , update=False ) :
        raise InternalError( "Unimplemented abstract method" )

    def get ( self , uuid ) :
        raise InternalError( "Unimplemented abstract method" )


    def add_record ( self , uuid , dbvalues , field_names , update=False ) :

        for key in dbvalues :
            if key not in field_names + self.field_names :
                raise UnknownField( key )

        self.put( uuid , dbvalues , update )

        return dbvalues

    def get_record( self , uuid , record_type ) :

        try :
            record = self.get( uuid )
            if record.get( 'type' ) == record_type :
                return record
        except KeyNotFound , ex :
            pass

        return None


    def get_uuid ( self , name ) :
        raise InternalError( "Unimplemented abstract method" )


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
                        )

        self.add_record( uuid , dbvalues , field_names )

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
                        )

        self.add_record( uuid , dbvalues , field_names )

        return dbvalues

    def update_node ( self , dbvalues , args , req=None ) :

        dbvalues[ "distro" ] = args['DISTRO']
        dbvalues[ "hostname" ] = args['HOSTNAME']
        dbvalues[ "modification_date" ] = time.mktime(time.gmtime())

        if args.has_key( 'METRICS' ) :
            metrics = {}
            if dbvalues.has_key( "metrics" ) :
                metriclist = "%s," % dbvalues['metrics']
                metrics.update( dict.fromkeys( metriclist.split(',') ) )
            metriclist = "%s," % args['METRICS']
            metrics.update( dict.fromkeys( metriclist.split(',') ) )
            del metrics['']
            dbvalues[ "metrics" ] = ",".join( metrics.keys() )

        if args.has_key( 'SERVICES' ) :
            services = {}
            if dbvalues.has_key( "services" ) :
                servlist = "%s," % dbvalues['services']
                services.update( dict.fromkeys( servlist.split(',') ) )
            servlist = "%s," % args['SERVICES']
            services.update( dict.fromkeys( servlist.split(',') ) )
            del services['']
            dbvalues[ "services" ] = ",".join( services.keys() )

        if req :
            dbvalues[ "hostaddress" ] = req.get_remote_host()
            dbvalues[ "modification_date" ] = req.request_time

        field_names = ( "distro" ,
                        "channels" ,
                        "metrics" ,
                        "services" ,
                        "hostname" ,
                        "hostaddress" ,
                        "modification_date"
                        )

        self.add_record( args['UUID'] , dbvalues , field_names , True )

        return dbvalues

    def get_node( self , uuid ) :

        return self.get_record( uuid , "node" )

