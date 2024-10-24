#!/bin/bash

# Function to get CPU time for a user
get_cpu_usage() {
    ps -u $1 -o %cpu= 2> /dev/null| awk '{sum+=$1} END {if (sum == 0) {print 0} else {print sum}}' 
	#	top -bn1 -u $1 | tail -n +6|  awk '{sum+=$9} END {if (sum == 0) {print 0} else {print sum}}'
	#	ps -u $1 -o %cpu= | awk '{sum+=$1} END {if (sum == 0) {print 0} else {print sum}}'
}

get_memory_usage(){
	ps -u $1 -o %mem= 2> /dev/null| awk '{sum+=$1} END {if (sum == 0) {print 0} else {print sum}}'
	#	top -bn1 -u $1 | tail -n +6|  awk '{sum+=$9} END {if (sum == 0) {print 0} else {print sum}}'
	#	ps -u $1 -o %mem= | awk '{sum+=$1} END {if (sum == 0) {print 0} else {print sum}}'
}

# Function to get disk space usage for a user
get_disk_usage() {
    if [ $(id -u) = 0 ]; then
    	du -sb /home/$1 2> /dev/null | awk '{printf("%.2f"), $1/1000000000}'
	else
		echo nan
	fi
}

# Get all users
users=$(ls /home/)




ARCH=$(uname -srvmo)
OS=$(cat /etc/system-release | awk '{printf("%s %s %s %s", $1, $2, $7, $8)}')
PCPU=$(grep 'physical id' /proc/cpuinfo | uniq | wc -l)
VCPU=$(grep processor /proc/cpuinfo | uniq | wc -l)
RAM_TOTAL=$(free -m | grep Mem | awk '{printf("%.2fG"), $2/1024.0}')
RAM_USED=$(free -m | grep Mem | awk '{printf("%.2fG"), $3/1024.0}')
RAM_PERC=$(free -k | grep Mem | awk '{printf("%.2f%%%%"), $3 / $2 * 100}')
DISK_TOTAL=$(df -k -l --total | grep total | awk '{print $2}')
DISK_USED=$(df -k -l --total | grep total | awk '{print $3}')
DISK_PERC=$(df -k -l --total | grep total | awk '{printf("%s%%"), $5}')
CPU_LOAD=$(top -bn1 | grep 'Cpu' | awk '{printf("%.1f%%%%"), $2 + $3 + $4}')
LAST_BOOT=$(who -b | awk '{print($3 " " $4)}')
TCP=$(grep TCP /proc/net/sockstat | awk '{print $3}')
USER_LOG=$(who | wc -l)

printf "
	------------------------------------------------
	Architecture	: $ARCH
	System os	: $OS
	Physical CPUs	: $PCPU
	Virtual CPUs	: $VCPU
	Memory Usage	: $RAM_USED/$RAM_TOTAL ($RAM_PERC)
	Disk Usage	: $DISK_USED/$DISK_TOTAL ($DISK_PERC)
	CPU Load	: $CPU_LOAD
	Last Boot	: $LAST_BOOT
	TCP Connections	: $TCP established
	Users logged	: $USER_LOG
	------------------------------------------------\n"

printf "\t%-10s %-10s %-10s %-10s\n" "User" "CPU %" "Memory %" "Disk Usage" 
printf "\t%-10s %-10s %-10s %-10s\n" "-----" "--------" "--------" "--------"

for user in $users
do
    cpu_usage=$(get_cpu_usage $user)
    memory_usage=$(get_memory_usage $user)
    disk_usage=$(get_disk_usage $user)

    printf  "\t%-10s %-10s %-10s %-10s\n" "$user" "$cpu_usage" "$memory_usage" "$disk_usage"
done | sort -k2,2rn -k3,3rn -k4,4rn

