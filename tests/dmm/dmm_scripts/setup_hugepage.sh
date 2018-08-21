#!/bin/bash -x

# check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
hugepageFree=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/free_hugepages)

if [ ${SYS_HUGEPAGE} -lt 1536 ] || [ $hugepageFree -eq 0 ]; then
    MOUNT=$(mount | grep /mnt/nstackhuge)
    count=$(mount | grep /mnt/nstackhuge | wc -l)

    while [ "${MOUNT}" != "" ] || [ "${count}" -ne 0 ]
    do
        sudo umount /mnt/nstackhuge
        sleep 1
        MOUNT=$(mount | grep /mnt/nstackhuge)
        count=$[$count -1]
    done

    sock_count=$(lscpu | grep 'Socket(s):' | head -1 | awk '{print $2}')
    ls -l /sys/devices/system/node/

    while [ "${sock_count}" -ne 0 ]
    do
        sock_count=$[$sock_count - 1]
        echo 1536 | sudo tee /sys/devices/system/node/node"$sock_count"/hugepages/hugepages-2048kB/nr_hugepages
    done

    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
    test $? -eq 0 || exit 1
else
    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
fi

cat /proc/meminfo
exit 0
