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
Thrift SAI interface Mirror tests
"""

import socket

from switch import *
from ptf.mask import Mask
import sai_base_test

import sys
from struct import pack, unpack

def ip6_to_integer(ip6):
    ip6 = socket.inet_pton(socket.AF_INET6, ip6)
    a, b = unpack(">QQ", ip6)
    return (a << 64) | b

def integer_to_ip6(ip6int):
    a = (ip6int >> 64) & ((1 << 64) - 1)
    b = ip6int & ((1 << 64) - 1)
    return socket.inet_ntop(socket.AF_INET6, pack(">QQ", a, b))

def ip4_to_integer(ip4):
    ip4int = int(socket.inet_aton('10.10.10.1').encode('hex'), 16)
    return ip4int

def integer_to_ip4(ip4int):
    return socket.inet_ntoa(hex(ip4int)[2:].zfill(8).decode('hex'))
    
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
    
@group('switch')
class Get_fdb_cnt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This performs Local mirroring
    We set port2 traffic to be monitored(both ingress and egress) on port1
    We send a packet from port 2 to port 3
    We expect the same packet on port 1 which is a mirror packet
    '''
    def runTest(self):
        print
        switch_init(self.client)
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac1='00:00:00:00:00:11'
        mac2='00:00:00:00:00:22'
        mac3='00:00:00:00:00:33'
        mac4='00:00:00:00:00:44'
        mac5='00:00:00:00:00:55'
        mac6='00:00:00:00:00:66'
        mac_action = SAI_PACKET_ACTION_FORWARD
        
        vlan_id=1
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)

        print "default_vlan_id:0x%x" %switch.default_vlan.vid
        print "default_vlan_oid:0x%x" %switch.default_vlan.oid
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_LEARN_DISABLE, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(switch.default_vlan.oid, attr)
        sai_thrift_flush_fdb_by_vlan(self.client, switch.default_vlan.oid)

        # Put ports under test in VLAN 2
        vlan_id1 = 10
        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_id2 = 20
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_id3 = 30
        vlan_oid3 = sai_thrift_create_vlan(self.client, vlan_id3)
        vlan_id4 = 40
        vlan_oid4 = sai_thrift_create_vlan(self.client, vlan_id4)
        vlan_id5 = 50
        vlan_oid5 = sai_thrift_create_vlan(self.client, vlan_id5)
        vlan_id6 = 60
        vlan_oid6 = sai_thrift_create_vlan(self.client, vlan_id6)
        
        sai_thrift_create_fdb(self.client, vlan_oid1, mac1, port0, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid2, mac2, port1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid3, mac3, port2, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid4, mac4, port3, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid5, mac5, port0, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid6, mac6, port1, mac_action)

        try:
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_FDB_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_FDB_ENTRY:
                    print "fdb_cnt: %d" %attribute.value.u32
                    if 6 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
                    
            sai_thrift_delete_fdb(self.client, vlan_oid5, mac5, port0)
            sai_thrift_delete_fdb(self.client, vlan_oid6, mac6, port1)
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_FDB_ENTRY:
                    print "fdb_cnt: %d" %attribute.value.u32
                    if 4 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
                    
            sai_thrift_create_fdb(self.client, vlan_oid5, mac5, port0, mac_action)
            sai_thrift_create_fdb(self.client, vlan_oid6, mac6, port1, mac_action)
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_FDB_ENTRY:
                    print "fdb_cnt: %d" %attribute.value.u32
                    if 6 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:           
            sai_thrift_delete_fdb(self.client, vlan_oid1, mac1, port0)
            sai_thrift_delete_fdb(self.client, vlan_oid2, mac2, port1)
            sai_thrift_delete_fdb(self.client, vlan_oid3, mac3, port2)
            sai_thrift_delete_fdb(self.client, vlan_oid4, mac4, port3)
            sai_thrift_delete_fdb(self.client, vlan_oid5, mac5, port0)
            sai_thrift_delete_fdb(self.client, vlan_oid6, mac6, port1)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            self.client.sai_thrift_remove_vlan(vlan_oid3)
            self.client.sai_thrift_remove_vlan(vlan_oid4)
            self.client.sai_thrift_remove_vlan(vlan_oid5)
            self.client.sai_thrift_remove_vlan(vlan_oid6)
            
@group('switch')
class Get_ipv4_route_cnt(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        dmac1 = '00:11:22:33:44:55'
        ip_addr1 = '10.10.10.1'
        ip_addr_subnet = []
        ip_mask = '255.255.255.254'
        mac = ''
        route_num = 4096

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id2)


        for i in range(route_num):
            ip_addr_subnet.append(integer_to_ip4(1+i*2))            
            sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop1)

        warmboot(self.client)
        try:
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_IPV4_ROUTE_ENTRY, SAI_SWITCH_ATTR_AVAILABLE_IPV6_ROUTE_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_IPV4_ROUTE_ENTRY :
                    print "ipv4_route_cnt: %d " %attribute.value.u32
                    if route_num != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_IPV6_ROUTE_ENTRY :
                    print "ipv6_route_cnt: %d " %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            for i in range(route_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop1)

            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)
   
@group('switch')
class Get_ipv6_route_cnt(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        dmac1 = '00:11:22:33:44:55'
        ip_addr_subnet = []
        mac = ''
        route_num = 4095

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
        nhop = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id2)

        dest_ip = '0000:5678:9abc:def0:4422:1133:5577:0000'
        ip_mask = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        dest_int = ip6_to_integer(dest_ip)
        for i in range(route_num):
            ip_addr_subnet.append(integer_to_ip6(dest_int+i))
            sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop)            

        warmboot(self.client)
        try:
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_IPV4_ROUTE_ENTRY, SAI_SWITCH_ATTR_AVAILABLE_IPV6_ROUTE_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_IPV4_ROUTE_ENTRY :
                    print "ipv4_route_cnt: %d " %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id == SAI_SWITCH_ATTR_AVAILABLE_IPV6_ROUTE_ENTRY :
                    print "ipv6_route_cnt: %d " %attribute.value.u32
                    if route_num != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            for i in range(route_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop)
            
            self.client.sai_thrift_remove_next_hop(nhop)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)
   
# only ipv4   
@group('switch')
class Get_nexthop_cnt(sai_base_test.ThriftInterfaceDataPlane):
 def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        dest_mac = []
        ip_addr = []
        ip_addr_subnet = []
        ip_mask = '255.255.255.255'
        nhop = []
        mac = ''
        next_hop_num = 1023

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        src_mac_start = ['01:22:33:44:55:', '11:22:33:44:55:', '21:22:33:44:55:', '31:22:33:44:55:', '41:22:33:44:55:', '51:22:33:44:55:', '61:22:33:44:55:', '71:22:33:44:55:', '81:22:33:44:55:', '91:22:33:44:55:', 'a1:22:33:44:55:']

        for i in range(next_hop_num):
            dest_mac.append(src_mac_start[i/99] + str(i%99).zfill(2))
            ip_addr.append(integer_to_ip4(1+i))
            ip_addr_subnet.append(integer_to_ip4(0xff0000+i))
            sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])
            nhop.append(sai_thrift_create_nhop(self.client, addr_family, ip_addr[i], rif_id2))
            sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop[i])

        warmboot(self.client)
        try:
            #for i in range(next_hop_num):
            #    pkt = simple_tcp_packet(eth_dst=router_mac,
            #                            eth_src='00:00:00:00:00:1',
            #                            ip_dst=ip_addr_subnet[i],
            #                            ip_src='192.168.8.1',
            #                            ip_id=106,
            #                            ip_ttl=64)
            #    exp_pkt = simple_tcp_packet(eth_dst=dest_mac[i],
            #                                 eth_src=router_mac,
            #                                 ip_dst=ip_addr_subnet[i],
            #                                 ip_src='192.168.8.1',
            #                                 ip_id=106,
            #                                 ip_ttl=63)
            #    print "send ip_addr = %s" %ip_addr_subnet[i]
            #    send_packet(self, 0, str(pkt))
            #    verify_packet(self, exp_pkt, 1)
            #print "packet check pass"
            
            ids_list = [ SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEXTHOP_ENTRY,  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEXTHOP_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEXTHOP_ENTRY :
                    print "ipv4_nexthop_cnt: %d " %attribute.value.u32
                    if next_hop_num != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEXTHOP_ENTRY :
                    print "ipv6_nexthop_cnt: %d " %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            for i in range(next_hop_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop[i])
                self.client.sai_thrift_remove_next_hop(nhop[i])
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('switch')
class Get_ipv4_neighbor_cnt(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        dest_mac = []
        ip_addr = []
        mac = ''
        neighbor_num = 1023

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        src_mac_start = ['01:22:33:44:55:', '11:22:33:44:55:', '21:22:33:44:55:', '31:22:33:44:55:', '41:22:33:44:55:', '51:22:33:44:55:', '61:22:33:44:55:', '71:22:33:44:55:', '81:22:33:44:55:', '91:22:33:44:55:', 'a1:22:33:44:55:']

        for i in range(neighbor_num):
            dest_mac.append(src_mac_start[i/99] + str(i%99).zfill(2))
            ip_addr.append(integer_to_ip4(1+i))
            sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])


        warmboot(self.client)
        try:
            #for i in range(neighbor_num):
            #    pkt = simple_tcp_packet(eth_dst=router_mac,
            #                            eth_src='00:00:00:00:00:1',
            #                            ip_dst=ip_addr[i],
            #                            ip_src='192.168.8.1',
            #                            ip_id=106,
            #                            ip_ttl=64)
            #    exp_pkt = simple_tcp_packet(eth_dst=dest_mac[i],
            #                                 eth_src=router_mac,
            #                                 ip_dst=ip_addr[i],
            #                                 ip_src='192.168.8.1',
            #                                 ip_id=106,
            #                                 ip_ttl=63)
            #    print "send ip_addr = %s" %ip_addr[i]
            #    send_packet(self, 0, str(pkt))
            #    verify_packet(self, exp_pkt, 1)
            #print "packet check pass"
            
            ids_list = [ SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEIGHBOR_ENTRY,  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEIGHBOR_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEIGHBOR_ENTRY :
                    print "ipv4_neighbor_cnt: %d " %attribute.value.u32
                    if neighbor_num != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEIGHBOR_ENTRY :
                    print "ipv6_neighbor_cnt: %d " %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
                    
        finally:
            for i in range(neighbor_num):
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

@group('switch')
class Get_ipv6_neighbor_cnt(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        dest_mac = []
        ip_addr = []
        mac = ''
        neighbor_num = 1023

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        src_mac_start = ['01:22:33:44:55:', '11:22:33:44:55:', '21:22:33:44:55:', '31:22:33:44:55:', '41:22:33:44:55:', '51:22:33:44:55:', '61:22:33:44:55:', '71:22:33:44:55:', '81:22:33:44:55:', '91:22:33:44:55:', 'a1:22:33:44:55:']
        dest_ip = '1234:5678:9abc:def0:4422:1133:5577:0000'
        dest_int = ip6_to_integer(dest_ip)
        for i in range(neighbor_num):
            dest_mac.append(src_mac_start[i/99] + str(i%99).zfill(2))
            ip_addr.append(integer_to_ip6(dest_int+i))
            sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])

        warmboot(self.client)
        try:
            #for i in range(neighbor_num):
            #    pkt = simple_tcpv6_packet(eth_dst=router_mac,
            #                              eth_src='00:00:00:00:00:1',
            #                              ipv6_dst=ip_addr[i],
            #                              ipv6_src='2000:bbbb::1',
            #                              ipv6_hlim=64)
            #    exp_pkt = simple_tcpv6_packet(eth_dst=dest_mac[i],
            #                                  eth_src=router_mac,
            #                                  ipv6_dst=ip_addr[i],
            #                                  ipv6_src='2000:bbbb::1',
            #                                  ipv6_hlim=63)
            #
            #
            #    print "send ip_addr = %s" %ip_addr[i]
            #    send_packet(self, 0, str(pkt))
            #    verify_packet(self, exp_pkt, 1)
            #print "packet check pass"
            
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEIGHBOR_ENTRY,  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEIGHBOR_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV4_NEIGHBOR_ENTRY :
                    print "ipv4_neighbor_cnt: %d " %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPV6_NEIGHBOR_ENTRY :
                    print "ipv6_neighbor_cnt: %d " %attribute.value.u32
                    if neighbor_num != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            for i in range(neighbor_num):
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)


@group('switch')
class Get_nexthop_group_cnt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This performs Local mirroring
    We set port2 traffic to be monitored(both ingress and egress) on port1
    We send a packet from port 2 to port 3
    We expect the same packet on port 1 which is a mirror packet
    '''
    def runTest(self):
        print
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop_group1 = sai_thrift_create_next_hop_group(self.client)

        warmboot(self.client)
        try:
            ids_list = [ SAI_SWITCH_ATTR_AVAILABLE_NEXT_HOP_GROUP_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_NEXT_HOP_GROUP_ENTRY :
                    print "nexthop_group_cnt: %d " %attribute.value.u32
                    if 1 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            self.client.sai_thrift_remove_next_hop_group(nhop_group1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)
@group('switch')
class Get_nexthop_group_member_cnt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This performs Local mirroring
    We set port2 traffic to be monitored(both ingress and egress) on port1
    We send a packet from port 2 to port 3
    We expect the same packet on port 1 which is a mirror packet
    '''
    def runTest(self):
        print
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        dmac2 = '00:11:22:33:44:56'
        sai_thrift_create_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif2)
        print "nhop1 = 0x%x" %nhop1
        print "nhop2 = 0x%x" %nhop2
        nhop_group1 = sai_thrift_create_next_hop_group(self.client)
        print "nhop_group1 = 0x%x" %nhop_group1
        nhop_gmember1 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop1)
        nhop_gmember2 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop2)
        print "nhop_gmember1 = 0x%x" %nhop_gmember1
        print "nhop_gmember2 = 0x%x" %nhop_gmember2

        warmboot(self.client)
        try:
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_NEXT_HOP_GROUP_MEMBER_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_NEXT_HOP_GROUP_MEMBER_ENTRY :
                    print "nexthop_group_member_cnt: %d" %attribute.value.u32
                    if 2 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"

        finally:
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember2)

            self.client.sai_thrift_remove_next_hop_group(nhop_group1)

            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)

            sai_thrift_remove_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)

            self.client.sai_thrift_remove_router_interface(rif1)
            self.client.sai_thrift_remove_router_interface(rif2)

            self.client.sai_thrift_remove_virtual_router(vr_id)
            
            
@group('switch')
class Get_l2mc_cnt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This performs Local mirroring
    We set port2 traffic to be monitored(both ingress and egress) on port1
    We send a packet from port 2 to port 3
    We expect the same packet on port 1 which is a mirror packet
    '''
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
        type = SAI_L2MC_ENTRY_TYPE_SG
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
            #send_packet(self, 0, str(pkt))
            #verify_packets(self, exp_pkt, [1,3])
            
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_L2MC_ENTRY , SAI_SWITCH_ATTR_AVAILABLE_IPMC_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_L2MC_ENTRY  :
                    print "l2mc_entry_cnt: %d" %attribute.value.u32
                    if 1 != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPMC_ENTRY  :
                    print "ipmc_entry_cnt: %d" %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
                                
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
            
@group('switch')
class Get_ipmc_cnt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This performs Local mirroring
    We set port2 traffic to be monitored(both ingress and egress) on port1
    We send a packet from port 2 to port 3
    We expect the same packet on port 1 which is a mirror packet
    '''
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
            #send_packet(self, 0, str(pkt))
            #verify_packets(self, exp_pkt, [1,2])
            
            ids_list = [SAI_SWITCH_ATTR_AVAILABLE_L2MC_ENTRY , SAI_SWITCH_ATTR_AVAILABLE_IPMC_ENTRY]
            switch_attr_list = self.client.sai_thrift_get_switch_attribute(ids_list)
            attr_list = switch_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_L2MC_ENTRY  :
                    print "l2mc_entry_cnt: %d" %attribute.value.u32
                    if 0 != attribute.value.u32:
                        raise NotImplementedError()
                if attribute.id ==  SAI_SWITCH_ATTR_AVAILABLE_IPMC_ENTRY  :
                    print "ipmc_entry_cnt: %d" %attribute.value.u32
                    if 1 != attribute.value.u32:
                        raise NotImplementedError()
                else:
                    print "unknown switch attribute"
        finally:
            self.client.sai_thrift_remove_ipmc_entry(ipmc_entry)
            self.client.sai_thrift_remove_ipmc_group_member(member_id1)
            self.client.sai_thrift_remove_ipmc_group_member(member_id2)
            self.client.sai_thrift_remove_ipmc_group(grp_id)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)
            
            self.client.sai_thrift_remove_virtual_router(vr_id)
            
@group('switch')
class Fdb_unicast_miss_pkt_action(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 1 -> ptf_intf 2, ptf_intf 3 (local mirror)"
        print "Sending packet ptf_intf 2 -> ptf_intf 1, ptf_intf 3 (local mirror)"

        switch_init(self.client)
        vlan_id = 10
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac3 = '00:22:22:22:22:33'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, port1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)
        
        self.client.sai_thrift_clear_cpu_packet_info()

        pkt1 = simple_tcp_packet(eth_dst=mac2,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            ip_id=102,
            ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac2,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            dl_vlan_enable=True,
            vlan_vid=10,
            ip_id=102,
            ip_ttl=64,
            pktlen=104)
            
        pkt2 = simple_tcp_packet(eth_dst=mac3,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            ip_id=102,
            ip_ttl=64)
        exp_pkt2 = simple_tcp_packet(eth_dst=mac3,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            dl_vlan_enable=True,
            vlan_vid=10,
            ip_id=102,
            ip_ttl=64,
            pktlen=104)
                
        try:
            # step 1
            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [2])   # go through: sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)
            
            time.sleep(1)            
            # step 2
            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt2))
            verify_each_packet_on_each_port(self, [exp_pkt2, exp_pkt2], [2, 3])  # go through: fdb default action, flooding in vlan

            time.sleep(1)
            # step 3
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_TRAP)  #  /** This is a combination of SAI packet action COPY and DROP. */
            attr = sai_thrift_attribute_t(id=SAI_SWITCH_ATTR_FDB_UNICAST_MISS_PACKET_ACTION , value=attr_value)
            self.client.sai_thrift_set_switch_attribute(attr)  

            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt2))
            verify_no_packet(self, exp_pkt2, 2)   #  /** This is a combination of SAI packet action COPY and DROP. */
            verify_no_packet(self, exp_pkt2, 3)
            
            ret = self.client.sai_thrift_get_cpu_packet_count()
            print "receive rx packet: %d" %ret.data.u16
            if ret.data.u16 != 1:
                raise NotImplementedError()
                
            attrs = self.client.sai_thrift_get_cpu_packet_attribute(0)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_HOSTIF_PACKET_ATTR_INGRESS_PORT:
                    print "ingress port: 0x%lx" %a.value.oid
                    if port1 != a.value.oid:
                        raise NotImplementedError()
            
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2) 

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('switch')
class Fdb_multicast_miss_pkt_action(sai_base_test.ThriftInterfaceDataPlane):
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
        dip_addr2 = '230.255.1.2'
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
        
        self.client.sai_thrift_clear_cpu_packet_info()

        # send the test packet(s)
        pkt1 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt1 = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr1,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
                                
        pkt2 = simple_tcp_packet(eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr2,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        exp_pkt2 = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=smac1,
                                ip_dst=dip_addr2,
                                ip_src=sip_addr1,
                                ip_id=105,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id)
        warmboot(self.client)
        try:
        # step1
            #send_packet(self, 0, str(pkt1))         # known muticast
            #verify_packets(self, exp_pkt1, [1,3])   # go through: muticast group
         
        # step2         
            #send_packet(self, 0, str(pkt2))         # unknown muticast
            #verify_each_packet_on_each_port(self, [exp_pkt2, exp_pkt2, exp_pkt2 ], [1, 3, 4])  # go through: fdb muticast default action, flooding in vlan
            #verify_packets(self, exp_pkt2, [1,3,4])   # go through: muticast group
            #verify_packet(self, exp_pkt2, 1) 
            #verify_packet(self, exp_pkt2, 3) 
            #verify_packet(self, exp_pkt2, 4) 
            
            #verify_each_packet_on_each_port(self, [exp_pkt2, exp_pkt2], [1, 3])  # go through: fdb muticast default action, flooding in vlan
            
        # step3  switch set 
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_TRAP)  #  /** This is a combination of SAI packet action COPY and DROP. */
            attr = sai_thrift_attribute_t(id=SAI_SWITCH_ATTR_FDB_MULTICAST_MISS_PACKET_ACTION , value=attr_value)
            self.client.sai_thrift_set_switch_attribute(attr)
            
            send_packet(self, 0, str(pkt2))         # unknown muticast
            verify_no_packet(self, exp_pkt2, 1)
            verify_no_packet(self, exp_pkt2, 3)
            verify_no_packet(self, exp_pkt2, 4)
            
            ret = self.client.sai_thrift_get_cpu_packet_count()
            print "receive rx packet: %d" %ret.data.u16
            if ret.data.u16 != 1:
                raise NotImplementedError()
                
            attrs = self.client.sai_thrift_get_cpu_packet_attribute(0)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_HOSTIF_PACKET_ATTR_INGRESS_PORT:
                    print "ingress port: 0x%lx" %a.value.oid
                    if port1 != a.value.oid:
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
            print "clean config done"
            
@group('switch')
class Fdb_broadcast_miss_pkt_action(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 1 -> ptf_intf 2, ptf_intf 3 (local mirror)"
        print "Sending packet ptf_intf 2 -> ptf_intf 1, ptf_intf 3 (local mirror)"

        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 20
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]

        dst_mac = 'FF:FF:FF:FF:FF:FF'
        mac1 = '12:34:56:78:9a:bc'
        mac_action = SAI_PACKET_ACTION_FORWARD

        #vlan_id1
        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_member1_0 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port0, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member1_1 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member1_2 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member1_3 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id1)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port0, attr)
        
        #vlan_id2
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_member2_0 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port0, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2_1 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2_2 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2_3 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id2)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb(self.client, vlan_oid1, dst_mac, port3, mac_action)

        pkt1 = simple_tcp_packet(eth_dst=dst_mac,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            ip_id=102,
            ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=dst_mac,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            dl_vlan_enable=True,
            vlan_vid=vlan_id1,
            ip_id=102,
            ip_ttl=64,
            pktlen=104)
         
         
        pkt2 = simple_tcp_packet(eth_dst=dst_mac,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            ip_id=102,
            ip_ttl=64)
        exp_pkt2 = simple_tcp_packet(eth_dst=dst_mac,
            eth_src=mac1,
            ip_dst='10.0.0.1',
            ip_src='192.168.0.1',
            dl_vlan_enable=True,
            vlan_vid=vlan_id2,
            ip_id=102,
            ip_ttl=64,
            pktlen=104)
                
        try:
            # step 1
            #print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            #send_packet(self, 0, str(pkt1))
            #verify_packet(self, exp_pkt1, 3)   # sai_thrift_create_fdb(self.client, vlan_oid, dst_mac, port3, mac_action)
            #
            #time.sleep(1)
            
            # step 2 
            #print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            #send_packet(self, 1, str(pkt2))
            #verify_packet(self, exp_pkt2, 0)   # sai_thrift_create_fdb(self.client, vlan_oid, dst_mac, port3, mac_action)
            #verify_each_packet_on_each_port(self, [exp_pkt2, exp_pkt2, exp_pkt2], [0, 2, 3])  # go through: fdb broadcast action, flooding in vlan_id2
            #verify_packets(self, exp_pkt2, [0, 2, 3])   # sai_thrift_create_fdb(self.client, vlan_oid, dst_mac, port3, mac_action)

            #time.sleep(1)
            
            # step 3
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_TRAP)  #  /** This is a combination of SAI packet action COPY and DROP. */
            attr = sai_thrift_attribute_t(id=SAI_SWITCH_ATTR_FDB_BROADCAST_MISS_PACKET_ACTION , value=attr_value)
            self.client.sai_thrift_set_switch_attribute(attr)
                
            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            self.client.sai_thrift_clear_cpu_packet_info()
            send_packet(self, 1, str(pkt2))

            time.sleep(5)
            
            verify_no_packet(self, exp_pkt2, 0)   #  /** This is a combination of SAI packet action COPY and DROP. */
            verify_no_packet(self, exp_pkt2, 2)   #  /** This is a combination of SAI packet action COPY and DROP. */
            verify_no_packet(self, exp_pkt2, 3)
            
            ret = self.client.sai_thrift_get_cpu_packet_count()
            print "receive rx packet: %d" %ret.data.u16
            #if ret.data.u16 != 1:
            if ret.data.u16 < 1:
                raise NotImplementedError()
                
            #attrs = self.client.sai_thrift_get_cpu_packet_attribute(0)
            #print "success to get packet attribute"
            #for a in attrs.attr_list:
            #    if a.id == SAI_HOSTIF_PACKET_ATTR_INGRESS_PORT:
            #        print "ingress port: 0x%lx" %a.value.oid
            #        if port1 != a.value.oid:
            #            raise NotImplementedError()
               
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid1, dst_mac, port3)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port0, attr)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1_0)
            self.client.sai_thrift_remove_vlan_member(vlan_member1_1)
            self.client.sai_thrift_remove_vlan_member(vlan_member1_2)
            self.client.sai_thrift_remove_vlan_member(vlan_member1_3)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member2_0)
            self.client.sai_thrift_remove_vlan_member(vlan_member2_1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2_2)
            self.client.sai_thrift_remove_vlan_member(vlan_member2_3)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            print "clean config done"
