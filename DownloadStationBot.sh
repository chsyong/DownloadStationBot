#!/bin/bash

################################################
#        USER Setting
################################################
PYTHON_PATH="/usr/bin/python"
BOT_MAIN="./DownloadStationBot.py"
CFG_PATH="./DownloadStationBot.cfg"
################################################

function ProcChk()
{
    PID=`/bin/ps -ef | /bin/grep "python" | /bin/grep "DownloadStationBot.py" | /usr/bin/awk '{print $2}'`
    if [ "$PID" ] ;  then
        printf "%16s : [36m[1mRunning[0m\n" "XPEnology DownloadStationBot";
    else
        printf "%16s : [31m[1mStopped[0m\n" "XPEnology DownloadStationBot";
    fi;
}

function BOTStart()
{
    echo "[36m[1mStarting XPEnology DownloadStationBot...[0m"
    PID=`/bin/ps -ef | /bin/grep "python" | /bin/grep "DownloadStationBot.py" | /usr/bin/awk '{print $2}'`

    if [ "$PID" ]; then
        echo "XPEnology DownloadStationBot BOT Already Running"
        # exit 1
    else
        $PYTHON_PATH "$BOT_MAIN" "$CFG_PATH" &
		sleep 1
        ProcChk
    fi
    
}


function BOTStop()
{
    echo "XPEnology DownloadStationBot safe stop Trying"

    PID=`/bin/ps -ef | /bin/grep "python" | /bin/grep "DownloadStationBot.py" | /usr/bin/awk '{print $2}'`

    if [ -z "$PID" ]; then
        echo "XPEnology DownloadStationBot Already Stop"
        # exit 1
    else
        kill -9 $PID
    fi

    sleep 1
}

case "$1" in
start)
    BOTStart
    ;;
stop)
    BOTStop
    ProcChk
    ;;
restart)
    BOTStop
    ProcChk
    BOTStart
    ;;
chk)
    ProcChk
    ;;
*)
BOTStart
    #echo "Usage : `basename $0` [ start | stop | restart | chk ]"
    ;;
esac
