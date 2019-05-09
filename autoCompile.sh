#!/usr/bin/env bash

echo "Which switch chip you want to use:"
echo "1. CTC7148"
echo "2. CTC8096"
echo "3. CTC7132"
read -p "Your choice:" chipname
if [ $chipname == 1 ]; then
    chipname="duet2"
elif [ $chipname == 2 ]; then
    chipname="goldengate"
elif [ $chipname == 3 ]; then
    chipname="tsingma"
else
    echo "Must be 1, 2 or 3!"
    exit
fi


saiprojecthome="`pwd`"

if [ ! -d build ]; then
    mkdir build
fi
if [ ! -d lib/$chipname ]; then
    mkdir -p lib/$chipname
fi
cd build/
# compile SDK
read -p "Please give your SDKHOME path(absolute path):" sdkpath
if [[ ! -d $sdkpath ]];then
    echo "Please input a valid sdkpath!"
    exit
fi
cd $sdkpath
sedsdkpath=`echo $sdkpath | sed -n 's/\//\\\\\//g;p'`
read -p "Do you need to compile SDK?(yes/no)" needCompile
if [[ $needCompile == "yes" || $needCompile = "y" ]];then
     make clean targetbase=linux BOARD=linux-board ARCH=x86 ChipAgent=FALSE CHIPNAME=$chipname SUBCHIPNAME=$chipname VER=r M64=TRUE auto=yes CPU=x86 ONE_LIB=yes SO_LIB=yes
     make image targetbase=linux BOARD=linux-board ARCH=x86 ChipAgent=FALSE CHIPNAME=$chipname SUBCHIPNAME=$chipname VER=r M64=TRUE auto=yes CPU=x86 ONE_LIB=yes SO_LIB=yes CTC_CFLAGS="-Wall -Werror -O2 -g"
    if [ ! $? ];then
        echo "compile SDK fail"
    exit
    fi
fi
cp build.x86.r/lib.linux-board/libctcsdk.so $saiprojecthome/lib/$chipname/

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
    read -p "Please give your hiredis source code path(absolute path):" redispath
    sedRedisPath=`echo $redispath | sed -n 's/\//\\\\\//g;p'`
    sed -i "s/^INCLUDE_DIRECTORIES.*$/INCLUDE_DIRECTORIES\(\"$sedRedisPath\"\)/g" CMakeLists.txt
else 
    sed -i '/ADD_DEFINITIONS(-DCONFIG_DBCLIENT)/d' CMakeLists.txt
fi

# compile SAI plugin
cd build 
rm -rf *
cmake ..
make
exit
