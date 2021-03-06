
import os


import baseclass , exceptions

import time

class Database ( baseclass.Database ) :

    def __init__ ( self, dbdir , dbname ) :

        self.dbenv = os.path.join( dbdir , dbname )
        if not os.path.isdir( self.dbenv ) :
            os.mkdir( self.dbenv )

        self.fieldsep = '\n'

    def close ( self ) :
        pass


    def lock_get( self , uuid , flag=0 ) :
        lock = os.path.join( self.dbenv , ".%s" % uuid )
        if os.path.exists( lock ) :
            if flag : 
                raise exceptions.RecordLocked(uuid)
            time.sleep( 0.01 )
            while os.path.exists( lock ) :
                time.sleep( 0.01 )
        fd = open( lock , 'w' )
        fd.close()
        return lock

    def lock_put( self , lock ) :
        os.unlink( lock )


    def put ( self , uuid , dbvalues , update=False ) :

        lock = self.lock_get( uuid , 1 )
        fname = os.path.join( self.dbenv , uuid )

        if os.path.exists( fname ) :
            if update :
                os.unlink( fname )
            else :
                self.lock_put(lock)
                raise exceptions.KeyExists( uuid )

        fd = open( fname , 'w' )
        fd.write( self.serialize( dbvalues ) )
        fd.close()

        self.lock_put(lock)

    def get ( self , uuid ) :

        fname = os.path.join( self.dbenv , uuid )

        if not os.path.exists( fname ) :
            raise exceptions.KeyNotFound( uuid )

        fd = open( fname )
        record = self.deserialize( "".join( fd.readlines() )[:-1] )
        fd.close()

        return record

    def get_uuid ( self , name ) :

        for filename in os.listdir( self.dbenv ) :
          try :
            fd = open( os.path.join( self.dbenv , filename ) )
            record = self.deserialize( "".join( fd.readlines() )[:-1] )
            fd.close()
            if not record.has_key( 'uuid' ) :
                record['uuid'] = filename
            if record.get( 'hostname' ) == name :
                return record['uuid']
          except :
            pass

        raise exceptions.KeyNotFound( name )

