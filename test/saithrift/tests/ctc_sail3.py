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
Thrift SAI interface L3 tests
"""
import socket
import sys
from struct import pack, unpack

from switch import *

import sai_base_test
from ptf.mask import Mask

@group('l3')
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

class L3VirtualRouterCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Virtual Router Create test. Verify v4_enabled and v6_enabled. 
        Steps:
        1. create vritual router with v4_enabled and v6_enabled
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V4_STATE:
                    print "set v4_enabled = %d" %v4_enabled
                    print "get v4_enabled = %d" %a.value.booldata
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V6_STATE:
                    print "set v6_enabled = %d" %v6_enabled
                    print "get v6_enabled = %d" %a.value.booldata
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3VirtualRouterRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Virtual Router Remove test. 
        Steps:
        1. create vritual router
        2. remove vritual router
        3. get attribute and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            self.client.sai_thrift_remove_virtual_router(vr_id)
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
        finally:
            print "Success!"

class L3VirtualRouterSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Virtual Router Remove test. 
        Steps:
        1. create vritual router
        2. get attribute
        4. set attribute
        5. get attribute
        6. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 0
        v6_enabled = 0
        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
                
        warmboot(self.client)
        try:
            print "=======first get attr again======="
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V4_STATE:
                    print "set v4_enabled = %d" %v4_enabled
                    print "get v4_enabled = %d" %a.value.booldata
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V6_STATE:
                    print "set v6_enabled = %d" %v6_enabled
                    print "get v6_enabled = %d" %a.value.booldata
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_SRC_MAC_ADDRESS:
                    print "set router_mac = %s" %router_mac
                    print "get router_mac = %s" %a.value.mac
                    if router_mac != a.value.mac:
                        raise NotImplementedError()

            print "======set and get attr again======"
            v4_enabled = 1
            v6_enabled = 1
            vr_router_mac = "aa:bb:cc:dd:ee:ff"
            attr_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
            attr = sai_thrift_attribute_t(id=SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V4_STATE, value=attr_value)
            self.client.sai_thrift_set_virtual_router_attribute(vr_id, attr)
            attr_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
            attr = sai_thrift_attribute_t(id=SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V6_STATE, value=attr_value)
            self.client.sai_thrift_set_virtual_router_attribute(vr_id, attr)
            attr_value = sai_thrift_attribute_value_t(mac=vr_router_mac)
            attr = sai_thrift_attribute_t(id=SAI_VIRTUAL_ROUTER_ATTR_SRC_MAC_ADDRESS, value=attr_value)
            self.client.sai_thrift_set_virtual_router_attribute(vr_id, attr)

            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id)
            for a in attrs.attr_list:
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V4_STATE:
                    print "set v4_enabled = %d" %v4_enabled
                    print "get v4_enabled = %d" %a.value.booldata
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V6_STATE:
                    print "set v6_enabled = %d" %v6_enabled
                    print "get v6_enabled = %d" %a.value.booldata
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_VIRTUAL_ROUTER_ATTR_SRC_MAC_ADDRESS:
                    print "set router_mac = %s" %vr_router_mac
                    print "get router_mac = %s" %a.value.mac
                    if vr_router_mac != a.value.mac:
                        raise NotImplementedError()    

        finally:
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouterInterfaceCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create router interface
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        port1 = port_list[0]
        vlan_id = 10
        mac = ''

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_SUB_PORT, port1, vlan_oid, v4_enabled, v6_enabled, mac)

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID:
                    if vr_id != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_TYPE:
                    if SAI_ROUTER_INTERFACE_TYPE_SUB_PORT != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_PORT_ID:
                    if port1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_VLAN_ID:
                    print "set vlan_oid = 0x%x" %vlan_oid
                    print "get vlan_oid = 0x%x" %a.value.oid
                    if vlan_oid != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()

        finally:
            print "clean up"
            self.client.sai_thrift_remove_router_interface(rif_id)
            self.client.sai_thrift_remove_virtual_router(vr_id)
            self.client.sai_thrift_remove_vlan(vlan_oid)

class L3RouterInterfaceRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Remove test.
        Steps:
        1. create router interface
        2. remove router interface
        3. get attribute and check
        4. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        port1 = port_list[0]
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            self.client.sai_thrift_remove_router_interface(rif_id)
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)


        finally:
            print "clean up"
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouterInterfaceDefaultTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Default attribute test.
        Steps:
        1. create router interface
        2. get default attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        port1 = port_list[0]
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS:
                    print "set router_mac = %s" %router_mac
                    print "get router_mac = %s" %a.value.mac
                    if router_mac != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_MTU:
                    print "get mtu = %d" %a.value.u32
                    if 1514 != a.value.u32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_TRAP != a.value.s32:
                        raise NotImplementedError()

        finally:
            print "clean up"
            self.client.sai_thrift_remove_router_interface(rif_id)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouterInterfaceSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create router interface
        2. set attribute
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        port1 = port_list[0]
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        warmboot(self.client)
        try:
            print "=======first get attr again======="
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS:
                    print "get router_mac = %s" %a.value.mac
                    if router_mac != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_MTU:
                    print "get mtu = %d" %a.value.u32
                    if 1514 != a.value.u32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_TRAP != a.value.s32:
                        raise NotImplementedError()

            print "======set and get attr again======"
            v4_enabled = 0
            v6_enabled = 0
            vr_router_mac = "aa:bb:cc:dd:ee:ff"
            mtu = 9600
            action = SAI_PACKET_ACTION_TRANSIT
            attr_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(mac=vr_router_mac)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(u32=mtu)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)
            attr_value = sai_thrift_attribute_value_t(s32=action)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id, attr)

            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_id)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE:
                    if v4_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE:
                    if v6_enabled != a.value.booldata:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS:
                    print "get router_mac = %s" %a.value.mac
                    if vr_router_mac != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_MTU:
                    print "get mtu = %d" %a.value.u32
                    if mtu != a.value.u32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTER_INTERFACE_ATTR_NEIGHBOR_MISS_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if action != a.value.s32:
                        raise NotImplementedError()

        finally:
            print "clean up"
            self.client.sai_thrift_remove_router_interface(rif_id)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouterInterfaceRouteMacTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create router interface with new route mac
        2. set ip packet with the new route mac and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = "aa:bb:cc:dd:ee:ff"

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, rif_id1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, rif_id1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouterInterfaceMTUTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create router interface with default MTU
        2. set ip packet and receive the packet
        3. set MTU size to 30
        4. set ip packet and not receive the packet
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''
        mtu = 30

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, rif_id1)        

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

            attr_value = sai_thrift_attribute_value_t(u32=mtu)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id1, attr)
            attr_value = sai_thrift_attribute_value_t(u32=mtu)
            attr = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_router_interface_attribute(rif_id2, attr)
            send_packet(self, 1, str(pkt))
            verify_no_packet(self, exp_pkt, 0, default_time_out)

        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, rif_id1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)


class L3RouterInterfaceBridgePortRifTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print ""
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        vlan1_id = 10
        vlan2_id = 100
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]

        mac1 = '00:01:01:01:01:01'
        ip1 = '11.11.11.1'

        mac2 = '00:02:02:02:02:02'
        ip2 = '10.10.10.2'
        ip_addr_subnet = '10.10.10.0'
        ip_mask = '255.255.255.0'

        mac3 = '00:22:22:22:22:22'
        ip3 = '10.0.0.1'
        
        vlan1_oid = sai_thrift_create_vlan(self.client, vlan1_id)
        vlan2_oid = sai_thrift_create_vlan(self.client, vlan2_id)

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        sai_thrift_vlan_remove_ports(self.client, switch.default_vlan.oid, [port2, port3, port4])
        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id, vlan2_id)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port3, bridge_id, vlan2_id)
        bport3_id = sai_thrift_create_bridge_sub_port(self.client, port4, bridge_id, vlan2_id)

        sai_thrift_create_fdb_bport(self.client, bridge_id, mac2, bport1_id, SAI_PACKET_ACTION_FORWARD)


        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        
        sub_port_rif_oid = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_SUB_PORT, port1, vlan1_oid, v4_enabled, v6_enabled, '')
        bridge_rif_oid = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_BRIDGE, 0, 0, v4_enabled, v6_enabled, '')
        bridge_rif_bp = sai_thrift_create_bridge_rif_port(self.client, bridge_id, bridge_rif_oid)

        sai_thrift_create_neighbor(self.client, SAI_IP_ADDR_FAMILY_IPV4, bridge_rif_oid, ip2, mac2)
        
        local_pkt = simple_tcp_packet(eth_src=mac2,
                                      eth_dst=mac3,
                                      dl_vlan_enable=True,
                                      vlan_vid=vlan2_id,
                                      ip_src=ip2,
                                      ip_dst=ip3,
                                      ip_id=102,
                                      ip_ttl=64)

        L3_pkt = simple_tcp_packet(eth_src=mac1,
                                   eth_dst=router_mac,
                                   ip_src=ip1,
                                   ip_dst=ip2,
                                   dl_vlan_enable=True,
                                   vlan_vid=vlan1_id,
                                   ip_id=105,
                                   ip_ttl=64)

        exp_pkt = simple_tcp_packet(eth_src=router_mac,
                                    eth_dst=mac2,
                                    ip_src=ip1,
                                    ip_dst=ip2,
                                    dl_vlan_enable=True,
                                    vlan_vid=vlan2_id,
                                    ip_id=105,
                                    ip_ttl=63)

        warmboot(self.client)
        try:
            print "Sending unknown L2 packet [{} -> {}] to learn FDB and flood within a .1D bridge".format(mac1, mac3)
            send_packet(self, 1, str(local_pkt))
            verify_packets(self, local_pkt, [2, 3])
            print "Success"

            print "Sending packet ({} -> {}) : Sub-port rif (port 1 : vlan {}) -> Bridge rif".format(ip1, ip2, vlan1_id)
            send_packet(self, 0, str(L3_pkt))
            verify_packets(self, exp_pkt, [1])
            print "Success"

        finally:

            sai_thrift_remove_neighbor(self.client, SAI_IP_ADDR_FAMILY_IPV4, bridge_rif_oid, ip2, mac2)
            self.client.sai_thrift_remove_router_interface(sub_port_rif_oid)
            self.client.sai_thrift_remove_bridge_port(bridge_rif_bp)
            self.client.sai_thrift_remove_router_interface(bridge_rif_oid)
            self.client.sai_thrift_remove_virtual_router(vr_id)
            sai_thrift_delete_fdb(self.client, bridge_id, mac2, bport1_id)
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port2)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port3)
            sai_thrift_remove_bridge_sub_port(self.client, bport3_id, port4)
            self.client.sai_thrift_remove_bridge(bridge_id)
            
            self.client.sai_thrift_remove_vlan(vlan1_oid)
            self.client.sai_thrift_remove_vlan(vlan2_oid)



class L3NeighborIPv4CreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get attr and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        status = sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        print "status = %d" %status
   
        warmboot(self.client)
        try:
            status = sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            print "status = %d" %status
            assert (status == SAI_STATUS_ITEM_ALREADY_EXISTS)   
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS:
                    print "set dest mac = %s" %dmac1
                    print "get dest mac = %s" %a.value.mac
                    if dmac1 != a.value.mac:
                        raise NotImplementedError()
        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborIPv4RemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get attr and check
        3. remove neighbor entry
        4. get attr and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
            

        finally:
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborIPv6CreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get attr and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip6=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS:
                    print "set dest mac = %s" %dmac1
                    print "get dest mac = %s" %a.value.mac
                    if dmac1 != a.value.mac:
                        raise NotImplementedError()
        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborIPv6RemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get attr and check
        3. remove neighbor entry
        4. get attr and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip6=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
            

        finally:
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborRemoveALLTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create ipv4 and ipv6 neighbor entry
        2. get attr and check
        3. remove all neighbor entry
        4. get attr and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''
        cnt = 256;

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        dmac1 = '00:11:22:33:44:55'
        ipv4_addr = '10.10.10.1'
        ipv6_addr = '1234:5678:9abc:def0:4422:1133:5577:99aa'        
        for i in range(cnt):
            print "create neighbors"
            ipv4_int = ip4_to_integer(ipv4_addr)+i
            ip_addr1 = integer_to_ip4(ipv4_int)
            sai_thrift_create_neighbor(self.client, SAI_IP_ADDR_FAMILY_IPV4, rif_id1, ip_addr1, dmac1)
            
            ipv6_int = ip6_to_integer(ipv6_addr)+i
            ip_addr2 = integer_to_ip6(ipv6_int)
            sai_thrift_create_neighbor(self.client, SAI_IP_ADDR_FAMILY_IPV6, rif_id1, ip_addr2, dmac1)

            print "check neighbor"
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)

            addr = sai_thrift_ip_t(ip6=ip_addr2)
            ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)

        print "remove all neighbor"
        self.client.sai_thrift_remove_all_neighbor_entry()

        warmboot(self.client)
        try:
            for i in range(cnt):
                ipv4_int = ip4_to_integer(ipv4_addr)+i
                ip_addr1 = integer_to_ip4(ipv4_int)
                addr = sai_thrift_ip_t(ip4=ip_addr1)
                ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
                neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
                attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
                print "status = %d" %attrs.status
                assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
                
                ipv6_int = ip6_to_integer(ipv6_addr)+i
                ip_addr2 = integer_to_ip6(ipv6_int)
                addr = sai_thrift_ip_t(ip6=ip_addr2)
                ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
                neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
                attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
                print "status = %d" %attrs.status
                assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)

        finally:
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborDefaultTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get default attr and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_PACKET_ACTION:
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE:
                    if 0 != a.value.booldata:
                        raise NotImplementedError()
        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Neighbor Entry Create test.
        Steps:
        1. create neighbor entry
        2. get default attr and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[0]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)

        addr_family=SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
           
            #check attr
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS:
                    print "set dest mac = %s" %dmac1
                    print "get dest mac = %s" %a.value.mac
                    if dmac1 != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_PACKET_ACTION:
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE:
                    if 0 != a.value.booldata:
                        raise NotImplementedError()
            # set attr
            dmac2 = 'aa:bb:cc:dd:ee:ff'
            attr_value = sai_thrift_attribute_value_t(mac=dmac2)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_TRANSIT)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            attr_value = sai_thrift_attribute_value_t(booldata=1)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)

            #check attr
            attrs = self.client.sai_thrift_get_neighbor_entry_attribute(neighbor_entry)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS:
                    print "set dest mac = %s" %dmac2
                    print "get dest mac = %s" %a.value.mac
                    if dmac2 != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_PACKET_ACTION_TRANSIT:
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE:
                    if 1 != a.value.booldata:
                        raise NotImplementedError()

        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborDestMacTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create neighbor entry
        2. set ip packet and check dest mac
        3. update neighbor entry dest mac
        4. set ip packet and check dest mac
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = "aa:bb:cc:dd:ee:ff"

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)
            #set dest mac
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            dmac2 = '00:11:22:33:44:66'
            attr_value = sai_thrift_attribute_value_t(mac=dmac2)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)

            # send the test packet(s)
            pkt = simple_tcp_packet(eth_dst=mac,
                                    eth_src='00:22:22:22:22:22',
                                    ip_dst='10.10.10.1',
                                    ip_src='192.168.0.1',
                                    ip_id=105,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(
                                    eth_dst=dmac2,
                                    eth_src=mac,
                                    ip_dst='10.10.10.1',
                                    ip_src='192.168.0.1',
                                    ip_id=105,
                                    ip_ttl=63)
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)            

        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborNoHostRouteTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create neighbor entry
        2. set ip packet and check dest mac
        3. update neighbor entry dest mac
        4. set ip packet and check dest mac
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = "aa:bb:cc:dd:ee:ff"

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

            #update no host route
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            #update to true
            attr_value = sai_thrift_attribute_value_t(booldata=1)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            send_packet(self, 2, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)
            #update to false
            attr_value = sai_thrift_attribute_value_t(booldata=0)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_NO_HOST_ROUTE, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborActionTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Router Interface Create test.
        Steps:
        1. create neighbor entry
        2. set ip packet and check dest mac
        3. update neighbor entry dest mac
        4. set ip packet and check dest mac
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = "aa:bb:cc:dd:ee:ff"

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

            #update no host route
            addr = sai_thrift_ip_t(ip4=ip_addr1)
            ipaddr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id1, ip_address=ipaddr)
            #update to true
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DENY)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            send_packet(self, 2, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)
            #update to false
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_TRANSIT)
            attr = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_neighbor_entry_attribute(neighbor_entry, attr)
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborUpdateByFDBTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        vlan_id = 10
        mac = ''

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_VLAN, 0, vlan_oid, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            #add fdb 
            sai_thrift_create_fdb(self.client, vlan_oid, dmac1, port2, SAI_PACKET_ACTION_FORWARD)
            send_packet(self, 0, str(pkt))
            verify_packet(self, exp_pkt, 1)
            #delete fdb 
            sai_thrift_delete_fdb(self.client, vlan_oid, dmac1, port2)
            send_packet(self, 0, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)


        finally:
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

class L3NextHopCreateTest(sai_base_test.ThriftInterfaceDataPlane):
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

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_next_hop_attribute(nhop1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_ATTR_TYPE:
                    if SAI_NEXT_HOP_TYPE_IP != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_ATTR_IP:
                    print "get ip = %s" %a.value.ipaddr.addr.ip4
                    if ip_addr1 != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID:
                    if rif_id1 != a.value.oid:
                        raise NotImplementedError()
        finally:

            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
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

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_next_hop_attribute(nhop1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_ATTR_TYPE:
                    if SAI_NEXT_HOP_TYPE_IP != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_ATTR_IP:
                    print "get ip = %s" %a.value.ipaddr.addr.ip4
                    if ip_addr1 != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID:
                    if rif_id1 != a.value.oid:
                        raise NotImplementedError()
            self.client.sai_thrift_remove_next_hop(nhop1)
            attrs = self.client.sai_thrift_get_next_hop_attribute(nhop1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)

        finally:            
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NeighborNextHopShareTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        # create next hop first
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst=ip_addr1,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ip_dst=ip_addr1,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        pkt1 = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [1])
            send_packet(self, 2, str(pkt1))
            verify_packets(self, exp_pkt1, [1])
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopGroupCreateTest(sai_base_test.ThriftInterfaceDataPlane):
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
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_TYPE:
                    if SAI_NEXT_HOP_GROUP_TYPE_ECMP != a.value.s32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_next_hop_group(nhop_group1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopGroupRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
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
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_TYPE:
                    if SAI_NEXT_HOP_GROUP_TYPE_ECMP != a.value.s32:
                        raise NotImplementedError()
            self.client.sai_thrift_remove_next_hop_group(nhop_group1)
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)

        finally:
            
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopGroupMemberCreateTest(sai_base_test.ThriftInterfaceDataPlane):
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
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    print "get next hop group id = 0x%x" %a.value.oid
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    print "get next hop id = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()               
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember2)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    print "get next hop group id = 0x%x" %a.value.oid
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    print "get next hop id = 0x%x" %a.value.oid
                    if nhop2 != a.value.oid:
                        raise NotImplementedError()  

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

class L3NextHopGroupMemberRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
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
        nhop_group1 = sai_thrift_create_next_hop_group(self.client)
        print "nhop_group1 = 0x%x" %nhop_group1
        nhop_gmember1 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop1)
        nhop_gmember2 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop2)
        print "nhop_gmember1 = 0x%x" %nhop_gmember1
        print "nhop_gmember2 = 0x%x" %nhop_gmember2

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()               
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember2)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    if nhop2 != a.value.oid:
                        raise NotImplementedError()  
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember2)
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember2)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)

        finally:


            self.client.sai_thrift_remove_next_hop_group(nhop_group1)

            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)

            sai_thrift_remove_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)

            self.client.sai_thrift_remove_router_interface(rif1)
            self.client.sai_thrift_remove_router_interface(rif2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopGroupEcmpGetTest(sai_base_test.ThriftInterfaceDataPlane):
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
        nhop_gmember3 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop2)
        nhop_gmember4 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop2)
        print "nhop_gmember1 = 0x%x" %nhop_gmember1
        print "nhop_gmember2 = 0x%x" %nhop_gmember2
        print "nhop_gmember3 = 0x%x" %nhop_gmember3
        print "nhop_gmember4 = 0x%x" %nhop_gmember4

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_NEXT_HOP_COUNT:
                    if 4 != a.value.u32:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_TYPE:
                    if SAI_NEXT_HOP_GROUP_TYPE_ECMP != a.value.s32:
                        raise NotImplementedError()  

        finally:
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember2)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember3)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember4)

            self.client.sai_thrift_remove_next_hop_group(nhop_group1)

            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)

            sai_thrift_remove_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)

            self.client.sai_thrift_remove_router_interface(rif1)
            self.client.sai_thrift_remove_router_interface(rif2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3NextHopGroupProtctionGetTest(sai_base_test.ThriftInterfaceDataPlane):
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
        nhop_group1 = sai_thrift_create_next_hop_protection_group(self.client)
        print "nhop_group1 = 0x%x" %nhop_group1
        nhop_gmember1 = sai_thrift_create_next_hop_protection_group_member(self.client, nhop_group1, nhop1, SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_PRIMARY)
        nhop_gmember2 = sai_thrift_create_next_hop_protection_group_member(self.client, nhop_group1, nhop2, SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_STANDBY)
        print "nhop_gmember1 = 0x%x" %nhop_gmember1
        print "nhop_gmember2 = 0x%x" %nhop_gmember2

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_NEXT_HOP_COUNT:
                    if 2 != a.value.u32:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_TYPE:
                    if SAI_NEXT_HOP_GROUP_TYPE_PROTECTION != a.value.s32:
                        raise NotImplementedError()  

            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    print "get next hop group id = 0x%x" %a.value.oid
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    print "get next hop id = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_CONFIGURED_ROLE:
                    print "get role = %d" %a.value.s32
                    if SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_PRIMARY != a.value.s32:
                        raise NotImplementedError()           
            attrs = self.client.sai_thrift_get_next_hop_group_member_attribute(nhop_gmember2)
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID:
                    if nhop_group1 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID:
                    if nhop2 != a.value.oid:
                        raise NotImplementedError()  
                if a.id == SAI_NEXT_HOP_GROUP_MEMBER_ATTR_CONFIGURED_ROLE:
                    print "get role = %d" %a.value.s32
                    if SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_STANDBY != a.value.s32:
                        raise NotImplementedError()    

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

class L3NextHopGroupProtctionSwitchOverTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        rif1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_mask1 = '255.255.0.0'
        dmac1 = '00:11:22:33:44:55'
        dmac2 = '00:11:22:33:44:56'
        sai_thrift_create_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif2)
        print "nhop1 = 0x%x" %nhop1
        print "nhop2 = 0x%x" %nhop2
        nhop_group1 = sai_thrift_create_next_hop_protection_group(self.client)
        print "nhop_group1 = 0x%x" %nhop_group1
        nhop_gmember1 = sai_thrift_create_next_hop_protection_group_member(self.client, nhop_group1, nhop1, SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_PRIMARY)
        nhop_gmember2 = sai_thrift_create_next_hop_protection_group_member(self.client, nhop_group1, nhop2, SAI_NEXT_HOP_GROUP_MEMBER_CONFIGURED_ROLE_STANDBY)
        print "nhop_gmember1 = 0x%x" %nhop_gmember1
        print "nhop_gmember2 = 0x%x" %nhop_gmember2

        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1, ip_mask1, nhop_group1)

        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.0.0',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ip_dst='10.10.0.0',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:56',
                                eth_src=router_mac,
                                ip_dst='10.10.0.0',
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)

        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt1, 0)
  
            attr_value = sai_thrift_attribute_value_t(booldata=1)
            attr = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_ATTR_SET_SWITCHOVER, value=attr_value)
            self.client.sai_thrift_set_next_hop_group_attribute(nhop_group1, attr)
            attrs = self.client.sai_thrift_get_next_hop_group_attribute(nhop_group1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_NEXT_HOP_GROUP_ATTR_SET_SWITCHOVER:
                    print "get next hop group switch over = %d" %a.value.booldata
                    if 1 != a.value.booldata:
                        raise NotImplementedError()
            
            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt2, 1)

        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1, ip_mask1, nhop_group1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember2)
            self.client.sai_thrift_remove_next_hop_group(nhop_group1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif2, ip_addr1, dmac2)
            self.client.sai_thrift_remove_router_interface(rif1)
            self.client.sai_thrift_remove_router_interface(rif2)
            self.client.sai_thrift_remove_router_interface(rif3)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv4CreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        warmboot(self.client)
        try:
            status = sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            print "status = %d" %status
            assert (status == SAI_STATUS_ITEM_ALREADY_EXISTS) 

            addr = sai_thrift_ip_t(ip4=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip4=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)            
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop1
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()
   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv4RemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
        sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip4=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip4=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)            
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
   
        finally:

            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv4SetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip4=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip4=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)            
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop1
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()

            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DENY)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)
            attr_value = sai_thrift_attribute_value_t(oid=nhop2)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_DENY != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop2
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop2 != a.value.oid:
                        raise NotImplementedError()

   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv4SetNextHopTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr2 = '10.10.10.2'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr2, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])
            #update nexthop
            addr = sai_thrift_ip_t(ip4=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip4=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)      
      
            attr_value = sai_thrift_attribute_value_t(oid=nhop2)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            send_packet(self, 2, str(pkt))
            verify_packet(self, exp_pkt, 1)

   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv4ActionTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr2 = '10.10.10.2'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr2, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        # send the test packet(s)
        pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(
                                eth_dst=dmac1,
                                eth_src=router_mac,
                                ip_dst=ip_addr1_subnet,
                                ip_src='192.168.0.1',
                                ip_id=105,
                                ip_ttl=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])
            #update action
            addr = sai_thrift_ip_t(ip4=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip4=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)       
     
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DENY)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            send_packet(self, 2, str(pkt))
            verify_no_packet(self, exp_pkt, 0, default_time_out)
            
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_FORWARD)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])

   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv6CreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        ip_addr1_subnet = '1234:5678:9abc:def0:4422:1133:5577:0'
        ip_mask1 = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        warmboot(self.client)
        try:
            status = sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            print "status = %d" %status
            assert (status == SAI_STATUS_ITEM_ALREADY_EXISTS) 

            addr = sai_thrift_ip_t(ip6=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip6=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)            
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop1
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()
   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv6RemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        ip_addr1_subnet = '1234:5678:9abc:def0:4422:1133:5577:0'
        ip_mask1 = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
        sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
        warmboot(self.client)
        try:

            addr = sai_thrift_ip_t(ip6=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip6=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)            
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
   
        finally:
            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv6SetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        ip_addr1_subnet = '1234:5678:9abc:def0:4422:1133:5577:0'
        ip_mask1 = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        warmboot(self.client)
        try:
            addr = sai_thrift_ip_t(ip6=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip6=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)             
            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_FORWARD != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop1
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop1 != a.value.oid:
                        raise NotImplementedError()

            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DENY)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)
            attr_value = sai_thrift_attribute_value_t(oid=nhop2)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            attrs = self.client.sai_thrift_get_route_attribute(route)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION:
                    print "get action = %d" %a.value.s32
                    if SAI_PACKET_ACTION_DENY != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID:
                    print "set next hop = 0x%x" %nhop2
                    print "get next hop = 0x%x" %a.value.oid
                    if nhop2 != a.value.oid:
                        raise NotImplementedError()

   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv6SetNextHopTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        ip_addr2 = '1234:5678:9abc:def0:4422:1133:5577:99ab'
        ip_addr1_subnet = '1234:5678:9abc:def0:4422:1133:5577:0'
        ip_mask1 = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr2, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        # send the test packet(s)
        # send the test packet(s)
        pkt = simple_tcpv6_packet( eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ipv6_dst=ip_addr1_subnet,
                                ipv6_src='2000::1',
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ipv6_dst=ip_addr1_subnet,
                                ipv6_src='2000::1',
                                ipv6_hlim=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])
            #update nexthop
            addr = sai_thrift_ip_t(ip6=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip6=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)             
            attr_value = sai_thrift_attribute_value_t(oid=nhop2)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)
            
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [1])

   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)

            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3RouteIPv6ActionTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac_valid = 0
        mac = ''

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif_id1 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif_id2 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif_id3 = sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        addr_family = SAI_IP_ADDR_FAMILY_IPV6
        ip_addr1 = '1234:5678:9abc:def0:4422:1133:5577:99aa'
        ip_addr2 = '1234:5678:9abc:def0:4422:1133:5577:99ab'
        ip_addr1_subnet = '1234:5678:9abc:def0:4422:1133:5577:0'
        ip_mask1 = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:0'
        dmac1 = '00:11:22:33:44:55'
        sai_thrift_create_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif_id1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr2, rif_id2)
        sai_thrift_create_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)

        # send the test packet(s)
        # send the test packet(s)
        pkt = simple_tcpv6_packet( eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ipv6_dst=ip_addr1_subnet,
                                ipv6_src='2000::1',
                                ipv6_hlim=64)
        exp_pkt = simple_tcpv6_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ipv6_dst=ip_addr1_subnet,
                                ipv6_src='2000::1',
                                ipv6_hlim=63)
        warmboot(self.client)
        try:
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])
            #update nexthop
            addr = sai_thrift_ip_t(ip6=ip_addr1_subnet)
            mask = sai_thrift_ip_t(ip6=ip_mask1)
            ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
            route = sai_thrift_route_entry_t(vr_id, ip_prefix)             
            
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_DENY)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            send_packet(self, 2, str(pkt))
            verify_no_packet(self, exp_pkt, 0, default_time_out)
            
            attr_value = sai_thrift_attribute_value_t(s32=SAI_PACKET_ACTION_FORWARD)
            attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION, value=attr_value)
            self.client.sai_thrift_set_route_attribute(route, attr)

            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [0])
   
        finally:
            sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr1_subnet, ip_mask1, nhop1)
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr2, dmac1)
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_router_interface(rif_id3)

            self.client.sai_thrift_remove_virtual_router(vr_id)


class L3StressVirtualRouterTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        vr_num = 63
        vr_id_list = []

        for i in range(vr_num):
            vr_id_list.append(sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled))
            print "vr_id = 0x%x" %vr_id_list[i]
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id_list[i])
            assert (attrs.status == SAI_STATUS_SUCCESS)

        for i in range(vr_num):
            self.client.sai_thrift_remove_virtual_router(vr_id_list[i])
            attrs = self.client.sai_thrift_get_virtual_router_attribute(vr_id_list[i])
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)

class L3StressRouterInterfaceTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        v4_enabled = 1
        v6_enabled = 1
        port1 = port_list[0]
        vlan_id = 2
        mac = ''
        rf_num = 1000
        vlan_list = []
        rif_list = []

        vr_id = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)
        for i in range(rf_num):
            vlan_list.append(sai_thrift_create_vlan(self.client, vlan_id+i))
            rif_list.append(sai_thrift_create_router_interface(self.client, vr_id, SAI_ROUTER_INTERFACE_TYPE_SUB_PORT, port1, vlan_list[i], v4_enabled, v6_enabled, mac))
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_list[i])
            assert (attrs.status == SAI_STATUS_SUCCESS)

        for i in range(rf_num):
            self.client.sai_thrift_remove_router_interface(rif_list[i])
            attrs = self.client.sai_thrift_get_router_interface_attribute(rif_list[i])
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
            self.client.sai_thrift_remove_vlan(vlan_list[i])

        self.client.sai_thrift_remove_virtual_router(vr_id)


class L3StressNeighborIPv4Test(sai_base_test.ThriftInterfaceDataPlane):
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
            for i in range(neighbor_num):
                pkt = simple_tcp_packet(eth_dst=router_mac,
                                        eth_src='00:00:00:00:00:1',
                                        ip_dst=ip_addr[i],
                                        ip_src='192.168.8.1',
                                        ip_id=106,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=dest_mac[i],
                                             eth_src=router_mac,
                                             ip_dst=ip_addr[i],
                                             ip_src='192.168.8.1',
                                             ip_id=106,
                                             ip_ttl=63)
                print "send ip_addr = %s" %ip_addr[i]
                send_packet(self, 0, str(pkt))
                verify_packet(self, exp_pkt, 1)
            print "packet check pass"
        finally:
            for i in range(neighbor_num):
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3StressNeighborIPv6Test(sai_base_test.ThriftInterfaceDataPlane):
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
            for i in range(neighbor_num):
                pkt = simple_tcpv6_packet(eth_dst=router_mac,
                                          eth_src='00:00:00:00:00:1',
                                          ipv6_dst=ip_addr[i],
                                          ipv6_src='2000:bbbb::1',
                                          ipv6_hlim=64)
                exp_pkt = simple_tcpv6_packet(eth_dst=dest_mac[i],
                                              eth_src=router_mac,
                                              ipv6_dst=ip_addr[i],
                                              ipv6_src='2000:bbbb::1',
                                              ipv6_hlim=63)


                print "send ip_addr = %s" %ip_addr[i]
                send_packet(self, 0, str(pkt))
                verify_packet(self, exp_pkt, 1)
            print "packet check pass"
        finally:
            for i in range(neighbor_num):
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])
            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)


class L3StressNexthopTest(sai_base_test.ThriftInterfaceDataPlane):
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
            for i in range(next_hop_num):
                pkt = simple_tcp_packet(eth_dst=router_mac,
                                        eth_src='00:00:00:00:00:1',
                                        ip_dst=ip_addr_subnet[i],
                                        ip_src='192.168.8.1',
                                        ip_id=106,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=dest_mac[i],
                                             eth_src=router_mac,
                                             ip_dst=ip_addr_subnet[i],
                                             ip_src='192.168.8.1',
                                             ip_id=106,
                                             ip_ttl=63)
                print "send ip_addr = %s" %ip_addr_subnet[i]
                send_packet(self, 0, str(pkt))
                verify_packet(self, exp_pkt, 1)
            print "packet check pass"
        finally:
            for i in range(next_hop_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop[i])
                self.client.sai_thrift_remove_next_hop(nhop[i])
                sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr[i], dest_mac[i])

            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3StressRouteIPv4Test(sai_base_test.ThriftInterfaceDataPlane):
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
            for i in range(route_num):
                pkt = simple_tcp_packet(eth_dst=router_mac,
                                        eth_src='00:00:00:00:00:1',
                                        ip_dst=ip_addr_subnet[i],
                                        ip_src='192.168.8.1',
                                        ip_id=106,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=dmac1,
                                             eth_src=router_mac,
                                             ip_dst=ip_addr_subnet[i],
                                             ip_src='192.168.8.1',
                                             ip_id=106,
                                             ip_ttl=63)
                print "send ip_addr = %s" %ip_addr_subnet[i]
                send_packet(self, 0, str(pkt))
                verify_packet(self, exp_pkt, 1)
            print "packet check pass"
        finally:
            for i in range(route_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop1)

            self.client.sai_thrift_remove_next_hop(nhop1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

class L3StressRouteIPv6Test(sai_base_test.ThriftInterfaceDataPlane):
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
            for i in range(route_num):
                pkt = simple_tcpv6_packet(eth_dst=router_mac,
                                          eth_src='00:00:00:00:00:1',
                                          ipv6_dst=ip_addr_subnet[i],
                                          ipv6_src='2000:bbbb::1',
                                          ipv6_hlim=64)
                exp_pkt = simple_tcpv6_packet(eth_dst=dmac1,
                                              eth_src=router_mac,
                                              ipv6_dst=ip_addr_subnet[i],
                                              ipv6_src='2000:bbbb::1',
                                              ipv6_hlim=63)


                print "send ip_addr = %s" %ip_addr_subnet[i]
                send_packet(self, 0, str(pkt))
                verify_packet(self, exp_pkt, 1)
            print "packet check pass"
        finally:
            for i in range(route_num):
                sai_thrift_remove_route(self.client, vr_id, addr_family, ip_addr_subnet[i], ip_mask, nhop)
            
            self.client.sai_thrift_remove_next_hop(nhop)
            sai_thrift_remove_neighbor(self.client, addr_family, rif_id2, ip_addr1, dmac1)            
            self.client.sai_thrift_remove_router_interface(rif_id1)
            self.client.sai_thrift_remove_router_interface(rif_id2)
            self.client.sai_thrift_remove_virtual_router(vr_id)

















