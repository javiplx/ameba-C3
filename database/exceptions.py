
class C3DBException ( Exception ) :
    def __init__ ( self , msg ) :
        classname = str( self.__class__ )
        self.type = classname.replace( "%s." % self.__module__ , "" )
        Exception.__init__( self , msg )

class UnknownField ( C3DBException ) :
    def __init__ ( self , field ) :
        message = "key '%s' unknown" % field
        C3DBException.__init__( self , message )

class KeyExists ( C3DBException ) :
    def __init__ ( self , uuid ) :
        message = "'%s' already registered" % uuid
        C3DBException.__init__( self , message )

class KeyNotFound ( C3DBException ) :
    def __init__ ( self , uuid ) :
        message = "'%s' not found" % uuid
        C3DBException.__init__( self , message )

class RecordLocked ( C3DBException ) :
    def __init__ ( self , uuid ) :
        message = "'%s' locked" % uuid
        C3DBException.__init__( self , message )

class InternalError ( C3DBException ) :
    def __init__ ( self , reason ) :
        message = reason
        C3DBException.__init__( self , message )

