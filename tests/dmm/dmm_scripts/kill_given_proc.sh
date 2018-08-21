#!/bin/bash

proc_name=$1
sudo pgrep $proc_name
if [ $? -eq "0" ]; then
    success=false
    sudo pkill $proc_name
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if '$proc_name' is still alive, attempt nr ${attempt}"
        sudo pgrep $proc_name
        if [ $? -eq "1" ]; then
            echo "'$proc_name' is dead"
            success=true
            break
        fi
        echo "'$proc_name' is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill '$proc_name' failed"
        sudo pkill -9 $proc_name
        echo "RC = $?"
        exit 1
    fi
else
    echo "'$proc_name' is not running"
fi

sleep 2
exit 0