# Overview
   The Switch Abstraction Interface(SAI) defines the API to provide a vendor-independent way of controlling forwarding elements, such as a switching ASIC, an NPU or a software switch in a uniform manner.

   This repository contains SAI implementation for Centec switching ASICs. Customers can configure Centec switching ASICs by SAI APIs in SONiC or other networking OS. This software release is Centec's contribution to the open community of its implementation of the SAI 1.3.0 as specified on the SAI Github at https://github.com/opencomputeproject/SAI,and the SAI release supports the Centec CTC8096 and CTC7148.

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
Centec support PTF framework, and add more than 300 case,more detail information refer to [PTF Tests](https://github.com/CentecNetworks/sai-plugin/wiki/PTF-Tests)

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

