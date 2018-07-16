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
We provide a compile script called ***autoCompile.sh***, run this script and follow the prompt, you can get it.

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
  

## 4. Get your sai-plugin
Enter into lib/chipname/ folder, you can see these files here:
    [centec@sw0 duet2]$ ll
    libctcsdk.so libdb.so.1 libsai.so.1
  

