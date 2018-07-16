# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Thrift SAI Mcast tests
"""
import socket
import sys
from struct import pack, unpack

from switch import *

import sai_base_test
from ptf.mask import Mask

def sai_thrift_fill_l2mc_entry(addr_family, bv_id, dip_addr, sip_addr, type):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=dip_addr)
        dipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
        addr = sai_thrift_ip_t(ip4=sip_addr)
        sipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=dip_addr)
        dipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
        addr = sai_thrift_ip_t(ip6=sip_addr)
        sipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
		
    l2mc_entry = sai_thrift_l2mc_entry_t(bv_id=bv_id, type=type, source=sipaddr, destination=dipaddr)
    return l2mc_entry

def sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr, sip_addr, type):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=dip_addr)
        dipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
        addr = sai_thrift_ip_t(ip4=sip_addr)
        sipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=dip_addr)
        dipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
        addr = sai_thrift_ip_t(ip6=sip_addr)
        sipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
		
    ipmc_entry = sai_thrift_ipmc_entry_t(vr_id=vr_id, type=type, source=sipaddr, destination=dipaddr)
    return ipmc_entry

@group('mcast')
class McastIPMCIPv4XGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        default_addr = '0.0.0.0'
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_XG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, default_addr, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('mcast')
class McastIPMCIPv4SGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)

@group('mcast')
class McastIPMCIPv4SGAggTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        lag_id1 = sai_thrift_create_lag(self.client, [])
        lag_member_id1 = sai_thrift_create_lag_member(self.client, lag_id1, port2)
        lag_member_id2 = sai_thrift_create_lag_member(self.client, lag_id1, port3)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, lag_id1, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets_any(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            
            sai_thrift_remove_lag_member(self.client, lag_member_id1)
            sai_thrift_remove_lag_member(self.client, lag_member_id2)
            sai_thrift_remove_lag(self.client, lag_id1)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('mcast')
class McastIPMCIPv4SGL2MCXGVlanINF0Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        port5 = port_list[4]
        port6 = port_list[5]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id1 = 10
        vlan_id2 = 20
        vlan_id3 = 30
        vlan_id4 = 40
        grp_attr_list = []
        
        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_oid3 = sai_thrift_create_vlan(self.client, vlan_id3)
        vlan_oid4 = sai_thrift_create_vlan(self.client, vlan_id4)
       
        # vlan 10 member list
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port5, SAI_VLAN_TAGGING_MODE_TAGGED)
        
        # vlan 20 member list
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member5 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port4, SAI_VLAN_TAGGING_MODE_TAGGED)
        
        #vlan 30 member list
        vlan_member6 = sai_thrift_create_vlan_member(self.client, vlan_oid3, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member7 = sai_thrift_create_vlan_member(self.client, vlan_oid3, port4, SAI_VLAN_TAGGING_MODE_TAGGED)
        
        #vlan 40 member list
        vlan_member8 = sai_thrift_create_vlan_member(self.client, vlan_oid4, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member9 = sai_thrift_create_vlan_member(self.client, vlan_oid4, port4, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member10 = sai_thrift_create_vlan_member(self.client, vlan_oid4, port5, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member11 = sai_thrift_create_vlan_member(self.client, vlan_oid4, port6, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
       
        #create L3if ,vlan if 10
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid1, v4_enabled, v6_enabled, mac)
        #create L3if ,vlan if 20
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid2, v4_enabled, v6_enabled, mac)
        #create L3if ,vlan if 30
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid3, v4_enabled, v6_enabled, mac)
        #create L3if ,vlan if 40
        rif_id4 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid4, v4_enabled, v6_enabled, mac)

        #create L2MC member group
        l2mc_grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_member_id1_1 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id1, port1)
        l2mc_member_id1_2 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id1, port2)
        
        l2mc_grp_id2 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_member_id2_1 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id2, port1)
        l2mc_member_id2_2 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id2, port5)

        l2mc_grp_id3 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_member_id3_1 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id3, port3)
        l2mc_member_id3_2 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id3, port4)

        l2mc_grp_id4 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_member_id4_1 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id4, port5)
        l2mc_member_id4_2 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id4, port6)
        
        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '225.1.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:01:01:01'
        smac1 = '00:00:00:00:00:01'        
        type = SAI_L2MC_ENTRY_TYPE_XG        
        
        #create (*,225.1.1.1 ,Vlan 10/20/30/40) L2MC entry
        l2mc_entry1_1 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid1, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry1_1, l2mc_grp_id1) 
        l2mc_entry1_2 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid2, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry1_2, l2mc_grp_id3) 
        l2mc_entry1_3 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid3, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry1_3, l2mc_grp_id3)
        l2mc_entry1_4 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid4, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry1_4, l2mc_grp_id3) 
        
        dip_addr2 = '226.1.1.1'
        #create (*,226.1.1.1 ,Vlan 10/20/30/40) L2MC entry
        l2mc_entry2_1 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid1, dip_addr2, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry2_1, l2mc_grp_id2)
        l2mc_entry2_2 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid2, dip_addr2, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry2_2, l2mc_grp_id3)
        l2mc_entry2_3 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid3, dip_addr2, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry2_3, l2mc_grp_id3)       
        l2mc_entry2_4 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid4, dip_addr2, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry2_4, l2mc_grp_id3)
        
        dip_addr3 = '227.1.1.1'
        #create (*,227.1.1.1 ,Vlan 10/20/30/40) L2MC entry
        l2mc_entry3_1 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid1, dip_addr3, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry3_1, l2mc_grp_id1) 
        l2mc_entry3_2 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid2, dip_addr3, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry3_2, l2mc_grp_id3)       
        l2mc_entry3_3 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid3, dip_addr3, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry3_3, l2mc_grp_id3)
        l2mc_entry3_4 = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid4, dip_addr3, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry3_4, l2mc_grp_id4)
        
        #cgreat RPF member group
        rpf_grp_id = self.client.sai_thrift_create_rpf_group(grp_attr_list)
        rpf_member_id1 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id1)  
        
        #create IPMC member group5 ,and add vlanif 20/vlanif 30/vlanif 40 to group   
        ipmc_grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list) 
        ipmc_member_id1 = sai_thrift_create_ipmc_group_member(self.client, ipmc_grp_id, rif_id2)
        ipmc_member_id2 = sai_thrift_create_ipmc_group_member(self.client, ipmc_grp_id, rif_id3)
        ipmc_member_id3 = sai_thrift_create_ipmc_group_member(self.client, ipmc_grp_id, rif_id4)
        
        type = SAI_IPMC_ENTRY_TYPE_XG
        #create (*,225.1.1.1 VRF1) ipmc entry,and add group5 to entry
        ipmc_entry1 = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry1, ipmc_grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)
        #create (*,226.1.1.1 VRF1) ipmc entry,and add group5 to entry
        ipmc_entry2 = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr2, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry2, ipmc_grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)
        #create (*,227.1.1.1 VRF1) ipmc entry,and add group5 to entry
        ipmc_entry3 = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr3, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry3, ipmc_grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)

        #### L2MC Entry add new port, the port will be automatically updated to IPMC member group in SAI Implement.
        l2mc_grp_id5 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_member_id5_1 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id5, port3)
        l2mc_member_id5_2 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id5, port4)
        l2mc_member_id5_3 = sai_thrift_create_l2mc_group_member(self.client, l2mc_grp_id5, port5)
        
        attr_value = sai_thrift_attribute_value_t(oid=l2mc_grp_id5)
        attr = sai_thrift_attribute_t(id=SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID, value=attr_value)
        self.client.sai_thrift_set_l2mc_entry_attribute(l2mc_entry1_4, attr)
        
        ##### Verify port list in IPMC entry (*,225.1.1.1 VRF1)
        #inject packet to port 1, port 3 and port 4 will receive two packets with vlanid 20, two packets with vlanid 30, three packets with vlanid 40
        
        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id1)
        exp_pkt1 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id2)
        exp_pkt2 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id3)
        exp_pkt3 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id4)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_each_packet_on_each_port(self, [exp_pkt1,exp_pkt1,exp_pkt2,exp_pkt2,exp_pkt3,exp_pkt3,exp_pkt3], [2,3,2,3,2,3,4])
        finally:
            print
            self.client.sai_thrift_remove_ipmc_group_member(ipmc_member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(ipmc_member_id2)
            self.client.sai_thrift_remove_ipmc_group_member(ipmc_member_id3)
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry1)
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry2)
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry3)
            self.client.sai_thrift_remove_ipmc_group(ipmc_grp_id)
            
            self.client.sai_thrift_remove_rpf_group_member(rpf_member_id1)
            self.client.sai_thrift_remove_rpf_group(rpf_grp_id)
            
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry1_1)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry1_2)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry1_3)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry1_4)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry2_1)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry2_2)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry2_3)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry2_4)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry3_1)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry3_2)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry3_3)
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry3_4)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id1_1)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id1_2)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id2_1)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id2_2)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id3_1)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id3_2)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id4_1)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id4_2)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id5_1)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id5_2)
            self.client.sai_thrift_remove_l2mc_group_member(l2mc_member_id5_3)
            self.client.sai_thrift_remove_l2mc_group(l2mc_grp_id1)
            self.client.sai_thrift_remove_l2mc_group(l2mc_grp_id2)
            self.client.sai_thrift_remove_l2mc_group(l2mc_grp_id3)
            self.client.sai_thrift_remove_l2mc_group(l2mc_grp_id4)
            self.client.sai_thrift_remove_l2mc_group(l2mc_grp_id5)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            self.client.sai_thrift_remove_router_interface(rif_id4)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            self.client.sai_thrift_remove_vlan_member(vlan_member5)
            self.client.sai_thrift_remove_vlan_member(vlan_member6)
            self.client.sai_thrift_remove_vlan_member(vlan_member7)
            self.client.sai_thrift_remove_vlan_member(vlan_member8)
            self.client.sai_thrift_remove_vlan_member(vlan_member9)
            self.client.sai_thrift_remove_vlan_member(vlan_member10)
            self.client.sai_thrift_remove_vlan_member(vlan_member11)
            
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            self.client.sai_thrift_remove_vlan(vlan_oid3)
            self.client.sai_thrift_remove_vlan(vlan_oid4)
            
@group('mcast')
class McastIPMCIPv4SGL2MCSGVlanINF1Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        port5 = port_list[4]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        vlan_id1 = 20
        vlan_id2 = 30
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)
        rif_id4 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_SUB_PORT, port5, vlan_oid1, v4_enabled, v6_enabled, mac)
        rif_id5 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_SUB_PORT, port5, vlan_oid2, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id1)
        
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id2 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
        member_id5 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id4)
        member_id6 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id5)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id2)
        
        member_id4 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id3)
        
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port4)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt3 = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id1)
        exp_pkt4 = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id2)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_each_packet_on_each_port(self, [exp_pkt1,exp_pkt1,exp_pkt2,exp_pkt3,exp_pkt4], [1,2,3,4,4])
        finally:
            self.client.sai_thrift_remove_ipmc_group_member(member_id3)
            self.client.sai_thrift_remove_ipmc_group_member(member_id4)
            self.client.sai_thrift_remove_ipmc_group_member(member_id5)
            self.client.sai_thrift_remove_ipmc_group_member(member_id6)
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group(grp_id2)
            
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            self.client.sai_thrift_remove_router_interface(rif_id4)
            self.client.sai_thrift_remove_router_interface(rif_id5)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            
@group('mcast')
class McastIPMCIPv4SGL2MCXGVlanINF2Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        port5 = port_list[4]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        default_addr = '0.0.0.0'
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id2 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id4 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id2)
        
        type = SAI_L2MC_ENTRY_TYPE_XG
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_group_member(member_id4)
            vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)
            member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port4)
            member_id4 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets_any(self, exp_pkt, [1,2,3])
            finally:
                self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
                self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                self.client.sai_thrift_remove_l2mc_group_member(member_id3)
                self.client.sai_thrift_remove_l2mc_group(grp_id1)
                
                self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                self.client.sai_thrift_remove_ipmc_group_member(member_id4)
                self.client.sai_thrift_remove_ipmc_group(grp_id2)
                
                self.client.sai_thrift_remove_router_interface(rif_id1)
                self.client.sai_thrift_remove_router_interface(rif_id2)
                
                self.client.sai_thrift_remove_virtual_router(vr_id)
                
                self.client.sai_thrift_remove_vlan_member(vlan_member2)
                self.client.sai_thrift_remove_vlan_member(vlan_member3)
                self.client.sai_thrift_remove_vlan_member(vlan_member4)
                
                self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastIPMCIPv4SGFDBVlanINF3Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port4)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id1)
        
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id2 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
        member_id4 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id2)
        
        self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        try:
            send_packet(self, 0, str(pkt))
            verify_each_packet_on_each_port(self, [exp_pkt1,exp_pkt2,exp_pkt2], [1,2,3])
        finally:
            self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id1)
            
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id4)
            self.client.sai_thrift_remove_ipmc_group(grp_id2)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
                
@group('mcast')
class McastIPMCIPv6XGL2MCXGVlanINF4Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        default_addr = '0::0'
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        
        type = SAI_L2MC_ENTRY_TYPE_XG
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id1)
        
        type = SAI_IPMC_ENTRY_TYPE_XG
        grp_id2 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, default_addr, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id2)
        
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id1)
            
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id3)
            self.client.sai_thrift_remove_ipmc_group(grp_id2)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastIPMCIPv6XGFDBVlanINF5Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        dump_status = self.client.sai_thrift_dump_log("mcast_old.txt")
        print "dump_status = %d" % dump_status
        assert (dump_status == SAI_STATUS_SUCCESS)
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        default_addr = '0::0'
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port2)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id1)
        
        type = SAI_IPMC_ENTRY_TYPE_XG
        grp_id2 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id2, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, default_addr, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id2)
        
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
        self.client.sai_thrift_remove_l2mc_group_member(member_id2)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
                self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                self.client.sai_thrift_remove_l2mc_group(grp_id1)
                
                self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                self.client.sai_thrift_remove_ipmc_group_member(member_id3)
                self.client.sai_thrift_remove_ipmc_group(grp_id2)
                
                self.client.sai_thrift_remove_router_interface(rif_id1)
                self.client.sai_thrift_remove_router_interface(rif_id2)
                
                self.client.sai_thrift_remove_virtual_router(vr_id)
                
                self.client.sai_thrift_remove_vlan_member(vlan_member2)
                self.client.sai_thrift_remove_vlan_member(vlan_member3)
                
                self.client.sai_thrift_remove_vlan(vlan_oid)

@group('mcast')
class McastIPMCIPv4SGL2MCFDBVlanINF6Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        port5 = port_list[4]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port5, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        default_addr = '0.0.0.0'
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id1)
        
        grp_id2 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id2, port3)
        member_id4 = sai_thrift_create_l2mc_group_member(self.client, grp_id2, port4)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id2)
        
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id3 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id5 = sai_thrift_create_ipmc_group_member(self.client, grp_id3, rif_id2)
        member_id6 = sai_thrift_create_ipmc_group_member(self.client, grp_id3, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id3)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(pktlen=104,
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt2 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_each_packet_on_each_port(self, [exp_pkt1,exp_pkt1,exp_pkt2], [1,2,4])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id1)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_each_packet_on_each_port(self, [exp_pkt1,exp_pkt1,exp_pkt2], [2,3,4])
            finally:
                type = SAI_L2MC_ENTRY_TYPE_XG
                grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
                member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port2)
                member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port4)
                l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
                sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id1)
                
                self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
                self.client.sai_thrift_remove_l2mc_group_member(member_id3)
                self.client.sai_thrift_remove_l2mc_group_member(member_id4)
                self.client.sai_thrift_remove_l2mc_group(grp_id2)
                
                try:
                    send_packet(self, 0, str(pkt))
                    verify_each_packet_on_each_port(self, [exp_pkt2,exp_pkt1,exp_pkt1], [4,1,3])
                finally:
                    self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                    self.client.sai_thrift_remove_l2mc_group(grp_id1)
                    
                    self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id5)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id6)
                    self.client.sai_thrift_remove_ipmc_group(grp_id2)
                    
                    self.client.sai_thrift_remove_router_interface(rif_id1)
                    self.client.sai_thrift_remove_router_interface(rif_id2)
                    self.client.sai_thrift_remove_router_interface(rif_id3)
                    
                    self.client.sai_thrift_remove_virtual_router(vr_id)
                    
                    self.client.sai_thrift_remove_vlan_member(vlan_member2)
                    self.client.sai_thrift_remove_vlan_member(vlan_member3)
                    self.client.sai_thrift_remove_vlan_member(vlan_member4)
                    
                    self.client.sai_thrift_remove_vlan(vlan_oid)
                
@group('mcast')
class McastIPMCIPv6XGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        default_addr = '0::0'
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_XG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, default_addr, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)

@group('mcast')
class McastIPMCIPv6SGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('mcast')
class McastIPMCIPv4SGAddRemoveMemberTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)
        rif_id4 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port4, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id4)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2,3])
        finally:
            self.client.sai_thrift_remove_ipmc_group_member(member_id3)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                self.client.sai_thrift_remove_ipmc_group_member(member_id1)
                self.client.sai_thrift_remove_ipmc_group_member(member_id2)
                self.client.sai_thrift_remove_ipmc_group(grp_id)
                
                self.client.sai_thrift_remove_router_interface(rif_id1)
                self.client.sai_thrift_remove_router_interface(rif_id2)
                self.client.sai_thrift_remove_router_interface(rif_id3)
                self.client.sai_thrift_remove_router_interface(rif_id4)
                
                self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('mcast')
class McastIPMCIPv4SGUpdateActionTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DROP)
            attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_no_packet_any(self, exp_pkt, [1,2])
            finally:
                attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_FORWARD)
                attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
                self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)
                
                try:
                    send_packet(self, 0, str(pkt))
                    verify_packets(self, exp_pkt, [1,2])
                finally:
                    self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id1)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id2)
                    self.client.sai_thrift_remove_ipmc_group(grp_id)
                    
                    self.client.sai_thrift_remove_router_interface(rif_id1)
                    self.client.sai_thrift_remove_router_interface(rif_id2)
                    self.client.sai_thrift_remove_router_interface(rif_id3)
                    
                    self.client.sai_thrift_remove_virtual_router(vr_id)

@group('mcast')
class McastIPMCIPv4SGUpdateGroupTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)
        rif_id4 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port4, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=106,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=106,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, exp_pkt, [1,2])
        finally:       
            attr_value = sai_thrift_attribute_value_t(oid=grp_id)
            attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_OUTPUT_GROUP_ID, value=attr_value)
            self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                grp_id1 = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
                member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id1, rif_id3)
                member_id4 = sai_thrift_create_ipmc_group_member(self.client, grp_id1, rif_id4)
                attr_value = sai_thrift_attribute_value_t(oid=grp_id1)
                attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_OUTPUT_GROUP_ID, value=attr_value)
                self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)
                try:
                    send_packet(self, 0, str(pkt))
                    verify_packets(self, exp_pkt, [2,3])
                finally:
                    self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id1)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id2)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id3)
                    self.client.sai_thrift_remove_ipmc_group_member(member_id4)
                    self.client.sai_thrift_remove_ipmc_group(grp_id)
                    self.client.sai_thrift_remove_ipmc_group(grp_id1)
                    
                    self.client.sai_thrift_remove_router_interface(rif_id1)
                    self.client.sai_thrift_remove_router_interface(rif_id2)
                    self.client.sai_thrift_remove_router_interface(rif_id3)
                    self.client.sai_thrift_remove_router_interface(rif_id4)
                    
                    self.client.sai_thrift_remove_virtual_router(vr_id)

@group('mcast')
class McastIPMCIPv4SGRPFTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        rpf_grp_id = self.client.sai_thrift_create_rpf_group(grp_attr_list)
        rpf_member_id1 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, exp_pkt, [1,2])
        finally:    
            self.client.sai_thrift_remove_rpf_group_member(rpf_member_id1)
            rpf_member_id2 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id1)
            
            attr_value = sai_thrift_attribute_value_t(oid=rpf_grp_id)
            attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_RPF_GROUP_ID, value=attr_value)
            self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)

            # send the test packet(s)
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                self.client.sai_thrift_remove_ipmc_group_member(member_id1)
                self.client.sai_thrift_remove_ipmc_group_member(member_id2)
                self.client.sai_thrift_remove_rpf_group_member(rpf_member_id2)
                self.client.sai_thrift_remove_rpf_group(rpf_grp_id)
                self.client.sai_thrift_remove_ipmc_group(grp_id)
                
                self.client.sai_thrift_remove_router_interface(rif_id1)
                self.client.sai_thrift_remove_router_interface(rif_id2)
                self.client.sai_thrift_remove_router_interface(rif_id3)
                
                self.client.sai_thrift_remove_virtual_router(vr_id)
                
@group('mcast')
class McastIPMCIPv6SGRPFTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        rpf_grp_id = self.client.sai_thrift_create_rpf_group(grp_attr_list)
        rpf_member_id1 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=63)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, exp_pkt, [1,2])
        finally:    
            self.client.sai_thrift_remove_rpf_group_member(rpf_member_id1)
            rpf_member_id2 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id1)
            
            attr_value = sai_thrift_attribute_value_t(oid=rpf_grp_id)
            attr = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_RPF_GROUP_ID, value=attr_value)
            self.client.sai_thrift_set_ipmc_entry_attribute(ipmc_entry, attr)

            # send the test packet(s)
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
                self.client.sai_thrift_remove_ipmc_group_member(member_id1)
                self.client.sai_thrift_remove_ipmc_group_member(member_id2)
                self.client.sai_thrift_remove_rpf_group_member(rpf_member_id2)
                self.client.sai_thrift_remove_rpf_group(rpf_grp_id)
                self.client.sai_thrift_remove_ipmc_group(grp_id)
                
                self.client.sai_thrift_remove_router_interface(rif_id1)
                self.client.sai_thrift_remove_router_interface(rif_id2)
                self.client.sai_thrift_remove_router_interface(rif_id3)
                
                self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('mcast')
class McastIPMCIPv4SGGetAttrsTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print "Get ipmc member/group/entry attributes"
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        grp_attr_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_IPMC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_ipmc_group(grp_attr_list)
        member_id1 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id1)
        member_id2 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id2)
        member_id3 = sai_thrift_create_ipmc_group_member(self.client, grp_id, rif_id3)
        rpf_grp_id = self.client.sai_thrift_create_rpf_group(grp_attr_list)
        rpf_member_id1 = sai_thrift_create_rpf_group_member(self.client, rpf_grp_id, rif_id2)
        ipmc_entry = sai_thrift_fill_ipmc_entry(addr_family, vr_id, dip_addr1, sip_addr1, type)
        sai_thrift_create_ipmc_entry(self.client, ipmc_entry, grp_id, SAI_PACKET_ACTION_FORWARD, rpf_grp_id)

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_ipmc_group_member_attribute(member_id1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_IPMC_GROUP_MEMBER_ATTR_IPMC_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_IPMC_GROUP_MEMBER_ATTR_IPMC_OUTPUT_ID:
                    print "set interface id: 0x%x, get interface id: 0x%x" %(rif_id1,a.value.oid)
                    if rif_id1 != a.value.oid:
                        raise NotImplementedError()

            attrs = self.client.sai_thrift_get_ipmc_group_attribute(grp_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_IPMC_GROUP_ATTR_IPMC_OUTPUT_COUNT:
                    print "set member count: 3, get member count: %d" %a.value.u16
                    if 3 != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_IPMC_GROUP_ATTR_IPMC_MEMBER_LIST:
                    index = len(a.value.objlist.object_id_list)
                    print "group id: 0x%x, create member1: 0x%x, member2: 0x%x, member3: 0x%x" %(grp_id, member_id1,member_id2,member_id3)
                    for bp in a.value.objlist.object_id_list:
                        print "member id: 0x%x" %bp
                    if 3 != index:
                        raise NotImplementedError()

            attrs = self.client.sai_thrift_get_ipmc_entry_attribute(ipmc_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_IPMC_ENTRY_ATTR_PACKET_ACTION:
                    print "set action: forward, get action: %d" %a.value.s32
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_IPMC_ENTRY_ATTR_OUTPUT_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_IPMC_ENTRY_ATTR_RPF_GROUP_ID:
                    print "set rpf group id: 0x%x, get rpf group id: 0x%x" %(rpf_grp_id,a.value.oid)
                    if rpf_grp_id != a.value.oid:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_rpf_group_member(rpf_member_id1)
            self.client.sai_thrift_remove_rpf_group(rpf_grp_id)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)

@group('mcast')
class McastL2MCIPv4XGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        port5 = port_list[4]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)

        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port5, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        default_addr = '0.0.0.0'
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_XG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port4)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)
        
        self.client.sai_thrift_remove_l2mc_group_member(member_id2)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,3])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('mcast')
class McastL2MCIPv4SGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []
        
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastL2MCIPv6XGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV6_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        default_addr = '0::0'
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_XG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('mcast')
class McastL2MCIPv6SGTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV6_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        dip_addr1 = 'ff06::1:1'
        sip_addr1 = '3001::1'
        dmac1 = '33:33:00:01:00:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ipv6_dst=dip_addr1,
                                ipv6_src=sip_addr1,
                                ipv6_hlim=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastL2MCIPv4SGAddRemoveMemberTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port4)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2,3])
        finally:
            self.client.sai_thrift_remove_l2mc_group_member(member_id3)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
                self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                self.client.sai_thrift_remove_l2mc_group(grp_id)
                
                self.client.sai_thrift_remove_vlan_member(vlan_member1)
                self.client.sai_thrift_remove_vlan_member(vlan_member2)
                self.client.sai_thrift_remove_vlan_member(vlan_member3)
                self.client.sai_thrift_remove_vlan_member(vlan_member4)
                
                self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastL2MCIPv4XGUpdateGroupTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        default_addr = '0.0.0.0'
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_XG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, default_addr, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, exp_pkt, [1,3])
        finally:
            attr_value = sai_thrift_attribute_value_t(oid=grp_id)
            attr = sai_thrift_attribute_t(id=SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID, value=attr_value)
            self.client.sai_thrift_set_l2mc_entry_attribute(l2mc_entry, attr)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                grp_id1 = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
                member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port3)
                member_id4 = sai_thrift_create_l2mc_group_member(self.client, grp_id1, port4)
                attr_value = sai_thrift_attribute_value_t(oid=grp_id1)
                attr = sai_thrift_attribute_t(id=SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID, value=attr_value)
                self.client.sai_thrift_set_l2mc_entry_attribute(l2mc_entry, attr)
                try:
                    send_packet(self, 0, str(pkt))
                    verify_packets(self, exp_pkt, [2,3])
                finally:
                    self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id3)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id4)
                    self.client.sai_thrift_remove_l2mc_group(grp_id)
                    self.client.sai_thrift_remove_l2mc_group(grp_id1)
                    
                    self.client.sai_thrift_remove_vlan_member(vlan_member1)
                    self.client.sai_thrift_remove_vlan_member(vlan_member2)
                    self.client.sai_thrift_remove_vlan_member(vlan_member3)
                    self.client.sai_thrift_remove_vlan_member(vlan_member4)
                    
                    self.client.sai_thrift_remove_vlan(vlan_oid)

@group('mcast')
class McastL2MCIPv4SGGetAttrsTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print "Get l2mc member/group/entry attributes"
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_TAGGED)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        type = SAI_L2MC_ENTRY_TYPE_SG
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port1)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id3 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        l2mc_entry = sai_thrift_fill_l2mc_entry(addr_family, vlan_oid, dip_addr1, sip_addr1, type)
        sai_thrift_create_l2mc_entry(self.client, l2mc_entry, grp_id)

        warmboot(self.client)
        try:
            bport_oid = sai_thrift_get_bridge_port_by_port(self.client, port2)
            assert (bport_oid != SAI_NULL_OBJECT_ID)
            
            attrs = self.client.sai_thrift_get_l2mc_group_member_attribute(member_id2)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_OUTPUT_ID:
                    print "set bridge port: 0x%x, get bridge port: 0x%x" %(bport_oid,a.value.oid)
                    if bport_oid != a.value.oid:
                        raise NotImplementedError()

            attrs = self.client.sai_thrift_get_l2mc_group_attribute(grp_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_L2MC_GROUP_ATTR_L2MC_OUTPUT_COUNT:
                    print "set member count: 3, get member count: %d" %a.value.u16
                    if 3 != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_L2MC_GROUP_ATTR_L2MC_MEMBER_LIST:
                    index = len(a.value.objlist.object_id_list)
                    print "group id: 0x%x, create member1: 0x%x, member2: 0x%x, member3: 0x%x" %(grp_id, member_id1,member_id2,member_id3)
                    for bp in a.value.objlist.object_id_list:
                        print "member id: 0x%x" %bp
                    if 3 != index:
                        raise NotImplementedError()
  
            attrs = self.client.sai_thrift_get_l2mc_entry_attribute(l2mc_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_L2MC_ENTRY_ATTR_PACKET_ACTION:
                    print "set action: forward, get action: %d" %a.value.s32
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
        finally:            
            self.client.sai_thrift_remove_l2mc_entry(l2mc_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group_member(member_id3)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastMcastFdbTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)       
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastMcastFdbUpdateActionTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)       
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
        finally:
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DROP)
            attr = sai_thrift_attribute_t(id=SAI_MCAST_FDB_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_mcast_fdb_entry_attribute(mcast_fdb_entry, attr)
            
            try:
                send_packet(self, 0, str(pkt))
                verify_no_packet_any(self, exp_pkt, [1,2])
            finally:
                attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_FORWARD)
                attr = sai_thrift_attribute_t(id=SAI_MCAST_FDB_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
                self.client.sai_thrift_set_mcast_fdb_entry_attribute(mcast_fdb_entry, attr)
                
                try:
                    send_packet(self, 0, str(pkt))
                    verify_packets(self, exp_pkt, [1,2])
                finally:
                    self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                    self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                    self.client.sai_thrift_remove_l2mc_group(grp_id)
                    
                    self.client.sai_thrift_remove_vlan_member(vlan_member1)
                    self.client.sai_thrift_remove_vlan_member(vlan_member2)
                    self.client.sai_thrift_remove_vlan_member(vlan_member3)
                    
                    self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastMcastFdbUpdateGroupTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)       
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, exp_pkt, [1,2])
        finally:
            attr_value = sai_thrift_attribute_value_t(oid=grp_id)
            attr = sai_thrift_attribute_t(id=SAI_MCAST_FDB_ENTRY_ATTR_GROUP_ID, value=attr_value)
            self.client.sai_thrift_set_mcast_fdb_entry_attribute(mcast_fdb_entry, attr)
                
            try:
                send_packet(self, 0, str(pkt))
                verify_packets(self, exp_pkt, [1,2])
            finally:
                self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
                self.client.sai_thrift_remove_l2mc_group_member(member_id1)
                self.client.sai_thrift_remove_l2mc_group_member(member_id2)
                self.client.sai_thrift_remove_l2mc_group(grp_id)
                
                self.client.sai_thrift_remove_vlan_member(vlan_member1)
                self.client.sai_thrift_remove_vlan_member(vlan_member2)
                self.client.sai_thrift_remove_vlan_member(vlan_member3)
                
                self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mcast')
class McastMcastFdbGetAttrsTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print "Get mcast fdb member/group/entry attributes"
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        vlan_id = 10
        grp_attr_list = []

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)       
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        dip_addr1 = '230.255.1.1'
        sip_addr1 = '10.10.10.1'
        dmac1 = '01:00:5E:7F:01:01'
        smac1 = '00:00:00:00:00:01'
        grp_id = self.client.sai_thrift_create_l2mc_group(grp_attr_list)
        member_id1 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port2)
        member_id2 = sai_thrift_create_l2mc_group_member(self.client, grp_id, port3)
        mcast_fdb_entry = sai_thrift_mcast_fdb_entry_t(mac_address=dmac1, bv_id=vlan_oid)
        sai_thrift_create_mcast_fdb_entry(self.client, mcast_fdb_entry, grp_id)

        warmboot(self.client)
        try:
            bport_oid = sai_thrift_get_bridge_port_by_port(self.client, port2)
            assert (bport_oid != SAI_NULL_OBJECT_ID)
            
            attrs = self.client.sai_thrift_get_l2mc_group_member_attribute(member_id1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_OUTPUT_ID:
                    print "set bridge port: 0x%x, get bridge port: 0x%x" %(bport_oid,a.value.oid)
                    if bport_oid != a.value.oid:
                        raise NotImplementedError()

            attrs = self.client.sai_thrift_get_l2mc_group_attribute(grp_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_L2MC_GROUP_ATTR_L2MC_OUTPUT_COUNT:
                    print "set member count: 2, get member count: %d" %a.value.u16
                    if 2 != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_L2MC_GROUP_ATTR_L2MC_MEMBER_LIST:
                    index = len(a.value.objlist.object_id_list)
                    print "group id: 0x%x, create member1: 0x%x, member2: 0x%x" %(grp_id, member_id1,member_id2)
                    for bp in a.value.objlist.object_id_list:
                        print "member id: 0x%x" %bp
                    if 2 != index:
                        raise NotImplementedError()

            attrs = self.client.sai_thrift_get_mcast_fdb_entry_attribute(mcast_fdb_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MCAST_FDB_ENTRY_ATTR_PACKET_ACTION:
                    print "set action: forward, get action: %d" %a.value.s32
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MCAST_FDB_ENTRY_ATTR_GROUP_ID:
                    print "set group id: 0x%x, get group id: 0x%x" %(grp_id,a.value.oid)
                    if grp_id != a.value.oid:
                        raise NotImplementedError()
        finally: 
            self.client.sai_thrift_remove_mcast_fdb_entry(mcast_fdb_entry)
            self.client.sai_thrift_remove_l2mc_group_member(member_id1)
            self.client.sai_thrift_remove_l2mc_group_member(member_id2)
            self.client.sai_thrift_remove_l2mc_group(grp_id)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)