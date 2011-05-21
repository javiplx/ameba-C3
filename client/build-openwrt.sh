#!/bin/sh

# Registration
# ameba-updater.sh -r register http://r26936.ovh.net/amebaC3

mkdir -p ameba-wrt/CONTROL

cat <<EOF > ameba-wrt/CONTROL/control
Package: amebac3-shell-client
Version: 0.9.2-1
Architecture: all
Maintainer: Javier Palacios <javiplx@gmail.com>
Description: AmebaC3 update shell agent
Section: admin
Priority: optional
Source: https://github.com/javiplx/ameba-C3/tarball/master
EOF

mkdir -p ameba-wrt/bin
cp ameba-updater.sh ameba-wrt/bin

opkg-build -O ameba-wrt

rm -rf ameba-wrt

