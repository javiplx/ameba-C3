
import os


import database

import time

class Database ( database.Database ) :

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
                raise database.RecordLocked(uuid)
            time.sleep( 0.01 )
            while os.path.exists( lock ) :
                time.sleep( 0.01 )
        fd = open( lock , 'w' )
        fd.close()
        return lock

    def lock_put( self , lock ) :
        os.unlink( lock )


    def add_record ( self , uuid , dbvalues ) :

        lock = self.lock_get( uuid , 1 )
        fname = os.path.join( self.dbenv , uuid )

        if os.path.exists( fname ) :
            self.lock_put(lock)
            raise database.KeyExists( uuid )

        fd = open( fname , 'w' )
        fd.write( self.serialize( dbvalues ) )
        fd.close()

        self.lock_put(lock)

    def retrieve ( self , uuid ) :

        fname = os.path.join( self.dbenv , uuid )

        if not os.path.exists( fname ) :
            raise database.KeyNotFound( uuid )

        fd = open( fname )
        record = self.deserialize( "".join( fd.readlines() ) )
        fd.close()

        return record

