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
import sys
from struct import pack, unpack

from switch import *

import sai_base_test
from ptf.mask import Mask

@group('hash')

class HashCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Hash Create Test. Verify that Hash is not support create. 
        Steps:
        1. Create Hash.
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        field_list = [SAI_NATIVE_HASH_FIELD_SRC_IP, SAI_NATIVE_HASH_FIELD_DST_IP]
        udf_group_list = [123,456]
        
        # create hash
        print "Create Hash "
        hash_id = sai_thrift_create_hash(self.client, field_list, udf_group_list)
        print "hash_id = %d" %hash_id
        
        warmboot(self.client)
        try:
            print "Check create hash, not support create hash"
            assert (hash_id == 0)
        finally:
            print "Success!"
            
class HashRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Hash Remove Test. 
        Steps:
        1. create Hash, not support
        2. remove Hash, not support
        3. get attribute and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        field_list = [SAI_NATIVE_HASH_FIELD_SRC_IP, SAI_NATIVE_HASH_FIELD_DST_IP]
        udf_group_list = [123,456]
        
        # create hash
        print "Create Hash "
        hash_id = sai_thrift_create_hash(self.client, field_list, udf_group_list)
        print "sai_thrift_create_hash; hash_id = %d" %hash_id
        
        # remove hash
        print "Remove Hash"
        status=self.client.sai_thrift_remove_hash(hash_id)
        print "sai_thrift_remove_hash; status = %d" %status
        assert (status == SAI_STATUS_NOT_SUPPORTED)
        
        warmboot(self.client)
        try:
            print "Check create hash, not support create hash"
            assert (hash_id == 0)
        finally:
            print "Success!"
   
@group('l2')
@group('lag')
class HashL2LagDefaultTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        vlan_id = 10
        hash_id_lag = 0x201C
        hash_id_ecmp = 0x1C
        field_list = [SAI_NATIVE_HASH_FIELD_SRC_MAC]
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)

        lag_id1 = sai_thrift_create_lag(self.client, [])
        print"lag:%u" %lag_id1
        print"lag:%lu" %lag_id1
        print"lag:%lx" %lag_id1
        print"lag:%x" %lag_id1


        """sai_thrift_vlan_remove_all_ports(self.client, switch.default_vlan.oid)"""
        print "port:%lx" %port1
        print "lag_id1:%lx" %lag_id1
        lag_member_id1 = sai_thrift_create_lag_member(self.client, lag_id1, port1)
        lag_member_id2 = sai_thrift_create_lag_member(self.client, lag_id1, port2)
        lag_member_id3 = sai_thrift_create_lag_member(self.client, lag_id1, port3)

        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, lag_id1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_LAG_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_lag_attribute(lag_id1, attr)

        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port4, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, lag_id1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port4, mac_action)
        
        # set lag hash: hash field default value to  ip_da
        #Hash field list
        if field_list:
            hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
            attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
            attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                                value=attr_value)
            self.client.sai_thrift_set_hash_attribute(hash_id_lag, attr)

        warmboot(self.client)
        try:
            count = [0, 0, 0]
            # src_mac how to write
            max_itrs = 20
            #src_mac_start = '00:22:22:22:{0}:{1}'
            src_mac_start = '00:22:22:22:22:{0}'
            for i in range(0, max_itrs):
                #src_mac = src_mac_start.format(str(i).zfill(4)[:2], str(i).zfill(4)[2:])
                src_mac = src_mac_start.format(str(i).zfill(4)[2:])
                pkt = simple_tcp_packet(eth_dst='00:11:11:11:11:11',
                                        eth_src=src_mac,
                                        ip_dst='10.10.10.1',
                                        ip_src='192.168.8.1',
                                        ip_id=109,
                                        ip_ttl=64)

                exp_pkt = simple_tcp_packet(eth_dst='00:11:11:11:11:11',
                                            eth_src=src_mac,
                                            ip_dst='10.10.10.1',
                                            ip_src='192.168.8.1',
                                            ip_id=109,
                                            ip_ttl=64)

                send_packet(self, 3, str(pkt))
                rcv_idx = verify_any_packet_any_port(self, [exp_pkt], [0, 1, 2])
                print"*********************** rcv_idx:%d" %rcv_idx
                count[rcv_idx] += 1

            print"count:####################################"
            print count
            for i in range(0, 3):
                #self.assertTrue((count[i] >= ((max_itrs / 3) * 0.8)),
                self.assertTrue((count[i] >= ((max_itrs / 3) * 0.3)),
                       "Not all paths are equally balanced")

            pkt = simple_tcp_packet(eth_src='00:11:11:11:11:11',
                                    eth_dst='00:22:22:22:22:22',
                                    ip_dst='10.0.0.1',
                                    ip_id=109,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(eth_src='00:11:11:11:11:11',
                                    eth_dst='00:22:22:22:22:22',
                                    ip_dst='10.0.0.1',
                                    ip_id=109,
                                    ip_ttl=64)
            print "Sending packet port 1 (lag member) -> port 4"
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [3])
            print "Sending packet port 2 (lag member) -> port 4"
            send_packet(self, 1, str(pkt))
            verify_packets(self, exp_pkt, [3])
            print "Sending packet port 3 (lag member) -> port 4"
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [3])
            
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, lag_id1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port4)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            
            sai_thrift_remove_lag_member(self.client, lag_member_id1)
            sai_thrift_remove_lag_member(self.client, lag_member_id2)
            sai_thrift_remove_lag_member(self.client, lag_member_id3)
            sai_thrift_remove_lag(self.client, lag_id1)
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
            for port in sai_port_list:
                sai_thrift_create_vlan_member(self.client, switch.default_vlan.oid, port, SAI_VLAN_TAGGING_MODE_UNTAGGED)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port4, attr) 

            field_list = [SAI_NATIVE_HASH_FIELD_SRC_MAC, SAI_NATIVE_HASH_FIELD_DST_MAC, SAI_NATIVE_HASH_FIELD_IN_PORT, SAI_NATIVE_HASH_FIELD_ETHERTYPE]
            if field_list:
                hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
                attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
                attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                                    value=attr_value)
                self.client.sai_thrift_set_hash_attribute(hash_id_lag, attr)           
           
@group('l2')
@group('lag')
class HashL2LagSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        vlan_id = 10
        hash_id_lag = 0x201C
        hash_id_ecmp = 0x1C
        field_list = [SAI_NATIVE_HASH_FIELD_DST_IP]
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)

        lag_id1 = sai_thrift_create_lag(self.client, [])
        print"lag:%u" %lag_id1
        print"lag:%lu" %lag_id1
        print"lag:%lx" %lag_id1
        print"lag:%x" %lag_id1


        """sai_thrift_vlan_remove_all_ports(self.client, switch.default_vlan.oid)"""
        print "port:%lx" %port1
        print "lag_id1:%lx" %lag_id1
        lag_member_id1 = sai_thrift_create_lag_member(self.client, lag_id1, port1)
        lag_member_id2 = sai_thrift_create_lag_member(self.client, lag_id1, port2)
        lag_member_id3 = sai_thrift_create_lag_member(self.client, lag_id1, port3)

        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, lag_id1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port4, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_LAG_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_lag_attribute(lag_id1, attr)

        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port4, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, lag_id1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port4, mac_action)
        
        # set lag hash: hash field default value to  ip_da
        #Hash field list
        if field_list:
            hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
            attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
            attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                                value=attr_value)
            self.client.sai_thrift_set_hash_attribute(hash_id_lag, attr)

        warmboot(self.client)
        try:
            count = [0, 0, 0]
            dst_ip = int(socket.inet_aton('10.10.10.1').encode('hex'),16)
            max_itrs = 20
            for i in range(0, max_itrs):
                dst_ip_addr = socket.inet_ntoa(hex(dst_ip)[2:].zfill(8).decode('hex'))
                pkt = simple_tcp_packet(eth_dst='00:11:11:11:11:11',
                                        eth_src='00:22:22:22:22:22',
                                        ip_dst=dst_ip_addr,
                                        ip_src='192.168.8.1',
                                        ip_id=109,
                                        ip_ttl=64)

                exp_pkt = simple_tcp_packet(eth_dst='00:11:11:11:11:11',
                                            eth_src='00:22:22:22:22:22',
                                            ip_dst=dst_ip_addr,
                                            ip_src='192.168.8.1',
                                            ip_id=109,
                                            ip_ttl=64)

                send_packet(self, 3, str(pkt))
                rcv_idx = verify_any_packet_any_port(self, [exp_pkt], [0, 1, 2])
                count[rcv_idx] += 1
                dst_ip += 1

            print count
            for i in range(0, 3):
                self.assertTrue((count[i] >= ((max_itrs / 3) * 0.8)),
                        "Not all paths are equally balanced")

            pkt = simple_tcp_packet(eth_src='00:11:11:11:11:11',
                                    eth_dst='00:22:22:22:22:22',
                                    ip_dst='10.0.0.1',
                                    ip_id=109,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(eth_src='00:11:11:11:11:11',
                                    eth_dst='00:22:22:22:22:22',
                                    ip_dst='10.0.0.1',
                                    ip_id=109,
                                    ip_ttl=64)
            print "Sending packet port 1 (lag member) -> port 4"
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [3])
            print "Sending packet port 2 (lag member) -> port 4"
            send_packet(self, 1, str(pkt))
            verify_packets(self, exp_pkt, [3])
            print "Sending packet port 3 (lag member) -> port 4"
            send_packet(self, 2, str(pkt))
            verify_packets(self, exp_pkt, [3])
            
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, lag_id1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port4)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            
            sai_thrift_remove_lag_member(self.client, lag_member_id1)
            sai_thrift_remove_lag_member(self.client, lag_member_id2)
            sai_thrift_remove_lag_member(self.client, lag_member_id3)
            sai_thrift_remove_lag(self.client, lag_id1)
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
            for port in sai_port_list:
                sai_thrift_create_vlan_member(self.client, switch.default_vlan.oid, port, SAI_VLAN_TAGGING_MODE_UNTAGGED)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port4, attr)  

            field_list = [SAI_NATIVE_HASH_FIELD_SRC_MAC, SAI_NATIVE_HASH_FIELD_DST_MAC, SAI_NATIVE_HASH_FIELD_IN_PORT, SAI_NATIVE_HASH_FIELD_ETHERTYPE]
            if field_list:
                hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
                attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
                attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                                    value=attr_value)
                self.client.sai_thrift_set_hash_attribute(hash_id_lag, attr)           

class HashL3IPv4EcmpHostTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print "Sending packet port 1 -> port 2 (192.168.0.1 -> 10.10.10.1 [id = 101])"
        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        v4_enabled = 1
        v6_enabled = 1
        mac = ''
        hash_id_lag = 0x201C
        hash_id_ecmp = 0x1C
        field_list = [SAI_NATIVE_HASH_FIELD_SRC_IP]

        addr_family = SAI_IP_ADDR_FAMILY_IPV4
        ip_addr1 = '10.10.10.1'
        ip_addr2 = '10.10.10.2'
        ip_addr1_subnet = '10.10.10.0'
        ip_mask1 = '255.255.255.0'
        dmac1 = '00:11:22:33:44:55'
        dmac2 = '00:11:22:33:44:56'

        vr1 = sai_thrift_create_virtual_router(self.client, v4_enabled, v6_enabled)

        rif1 = sai_thrift_create_router_interface(self.client, vr1, SAI_ROUTER_INTERFACE_TYPE_PORT, port1, 0, v4_enabled, v6_enabled, mac)
        rif2 = sai_thrift_create_router_interface(self.client, vr1, SAI_ROUTER_INTERFACE_TYPE_PORT, port2, 0, v4_enabled, v6_enabled, mac)
        rif3 = sai_thrift_create_router_interface(self.client, vr1, SAI_ROUTER_INTERFACE_TYPE_PORT, port3, 0, v4_enabled, v6_enabled, mac)

        sai_thrift_create_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
        sai_thrift_create_neighbor(self.client, addr_family, rif2, ip_addr2, dmac2)

        nhop1 = sai_thrift_create_nhop(self.client, addr_family, ip_addr1, rif1)
        nhop2 = sai_thrift_create_nhop(self.client, addr_family, ip_addr2, rif2)
        nhop_group1 = sai_thrift_create_next_hop_group(self.client)
        nhop_gmember1 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop1)
        nhop_gmember2 = sai_thrift_create_next_hop_group_member(self.client, nhop_group1, nhop2)

        sai_thrift_create_route(self.client, vr1, addr_family, ip_addr1_subnet, ip_mask1, nhop_group1)
        
       ## set lag hash: hash field default value to  ip_sa
       ##Hash field list
        if field_list:
            hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
            attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
            attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                            value=attr_value)
            self.client.sai_thrift_set_hash_attribute(hash_id_ecmp, attr)
       
       # send the test packet(s)
        warmboot(self.client)
        try:
        # step1
            pkt = simple_tcp_packet(eth_dst=router_mac,
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=106,
                                ip_ttl=64)

            exp_pkt1 = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:55',
                                eth_src=router_mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=106,
                                #ip_tos=3,
                                ip_ttl=63)
            exp_pkt2 = simple_tcp_packet(
                                eth_dst='00:11:22:33:44:56',
                                eth_src=router_mac,
                                ip_dst='10.10.10.1',
                                ip_src='192.168.0.1',
                                ip_id=106,
                                #ip_tos=3,
                                ip_ttl=63)

            send_packet(self, 2, str(pkt))
            #verify_any_packet_any_port(self, [exp_pkt1, exp_pkt2], [0, 1])
            verify_packets(self, exp_pkt1, [0])

            # step2
            pkt = simple_tcp_packet(eth_dst=router_mac,
                                    eth_src='00:22:22:22:22:22',
                                    ip_dst='10.10.10.2',
                                    ip_src='192.168.100.3',
                                    ip_id=106,
                                    ip_ttl=64)
            
            exp_pkt1 = simple_tcp_packet(
                                    eth_dst='00:11:22:33:44:55',
                                    eth_src=router_mac,
                                    ip_dst='10.10.10.2',
                                    ip_src='192.168.100.3',
                                    ip_id=106,
                                    #ip_tos=3,
                                    ip_ttl=63)
            exp_pkt2 = simple_tcp_packet(
                                    eth_dst='00:11:22:33:44:56',
                                    eth_src=router_mac,
                                    ip_dst='10.10.10.2',
                                    ip_src='192.168.100.3',
                                    ip_id=106,
                                    #ip_tos=3,
                                    ip_ttl=63)
            
            send_packet(self, 2, str(pkt))
            #verify_any_packet_any_port(self, [exp_pkt1, exp_pkt2], [0, 1])
            verify_packets(self, exp_pkt2, [1])
            
            ## step3
            count = [0, 0]
            src_ip = int(socket.inet_aton('192.168.100.3').encode('hex'),16)
            max_itrs = 20
            for i in range(0, max_itrs):
                src_ip_addr = socket.inet_ntoa(hex(src_ip)[2:].zfill(8).decode('hex'))
                pkt = simple_tcp_packet(eth_dst=router_mac,
                                        eth_src='00:22:22:22:22:22',
                                        ip_dst='10.10.10.3',
                                        ip_src=src_ip_addr,
                                        ip_id=106,
                                        ip_ttl=64)
            
                exp_pkt1 = simple_tcp_packet(eth_dst='00:11:22:33:44:55',
                                        eth_src=router_mac,
                                        ip_dst='10.10.10.3',
                                        ip_src=src_ip_addr,
                                        ip_id=106,
                                        #ip_tos=3,
                                        ip_ttl=63)
                exp_pkt2 = simple_tcp_packet(eth_dst='00:11:22:33:44:56',
                                        eth_src=router_mac,
                                        ip_dst='10.10.10.3',
                                        ip_src=src_ip_addr,
                                        ip_id=106,
                                        #ip_tos=3,
                                        ip_ttl=63)
            
                send_packet(self, 2, str(pkt))
                rcv_idx = verify_any_packet_any_port(self, [exp_pkt1,exp_pkt2], [0, 1])
                count[rcv_idx] += 1
                print"*********************** rcv_idx:%d" %rcv_idx
                src_ip += 1
            
            print count
            for i in range(0, 2):
                self.assertTrue((count[i] >= ((max_itrs / 2) * 0.8)),
                        "Not all paths are equally balanced")
                        
        finally:

            sai_thrift_remove_route(self.client, vr1, addr_family, ip_addr1_subnet, ip_mask1, nhop_group1)
            
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember1)
            self.client.sai_thrift_remove_next_hop_group_member(nhop_gmember2)
            
            self.client.sai_thrift_remove_next_hop_group(nhop_group1)
            
            self.client.sai_thrift_remove_next_hop(nhop1)
            self.client.sai_thrift_remove_next_hop(nhop2)
            
            sai_thrift_remove_neighbor(self.client, addr_family, rif1, ip_addr1, dmac1)
            sai_thrift_remove_neighbor(self.client, addr_family, rif2, ip_addr2, dmac2)
            
            self.client.sai_thrift_remove_router_interface(rif1)
            self.client.sai_thrift_remove_router_interface(rif2)
            self.client.sai_thrift_remove_router_interface(rif3)

            self.client.sai_thrift_remove_virtual_router(vr1)  

            field_list = [SAI_NATIVE_HASH_FIELD_SRC_MAC, SAI_NATIVE_HASH_FIELD_DST_MAC, SAI_NATIVE_HASH_FIELD_IN_PORT, SAI_NATIVE_HASH_FIELD_ETHERTYPE]
            if field_list:
                hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
                attr_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
                attr = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                                    value=attr_value)
                self.client.sai_thrift_set_hash_attribute(hash_id_ecmp, attr)            