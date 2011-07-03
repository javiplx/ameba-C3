#!/bin/sh

# Copyright (C) 2010, 2011 Javier Palacios
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License Version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


version="0.9.4"

retcode=2

distroname=OpenWrt_`cat /etc/openwrt_version`
random_wait="300"
pull_mode="check"
metrics=""
services=""

progname=$0

print_usage () {
    prog=$1
    shift
    test $# -gt 0 && echo "ERROR : $*"
cat <<EOF
${prog} [-r] [-d distroname] [-m metric1,metric2,...] [-s service1,service2,...] register url [uuid]
${prog} [-w seconds] [-c|-f] pull
${prog} login
${prog} loginout
EOF
}


. /etc/functions.sh

guess_metrics() {

  config_load system
  cfg=`config_foreach echo stats`

  metrics=""
  for metric in `uci get system.${cfg}.metric` ; do
    case $metric in
      netdev)
         for ifname in `awk -F: 'NF>1 { print $1 }' /proc/net/dev | tr '.' '_'` ; do
           metrics=$metrics" netdev."$ifname
           done
         ;;
      *) metrics=$metrics" "$metric
         ;;
      esac
    done

  echo $metrics | tr ' ' ','
}


while getopts "rd:w:m:cfs:" opt ; do

  case $opt in
    d) test -n "${distroname}" -a "${distroname}" != "${OPTARG}" && echo "WARNING : Guessed distro name '${distroname}' differs from supplied on command line '${OPTARG}'"
       distroname=${OPTARG}
       ;;
    w) random_wait=${OPTARG}
       ;;
    r) requestuuid="Y"
       ;;
    c) pull_mode="check"
       ;;
    m) test ${OPTARG} = "auto" && metrics=`guess_metrics` || metrics=${OPTARG}
       ;;
    s) services=${OPTARG}
       ;;
    f) pull_mode="upgrade"
       ;;
    *) print_usage ${progname}
       exit 1
       ;;
    esac

  done

eval action=\$$OPTIND
test -n "${action}" && shift $OPTIND

case $action in

  register)
    if [ -n "${requestuuid}" ] ; then
      if [ $# -eq 2 -a "$2" != "__REQUEST__" ] ; then
        echo "ERROR : Unallowed request for UUID when a value is supplied on command line"
        fi
      set -- $1 __REQUEST__
      fi
    if [ $# -ne 2 ] ; then
      echo "ERROR : register bad usage"
      exit 1
      fi
    url=$1
    uuid=$2
    distroname=`echo $distroname | tr ' ' '_'`
    postdata="UUID=${uuid}&HOSTNAME=`uname -n`&DISTRO=${distroname}"
    test -n "${metrics}" && postdata="${postdata}&METRICS=${metrics}"
    test -n "${services}" && postdata="${postdata}&SERVICES=${services}"
    wget -q -U "AmebaC3-Agent/${version} (shell)" -O /tmp/aupd.response.$$ "${url}/register?${postdata}" 2> /dev/null
    if [ -s /tmp/aupd.response.$$ ] ; then
     if [ ${uuid} = "__REQUEST__" ] ; then
      uuid=`sed -n -e 's/^UUID //p' /tmp/aupd.response.$$`
      response=`grep -v '^UUID' /tmp/aupd.response.$$`
     else
      response=`cat /tmp/aupd.response.$$`
      fi
     if [ "${response}" = "OK" ] ; then
      touch /etc/config/aupd
      uci set aupd.main=global
      uci set aupd.main.url=${url}
      uci set aupd.main.uuid=${uuid}
      uci commit aupd
      retcode=0
      fi
     fi
    rm -f /tmp/aupd.response.$$
    ;;

  login)
    if [ $# -ne 0 ] ; then
      echo "ERROR : login bad usage"
      exit 1
      fi
    url=`uci get aupd.main.url`
    uuid=`uci get aupd.main.uuid`
    response=`wget -q -U "AmebaC3-Agent/${version} (shell)" -O - --header "Authorization: UUID ${uuid}" "${url}/login" 2> /dev/null`
    if [ -n "${response}" ] ; then
     set -- `echo $response | head -1`
     if [ $# -eq 2 -a "$1" = "ID" ] ; then
      sessid=$2
      retcode=0
      fi
     fi
    ;;

  loginout)
    if [ $# -ne 1 ] ; then
      echo "ERROR : loginout bad usage"
      exit 1
      fi
    status=$1
    url=`uci get aupd.main.url`
    uuid=`uci get aupd.main.uuid`
    response=`wget -q -U "AmebaC3-Agent/${version} (shell)" -O - --header "Authorization: UUID ${uuid}" "${url}/login" 2> /dev/null`
    if [ -n "${response}" ] ; then
     set -- `echo $response | head -1`
     if [ $# -eq 2 -a "$1" = "ID" ] ; then
      sessid=$2
      response=`wget -q -U "AmebaC3-Agent/${version} (shell)" -O - --header "X-AmebaStatus: ${status}" --header "Cookie: pysid=${sessid}" "${url}/logoff" 2> /dev/null`
      if [ -n "${response}" ] ; then
        retcode=0
        fi
      fi
     fi
    ;;

  pull)
    if [ $# -ne 0 ] ; then
      echo "ERROR : pull bad usage"
      exit 1
      fi
    if [ ${pull_mode} = "upgrade" ] ; then
      test -n "${random_wait}" && sleep ${random_wait}
      opkg -V 0 upgrade > /dev/null
      if [ $? -eq 1 ] ; then
        status="OK"
      else
        status="ERROR"
        fi
    else
      test -n "${random_wait}" && sleep ${random_wait}
      opkg -V 0 update 2> /dev/null && opkg -test upgrade 2> /dev/null | grep -q '^Upgrading '
      if [ $? -eq 1 ] ; then
        status="OK"
      else
        status="WARNING"
        fi
      fi
    url=`uci get aupd.main.url`
    uuid=`uci get aupd.main.uuid`
    response=`wget -q -U "AmebaC3-Agent/${version} (shell)" -O - --header "Authorization: UUID ${uuid}" "${url}/login" 2> /dev/null`
    if [ -n "${response}" ] ; then
     set -- `echo $response | head -1`
     if [ $# -eq 2 -a "$1" = "ID" ] ; then
      sessid=$2
      response=`wget -q -U "AmebaC3-Agent/${version} (shell)" -O - --header "X-AmebaStatus: ${status}" --header "Cookie: pysid=${sessid}" "${url}/logoff" 2> /dev/null`
      if [ -n "${response}" ] ; then
        retcode=0
        fi
      fi
     fi
    ;;

  *)
    print_usage ${progname} "Unknown operation"
    retcode=1
    ;;

  esac

exit ${retcode}
