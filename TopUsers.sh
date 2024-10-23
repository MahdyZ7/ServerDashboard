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


for user in $users
do
    cpu_usage=$(get_cpu_usage $user)
    memory_usage=$(get_memory_usage $user)
    disk_usage=$(get_disk_usage $user)

    printf  "%s %s %s %s\n" "$user" "$cpu_usage" "$memory_usage" "$disk_usage"
done | sort -k2,2rn -k3,3rn -k4,4rn

