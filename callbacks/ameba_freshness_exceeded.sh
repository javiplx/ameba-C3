#!/bin/sh

. /usr/lib/nagios/plugins/utils.sh

${ECHO} "UNKNOWN - freshness threshold exceeded"

exit ${STATE_UNKNOWN}
