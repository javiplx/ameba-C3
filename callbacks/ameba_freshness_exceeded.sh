#!/bin/sh

. %PLUGINS_DIR%/utils.sh

${ECHO} "UNKNOWN - freshness threshold exceeded"

exit ${STATE_UNKNOWN}
