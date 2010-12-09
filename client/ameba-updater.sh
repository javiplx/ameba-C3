#!/bin/sh

# Copyright (C) 2010 Javier Palacios
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License Version 2
# as published by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


distroname=`uci get webif.general.firmware_name`
random_wait=""

progname=$0

print_usage () {
    prog=$1
cat <<EOF
${prog} [--requestuuid] [--d distroname] register url [uuid]
${prog} [-w seconds] [--check-only|--force-upgrade] pull
${prog} login
${prog} loginout
EOF
}

while getopts "d:w:" opt ; do

  case $opt in
    d) test "${distroname}" != "${OPTARG}" && echo "WARNING : Guessed distro name '${distroname}' differs from supplied on command line '${OPTARG}'"
       distroname=${OPTARG}
       ;;
    w) random_wait=${OPTARG}
       ;;
    *) print_usage
       exit 1
       ;;
    esac
    
  done

eval action=\$$OPTIND
shift $OPTIND

case $action in

  register)
    if [ $# -ne 2 ] ; then
      echo "ERROR : register bad usage"
      exit 1
      fi
    url=$1
    uuid=$2
    distroname=`echo $distroname | tr ' ' '_'`
    postdata="UUID=${uuid}&HOSTNAME=`uname -n`&DISTRO=${distroname}"
    response=`wget -q -O - "${url}/register?${postdata}"`
    if [ "${response}" = "OK" ] ; then
      uci set aupd.main=global
      uci set aupd.main.url=${url}
      uci set aupd.main.uuid=${uuid}
      uci commit
      fi
    ;;

  login)
    if [ $# -ne 0 ] ; then
      echo "ERROR : login bad usage"
      exit 1
      fi
    url=`uci get aupd.main.url`
    uuid=`uci get aupd.main.uuid`
    response=`wget -q --header "Authorization: UUID ${uuid}" -O - "${url}/login"`
    set -- `echo $response | head -1`
    if [ $# -eq 2 -a "$1" = "ID" ] ; then
      sessid=$2
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
    response=`wget -q --header "Authorization: UUID ${uuid}" -O - "${url}/login"`
    set -- `echo $response | head -1`
    if [ $# -eq 2 -a "$1" = "ID" ] ; then
      sessid=$2
      fi
    response=`wget -q --header "X-AmebaStatus: ${status}" --header "Cookie: pysid=${sessid}" -O - "${url}/logoff"`
    ;;

  pull)                                                                                                                                                     
    if [ $# -ne 0 ] ; then                                                                                                                                  
      echo "ERROR : pull bad usage"                                                                                                                         
      exit 1                                                                                                                                                
      fi                                                                                                                                                    
    test -n "${random_wait}" && sleep ${random_wait}
    ipkg -V 0 update && ipkg -test upgrade | grep -q '^Upgrading '                                                                                          
    if [ $? -eq 1 ] ; then                                                                                                                                  
      status="OK"                                                                                                                                           
    else                                                                                                                                                    
      status="WARNING"                                                                                                                                      
      fi                                                                                                                                                    
    url=`uci get aupd.main.url`                                                                                                                             
    uuid=`uci get aupd.main.uuid`                                                                                                                           
    response=`wget -q --header "Authorization: UUID ${uuid}" -O - "${url}/login"`                                                                           
    set -- `echo $response | head -1`                                                                                                                       
    if [ $# -eq 2 -a "$1" = "ID" ] ; then                                                                                                                   
      sessid=$2                                                                                                                                             
      fi                                                                                                                                                    
    response=`wget -q --header "X-AmebaStatus: ${status}" --header "Cookie: pysid=${sessid}" -O - "${url}/logoff"`                                          
    ;;                                                                                                                                                      

  *)
    print_usage ${progname}
    ;;

  esac

