
import os


restart_allowed = True # [%lu] RESTART_PROGRAM
# [<timestamp>] PROCESS_SERVICE_CHECK_RESULT;<host_name>;<description>;<return_code>;<plugin_output>
# [<timestamp>] PROCESS_HOST_CHECK_RESULT;<host_name>;<host_status>;<plugin_output>

cfg_dir = "/etc/nagios/ameba"
commandfile = "/var/spool/nagios/cmd/nagios.cmd"

node_template = """define host{
        use                     ameba-node
        host_name               %(hostname)s%(random)s
        alias                   %(uuid)s
        address                 %(hostaddress)s
        }

define service{
        use                             local-service
        host_name                       %(hostname)s%(random)s
        service_description             ameba updater
	passive_checks_enabled		1
	check_freshness			1
	freshness_threshold		3600
        active_checks_enabled           0
        check_command                   check_freshness
        }
"""

group_template = """define hostgroup{
        hostgroup_name  %(distro)s
        alias           %(distro)s nodes
        members         %(hostname)s%(random)s
        }
"""

def run ( uuid , dbvalues ) :

    _dbvalues = { 'uuid':uuid }
    _dbvalues.update( dbvalues )

    import time
    _dbvalues['random'] = "-00"

    fname = os.path.join( cfg_dir , "%s.cfg" % uuid )
    # FIXME : Exception if exists? Is truncate is enough?
    # FIXME : Permissions
    fd = open( fname , 'w' )
    fd.write( node_template % _dbvalues )
    fd.close()

    coso = []
    fname = os.path.join( cfg_dir , "%s.cfg" % _dbvalues['distro'] )
    if os.path.exists( fname ) :
        outlines = []
        fd = open( fname )
        for line in fd.readlines() :
            if line.find( "members" ) != -1 :
                outlines.append( line.replace( "\n" , " , %s%s" % ( _dbvalues['hostname'] , _dbvalues['random'] ) ) )
            else :
                outlines.append( line[:-1] )
        fd.close()
        fd = open( fname , 'w' )
        fd.write( "\n".join( outlines ) )
        fd.write( "\n" )
        fd.close()
    else :
        fd = open( fname , 'w' )
        fd.write( group_template % _dbvalues )
        fd.close()

    if restart_allowed :
        fd = open( commandfile , 'a' )
        fd.write( "[%lu] RESTART_PROGRAM\n" % time.time() )
        fd.close()

