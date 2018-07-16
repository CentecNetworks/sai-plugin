#!/usr/bin/env bash

echo "Which switch chip you want to use:"
echo "1. CTC7148"
echo "2. CTC8096"
read -p "Your choice:" chipname
if [ $chipname == 1 ]; then
    chipname="duet2"
elif [ $chipname == 2 ]; then
    chipname="goldengate"
else
    echo "Must be 1 or 2!"
    exit
fi


saiprojecthome="`pwd`"

if [ ! -d build ]; then
    mkdir build
fi
cd build/
# compile SDK
read -p "Please give your SDKHOME path:" sdkpath
if [[ ! -d $sdkpath ]];then
    echo "Please input a valid sdkpath!"
    exit
fi
cd $sdkpath
sedsdkpath=`echo $sdkpath | sed -n 's/\//\\\\\//g;p'`
read -p "Do you need to compile SDK?(yes/no)" needCompile
if [[ $needCompile == "yes" || $needCompile = "y" ]];then
    make clean
    make CHIPNAME=$chipname SUBCHIPNAME=$chipname targetbase=linux BOARD=linux-board ARCH=x86 auto=yes cpp=no  ChipAgent=FALSE M64=TRUE VER=r ONE_LIB=yes SO_LIB=yes
    if [ ! $? ];then
        echo "compile SDK fail"
    exit
    fi
fi
cp build.x86.d/lib.linux-board/libctcsdk.so $saiprojecthome/lib/$chipname/

# modify CMakeLists.txt
cd $saiprojecthome
sed -i "s/^SET(CHIPNAM.*$/SET\(CHIPNAME\ \"$chipname\"\)/g" CMakeLists.txt
sed -i "s/^SET(SDKHOME.*$/SET\(SDKHOME\ \"$sedsdkpath\"\)/g" CMakeLists.txt

read -p "Do you want to enable warmboot feature?(yes/no)" answer
if [[ ($answer == "yes" || $answer == "y") && (! -d $saiprojecthome/lib/redis/) ]];then 
    echo "Must have redis libraries in $saiprojecthome/lib/redis/"
    exit
elif [[ $answer == "yes" || $answer == "y" ]];then
    if [ ! `grep "ADD_DEFINITIONS(-DCONFIG_DBCLIENT)" CMakeLists.txt` ];then
        firstline=`cat -n CMakeLists.txt  |grep "ADD_DEFINITIONS" | awk '{print $1}'| sed -n '1p'`
        sed -i "$firstline a\ADD_DEFINITIONS(-DCONFIG_DBCLIENT)" CMakeLists.txt
    fi
else 
    sed -i '/ADD_DEFINITIONS(-DCONFIG_DBCLIENT)/d' CMakeLists.txt
fi

# compile SAI plugin
cd build 
rm -rf *
cmake ..
make
exit
