#!/bin/bash

ARCH=$(uname -srvmo)
PCPU=$(grep 'physical id' /proc/cpuinfo | uniq | wc -l)
VCPU=$(grep processor /proc/cpuinfo | uniq | wc -l)
RAM_TOTAL=$(free -m | grep Mem | awk '{printf("%.2fG"), $2/1000.0}')
RAM_USED=$(free -m | grep Mem | awk '{printf("%.2fG"), $3/1000.0}')
RAM_PERC=$(free -k | grep Mem | awk '{printf("%.2f"), $3 / $2 * 100}')
DISK_TOTAL=$(df -h --total | grep total | awk '{print $2}')
DISK_USED=$(df -h --total | grep total | awk '{print $3}')
DISK_PERC=$(df -k --total | grep total | awk '{printf("%s%%"), $5}')
CPU_LOAD=$(top -bn1 | grep 'Cpu' | awk '{printf("%.1f%%%%"), $2 + $3 + $4}')
LAST_BOOT=$(who -b | awk '{print($3 " " $4)}')
TCP=$(grep TCP /proc/net/sockstat | awk '{print $3}')
USER_LOG=$(who | wc -l)

printf "$ARCH,$PCPU,$VCPU,$RAM_USED/$RAM_TOTAL,$RAM_PERC,\
$DISK_USED/$DISK_TOTAL,$DISK_PERC,$CPU_LOAD,$LAST_BOOT,\
$TCP,$USER_LOG"
