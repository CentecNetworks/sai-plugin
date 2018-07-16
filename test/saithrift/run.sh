#!/bin/bash

help() {
echo "Please run this script like:"
echo "./run.sh -c gg ctc"
echo "./run.sh --chip d2 sai"
echo "./run.sh -h"
echo "./run.sh --help"
echo "./run.sh"
echo "Default use duet2"
exit
}

ARGS=`getopt -o c:h -l "chip:,help" -- "$@"`
if [ $? != 0 ]
then
    help
fi
eval set --"${ARGS}"
while true
do
    case "$1" in
        -c|--chip)
         if [ $2 == "goldengate" ] || [ $2 == "gg" ]
         then
             chipname="goldengate";
         elif [ $2 == "duet2" ] || [ $2 == "dt2" ] || [ $2 == "d2" ]
         then
             chipname="duet2";
         else
             help
         fi
         shift 2
         ;;
        -h|--help)
         help;
         shift
         ;;
         --)
         shift
         break
         ;;
    esac
done
if [ -z $chipname ]
then 
     chipname="duet2";
fi
pid=""
run_one=0
grep_file="tests/*"
if [ ! -z "$@" ]
then
	if [ "$@" = "ctc" ]
		then
		grep_file="tests/ctc_*"
	elif [ "$@" = "sai" ]
	then
		grep_file="tests/sai*"
	elif [[ "$@" ==  *.* ]]
		then
		run_one=1
	else 
		grep_file="tests/"$@"*"
	fi
fi

echo "*************************Now we run $chipname cases*************************"

if [ -z $chipname ]
then
     chipname="duet2"
fi

portmap_profile="port_map_file='default_interface_to_front_map.ini';chipname='$chipname'"
interface_list="--interface "'0@eth0'" --interface "'1@eth1'" --interface "'2@eth2'" --interface "'3@eth3'" --interface "'4@eth4'" --interface "'5@eth5'" --interface "'6@eth6'" --interface "'7@eth7'"  --interface "'8@eth8'" --interface "'9@eth9'" --interface "'10@eth10'" --interface "'11@eth11'" --interface "'12@eth12'" --interface "'13@eth13'" --interface "'14@eth14'" --interface "'15@eth15'""

if [ $run_one = 1 ]
	then
	ptf --test-dir tests $1 $interface_list -t $portmap_profile
else
	grep -E "^class" $grep_file | sed -n -e 's/tests\///' -e 's/\.py//' -e 's/class *//' -e 's/:/./' -e 's/(.*$//p' > test_case.txt 
	
	time=`date +"%Y-%m-%d-%H-%M-%S"`
        if [ ! -d "./test_log" ]
        then
            mkdir test_log
        fi
	log_path="./test_log/log_${time}.txt"
	nopass_log="./test_log/nopass_log_${time}.txt"
        report="./test_log/test_report_${time}.csv"
        echo "case," >> $report
	echo "test begin>>>"
	for str in `cat test_case.txt`
		do
		ptf --test-dir tests $str $interface_list -t $portmap_profile >> $log_path 2>&1
                if [ $? == 0 ]
                then 
                      echo "$str,PASS" >> $report
                      echo -e "$str                                                    \t\tPASS"
                else
                      echo "$str,FAIL">> $report
                      echo -e "$str                                                     \t\t\033[40;31;1mFAIL \033[0m"
                fi
		pid=`pgrep saiserver -u root`
		if [[ "$pid" == "" ]]
			then
			echo "SAI Server Break Interrupt! Please Restart Server!"
			break
		fi
		done
	
	grep -E "^ERROR:" $log_path | sed -n  -e 's/ERROR: *//p' >> $nopass_log
	grep -E "^FAIL:" $log_path | sed -n  -e 's/FAIL: *//p' >> $nopass_log
	
	echo "<<<test end"
	echo "log path:"$log_path
	echo "nopass log path:"$nopass_log
fi
