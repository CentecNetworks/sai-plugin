# Overview
   The Switch Abstraction Interface(SAI) defines the API to provide a vendor-independent way of controlling forwarding elements, such as a switching ASIC, an NPU or a software switch in a uniform mann
er.

   This repository contains SAI implementation for Centec switching ASICs. Customers can configure Centec switching ASICs by SAI APIs in SONiC or other networking OS. This software release is Centec's
 contribution to the open community of its implementation of the SAI 1.3.0 as specified on the SAI Github at https://github.com/opencomputeproject/SAI,and the SAI release supports the Centec CTC8096 a
nd CTC7148.

# Features
| SAI Module     | Supported   | SAI Module     | Supported   |
|----------------|-------------|----------------|-------------|
| ACL            |     Y       | Schedulergroup |     Y       |
| Buffer         |     Y       | STP            |     Y       |
| Fdb            |     Y       | Switch         |     Y       |
| Hash           |     Y       | Tunnel         |     Y       |
| HostIntf       |     Y       | UDF            |     Y       |
| Lag            |     Y       | Vlan           |     Y       |
| Mirror         |     Y       | WRED           |     Y       |
| Multicast      |     Y       | Ipmc           |     Y       |
| Neighbor       |     Y       | Ipmcgroup      |     Y       |
| Nexthop        |     Y       | L2mc           |     Y       |
| Nexthopgroup   |     Y       | L2mcgroup      |     Y       |
| Policer        |     Y       | Mcastfdb       |     Y       |
| Port           |     Y       | Rpfgroup       |     Y       |
| QoSmaps        |     Y       | Mpls           |     Y       |
| Queue          |     Y       | Warmboot       |     Y       |
| Route          |     Y       | Segmentroute   |     N       |
| Router         |     Y       | BFD            |     Planed  |
| RouterIntf     |     Y       | TAM            |     Planed  |
| Samplepacket   |     Y       | uBurst         |     Planed  |
| Scheduler      |     Y       | Dtel           |     Planed  |

# Testing
The Centec SAI use PTF framework to do testing. The PTF Tests have more than 300 cases, include more than 250 cases from CentecNetwors, and 56 cases from official SAI project,More detail information r
efer to [PTF Tests](https://github.com/CentecNetworks/sai-plugin/wiki/PTF-Tests)

# Contact us
 Website: [http://www.centecnetworks.com]
 Issue tracker: [https://github.com/CentecNetworks/sai-plugin/issues]
 Support email: support@centecnetworks.com
 Sales email: sales@centecnetworks.com

# Release Log
## 2018-06-22
### Feauture Added:
    Support CTC7148 & CTC8096 Chips
    Support SAI 1.2.4 & V1.3
    Support Switch/Bridge/Port/Lag
    Support L2/L3
    Support L2/L3 Mcast
    Support SamplePacket/Mirror
    Support MPLS
    Support Tunnel
    Support Buffer/QosMaps/Queue/Policer/Scheduler
    Support HostInterface
    Support Warmboot
### Dependencies
 This pakage depends on Centec SDK V5.3.0

# How to compile

## 1. Preparation
- This SAI plugin requires Centec SDK support, so first step, you need to get Cnetec SDK for your switch chip.
- To get SDK, please contect Centec.

## 2. Edit CMakeLists.txt and make
We provide a compile script called ***autoCompile.sh***, run this script and fllow the prompt, you can get it.

Or you can modify the CMakeLists.txt by yoursefl, following here:
First we need to edit $SAIPROJECT\_SOURCE\_DIR/**CMakeLists.txt**, which located in this folder. With this file, cmake can generate Makefile automatically. Here we give a example, which provides a switch box with x86 CPU and Centec CTC7148(duet2) switch chip:

    SET(ARCH "board")
    SET(CHIPNAME "duet2")
    SET(SDKHOME "${SAIPROJECT_SOURCE_DIR}/ctcsdk/")

If you want ot enable warmboot feature, you will be need redis support,and set this 

    ADD_DEFINITIONS(-DCONFIG_DBCLIENT)

After this, let us enter folder ***build/***, and run these command:

    [centec@sw0 build]$ rm -rf *
    [centec@sw0 build]$ cmake ../

Then you can see we have ***Makefile*** now, and let us make it:

    [centec@sw0 build]$ ls
    app  centec  CMakeCache.txt  CMakeFiles  cmake_install.cmake  db  Makefile
    [centec@sw0 build]$ make
    Scanning dependencies of target sai
    [  2%] Building C object centec/CMakeFiles/sai.dir/src/ctc_sai_samplepacket.c.o
    [  4%] Building C object centec/CMakeFiles/sai.dir/src/ctc_sai_oid.c.o
    ...
    [ 92%] Building C object centec/CMakeFiles/sai.dir/src/ctc_sai_stp.c.o
    [ 95%] Building C object centec/CMakeFiles/sai.dir/src/ctc_sai_mcast.c.o
    Linking C shared library ../../lib/duet2/libsai.so
    [ 95%] Built target sai
    Scanning dependencies of target db
    [ 97%] Building C object db/CMakeFiles/db.dir/ctc_redis_client.c.o
    Linking C shared library ../../lib/duet2/libdb.so
    [ 97%] Built target db
    Scanning dependencies of target ctcsai
    [100%] Building C object app/CMakeFiles/ctcsai.dir/ctc_main.c.o
    Linking C executable ../ctcsai
    [100%] Built target ctcsai
    [centec@sw0 build]$ 

## 4. Get your sai-plugin
Enter into lib/chipname/ folder, you can see these files here:

    [centec@sw0 duet2]$ ll
    total 118700
    drwxr-xr-x 3 centec sdk  4096 Jul  9 17:50 .
    drwxr-xr-x 6 centec sdk  4096 Jun 11 19:03 ..
    -rwxr-xr-x 1 centec sdk 118458244 Jul  9 17:49 libctcsdk.so
    lrwxrwxrwx 1 centec sdk12 Jul  9 17:50 libdb.so -> libdb.so.1.2
    -rwxr-xr-x 1 centec sdk 70970 Jul  9 17:50 libdb.so.1
    lrwxrwxrwx 1 centec sdk10 Jul  9 17:50 libdb.so.1.2 -> libdb.so.1
    lrwxrwxrwx 1 centec sdk13 Jul  9 17:50 libsai.so -> libsai.so.1.2
    -rwxr-xr-x 1 centec sdk   2512643 Jul  9 17:50 libsai.so.1
    lrwxrwxrwx 1 centec sdk11 Jul  9 17:50 libsai.so.1.2 -> libsai.so.1
    [centec@sw0 duet2]$

These dynamic libraries are what you need.
