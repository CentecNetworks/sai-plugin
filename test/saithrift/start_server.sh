if [ $1 ] && [ $1 == "gg" ]
then
	./saiserver -p ./goldengate/profile.ini -f ./goldengate/portmap.ini
else
	./saiserver -p profile.ini -f portmap.ini
fi
