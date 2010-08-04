
class C3DBException ( Exception ) :
    def __init__ ( self ) :
        classname = str( self.__class__ )
        self.type = classname.replace( "%s." % self.__module__ , "" )
        Exception.__init__( self )

class UnknownField ( C3DBException ) :
    def __init__ ( self , field ) :
        C3DBException.__init__( self )
        self.message = "key '%s' unknown" % field

class KeyExists ( C3DBException ) :
    def __init__ ( self , uuid ) :
        C3DBException.__init__( self )
        self.message = "'%s' already registered" % uuid

class KeyNotFound ( C3DBException ) :
    def __init__ ( self , uuid ) :
        C3DBException.__init__( self )
        self.message = "'%s' not found" % uuid

class RecordLocked ( C3DBException ) :
    def __init__ ( self , uuid ) :
        C3DBException.__init__( self )
        self.message = "'%s' locked" % uuid

class InternalError ( C3DBException ) :
    def __init__ ( self , reason ) :
        C3DBException.__init__( self )
        self.message = reason

