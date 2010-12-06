#!/bin/sh


distroname=`uci get webif.general.firmware_name`

while getopts "d:" opt ; do

  case $opt in
    d) test "${distroname}" != "${OPTARG}" && echo "WARNING : Guessed distro name '${distroname}' differs from supplied on command line '${OPTARG}'"
       distroname=${OPTARG}
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

  esac

