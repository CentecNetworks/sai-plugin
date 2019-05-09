echo "chip is $1"
if [ $1 ] && [ $1 == "gg" ]
then
	./saiserver -p ./goldengate/profile.ini -f ./goldengate/portmap.ini
elif [ $1 ] && [ $1 == "tm" ]
then
	./saiserver -p profile_tm.ini -f portmap.ini
else 
        ./saiserver -p profile.ini -f portmap.ini
fi
