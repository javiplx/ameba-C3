DESCRIPTION = "AmebaC3 update agent"
SECTION = "admin"
PRIORITY = "optional"
LICENSE = "GPLv2"

SRCREV = "master"
PR = "r2"

SRC_URI = "\
  git://github.com/javiplx/ameba-C3.git;protocol=http;branch=master \
"

S = "${WORKDIR}/git/client"

inherit distutils
