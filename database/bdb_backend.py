
# Por que usar btree con record numbers
# http://www.oracle.com/technology/documentation/berkeley-db/db/programmer_reference/bt_conf.html#am_conf_bt_recnum
import bsddb


import database

class Database ( database.Database ) :

    def __init__ ( self, dbdir , dbname ) :

        self.dbenv = bsddb.db.DBEnv()
        self.dbenv.open( dbdir , bsddb.db.DB_INIT_LOCK | bsddb.db.DB_INIT_MPOOL | bsddb.db.DB_CREATE , 0600 )

        self.dbname = "%s.db" % dbname

        self.dbenv.set_timeout( 500, bsddb.db.DB_SET_LOCK_TIMEOUT )
        self.dblock = self.dbenv.lock_id()

    def close ( self ) :
    #    self.dbenv.lock_id_free( self.dblock )
        self.dbenv.close()


    def lock_get( self , uuid , flag=0 ) :
        try :
            lock = self.dbenv.lock_get( self.dblock , uuid , bsddb.db.DB_LOCK_WRITE , flag )
        except bsddb.db.DBLockNotGrantedError , ex :
            raise database.RecordLocked(uuid)
        except :
            raise Exception( "Unexpected excepton" )
        return lock

    def lock_put( self , lock ) :
        self.dbenv.lock_put(lock)


    def add_record ( self , uuid , dbvalues ) :

        db = bsddb.db.DB( self.dbenv )
        db.open( self.dbname , dbtype=bsddb.db.DB_HASH , flags=bsddb.db.DB_CREATE , mode=0600 )
        lock = self.lock_get( uuid , bsddb.db.DB_LOCK_NOWAIT )

        if db.has_key( uuid ) :
            db.close()
            self.lock_put(lock)
            raise database.KeyExists( uuid )

        db[ uuid ] = self.serialize( dbvalues )

        db.close()
        self.lock_put(lock)

    def retrieve ( self , uuid ) :

        db = bsddb.db.DB( self.dbenv )
        db.open( self.dbname , dbtype=bsddb.db.DB_HASH , flags=bsddb.db.DB_RDONLY )

        if not db.has_key( uuid ) :
            db.close()
            raise database.KeyNotFound( uuid )

        record = self.deserialize( db[uuid] )

        db.close()

        return record

