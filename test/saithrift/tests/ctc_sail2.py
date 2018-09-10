# Copyright 2013-present Centec Networks, Inc.
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
Thrift SAI interface L2 tests
"""
import socket
from switch import *
import sai_base_test

@group('l2')
class L2AccessTohybridVlanTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Access To hybrid test,verify vlan attribute
        steps:
	step1:set port1 & port2 as access ports,port3 as hybrid port
	step2:set default vlan of port1 as 10
	          set default vlan of port2 as 20
	step3:send untagged packet to port1 ,the packet will be received from port 3 without tag
	          send untagged packet to port1 ,the packet will be received from port 3 with tag 20
	step4:clean up
	"""
        print
        print "start test"
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 20
        vlan_id3 = 30
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac3 = '00:30:30:30:30:30'
        mac4 = '00:40:40:40:40:40'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_oid3 = sai_thrift_create_vlan(self.client, vlan_id3)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id1)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        
        attr_value = sai_thrift_attribute_value_t(u16=vlan_id2)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port2, attr)
	
        attr_value = sai_thrift_attribute_value_t(u16=vlan_id3)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port3, attr)

        sai_thrift_create_fdb(self.client, vlan_oid1, mac2, port3, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid2, mac4, port3, mac_action)

        pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=101,
                                ip_ttl=64)
        pkt1 = simple_tcp_packet(eth_dst=mac4,
                                eth_src=mac3,
                                ip_dst='20.0.0.1',
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=100)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac4,
                                eth_src=mac3,
                                ip_dst='20.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=20,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)
                                
        warmboot(self.client)
        try:
            print "Sending L2 packet port 1 -> port 3 [access vlan=10]), packet from port3 without vlan"
            send_packet(self, 0, str(pkt))
            verify_packets(self, pkt, [2])
            print "Sending L2 packet port 2 -> port 3 [access vlan=20]) packet from port3 with vlan 20"
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [2])
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid1, mac2, port3)
            sai_thrift_delete_fdb(self.client, vlan_oid2, mac4, port3)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid1)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            self.client.sai_thrift_set_port_attribute(port3, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            self.client.sai_thrift_remove_vlan(vlan_oid3)
@group('l2')
class L2TrunkTohybridVlanTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        
        """
        Trunk To hybrid test,verify vlan attribute
        steps:
	step1:set port1 & port2 as trunk ports,port3 as hybrid port
	step2:set default vlan of port1 as 10
	          set default vlan of port2 as 30
	step3:Sending L2 packet port 1 -> port 2 [without vlan]), packet from port2 with vlan 10
                  Sending L2 packet port 1 -> port 2 [with vlan 10]) packet from port2 with vlan 10
                  Sending L2 packet port 1 -> port 2 [with vlan 20]) packet from port2 with  vlan 20
                  Sending L2 packet port 1 -> port 2 [with vlan 30]) packet from port2 without vlan 
	step4:clean up
	"""

        print
        print "start test"
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 20
        vlan_id3 = 30
        port1 = port_list[0]
        port2 = port_list[1]
        
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_oid3 = sai_thrift_create_vlan(self.client, vlan_id3)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid3, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member5 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member6 = sai_thrift_create_vlan_member(self.client, vlan_oid3, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id1)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        
        attr_value = sai_thrift_attribute_value_t(u16=vlan_id3)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port2, attr)


        sai_thrift_create_fdb(self.client, vlan_oid1, mac2, port2, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid2, mac2, port2, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid3, mac2, port2, mac_action)

        pkt1 = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=101,
                                ip_ttl=64,
                                pktlen=96)
        pkt2 = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=101,
                                ip_ttl=64,
                                pktlen=100)
        
        pkt3 = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='20.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=20,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=100)
        pkt4 = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='30.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=30,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=100)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='30.0.0.1',
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=96)
                                
        warmboot(self.client)
        try:
            print "Sending L2 packet port 1 -> port 2 [without vlan]), packet from port2 with vlan 10"
            send_packet(self, 0, str(pkt1))
            verify_packets(self, pkt2, [1])
            print "Sending L2 packet port 1 -> port 2 [with vlan 10]) packet from port2 with vlan 10"
            send_packet(self, 0, str(pkt2))
            verify_packets(self, pkt2, [1])
            print "Sending L2 packet port 1 -> port 2 [with vlan 20]) packet from port2 with  vlan 20"
            send_packet(self, 0, str(pkt3))
            verify_packets(self, pkt3, [1])
            print "Sending L2 packet port 1 -> port 2 [with vlan 30]) packet from port2 without vlan"
            send_packet(self, 0, str(pkt4))
            verify_packets(self, exp_pkt1, [1])
        finally:
            
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid1)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid2)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid3)
            sai_thrift_delete_fdb(self.client, vlan_oid1, mac2, port2)
            sai_thrift_delete_fdb(self.client, vlan_oid2, mac2, port2)
            sai_thrift_delete_fdb(self.client, vlan_oid3, mac2, port2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            self.client.sai_thrift_remove_vlan_member(vlan_member5)
            self.client.sai_thrift_remove_vlan_member(vlan_member6)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            self.client.sai_thrift_remove_vlan(vlan_oid3)

@group('l2')
class L2FlushStatic(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        """
        flush static fdb entry,verify fdb flush funtion
        steps:
	step1:create a static fdb entry
	step2:send a packet,then fdb will learn a dynamic entry
	          
	step3:flush the static fdb
	step4:check the static fdb was flushed,the dynamic fdb was not flushed
	step5:clean up
	"""
        switch_init(self.client)
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD
        fdb_entry_type  = SAI_FDB_FLUSH_ENTRY_TYPE_STATIC

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)
        self.client.sai_thrift_set_port_attribute(port3, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)

        pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, fdb_entry_type)
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1, 2])
            
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [0])
            verify_no_packet(self, exp_pkt1, 2)
        finally:
            print "show fdb entry" 
            time.sleep(20)
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, SAI_FDB_FLUSH_ENTRY_TYPE_STATIC)
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            self.client.sai_thrift_set_port_attribute(port3, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('l2')
class L2FlushDynamic(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):

        """
        flush static fdb entry,verify fdb flush funtion
        steps:
	step1:create a static fdb entry
	step2:send a packet,then fdb will learn a dynamic entry
	          
	step3:flush the static fdb
	step4:check the static fdb was flushed,the dynamic fdb was not flushed
	step5:clean up
	"""
        print
        print 'flush dynamic'
        switch_init(self.client)
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD
        fdb_entry_type  = SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)
        self.client.sai_thrift_set_port_attribute(port3, attr)


        pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.2',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.2',
                                ip_id=107,
                                ip_ttl=64)

        print "start send packet"
        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1,2])
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [0])
            print "flush dynamic fdb entry"
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, fdb_entry_type)
            
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [0,2])
        finally:
            print "show fdb entry" 
            time.sleep(10)
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, SAI_FDB_FLUSH_ENTRY_TYPE_STATIC)
            sai_thrift_flush_fdb(self.client, SAI_NULL_OBJECT_ID, SAI_NULL_OBJECT_ID, SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            self.client.sai_thrift_set_port_attribute(port3, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan(vlan_oid)

            
@group('l2')
class L2FdbGetSetEntryTypeDynamicToStatic(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry type from Dynamic to Static,verify fdb set fdb type attribute
        steps:
	step1:create a dynamic fdb entry
	step2:check the entry type is right	          
	step3:set fdb entry type from Dynamic to Static
	step4:check the entry type is right
	step5:clean up

	NOTICE:sdk not suport set fdb entry from static to dynamic
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_FORWARD
        

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, mac_action, SAI_FDB_ENTRY_TYPE_DYNAMIC)
        result = sai_thrift_check_fdb_attribtue_type(self.client, vlan_oid, mac2, SAI_FDB_ENTRY_TYPE_DYNAMIC)
        
        if(1 == result):
            print "fdb entry type is right"
        else:
            print "fdb entry type is wrong"
        assert(1 == result)
        
        sai_thrift_set_fdb_type(self.client, vlan_oid, mac2,  SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_type(self.client, vlan_oid, mac2, SAI_FDB_ENTRY_TYPE_STATIC)
        if(1 == result):
            print "fdb entry type is right"
        else:
            print "fdb entry type is wrong"
        assert(1 == result)
        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('l2')
class L2FdbGetSetEntryActionTransitToTrap(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry action from Transit to trap,verify fdb set fdb action attribute
        steps:
	step1:create a  fdb entry,the action is transit
	step2:check the entry action is right	          
	step3:set fdb action from Transit to Trap
	step4:check the entry type is right
	step5:clean up
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        result = 0;
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_TRANSIT

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, mac_action, SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_TRANSIT)
        
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"

        assert(1 == result)

        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            print "modify action from transit to trap"

        sai_thrift_set_fdb_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_TRAP)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_TRAP)
      
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)
            print "TODO"
            """
            TODO:check packet passed to cpu
            """
        finally:
            print "=====test done======"
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)


@group('l2')
class L2FdbGetSetEntryActionTransitToLog(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry action from Transit to log,verify fdb set fdb action attribute
        steps:
	step1:create a  fdb entry,the action is transit
	step2:check the entry action is right	          
	step3:set fdb action from Transit to Log
	step4:check the entry type is right
	step5:clean up
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        result = 0;
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_TRANSIT

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, mac_action, SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_TRANSIT)
        
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)
        

        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            print "modify action from transit to log"

        sai_thrift_set_fdb_action(self.client, vlan_oid, mac2,  SAI_PACKET_ACTION_LOG)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_LOG)
      
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
            """
            TODO:check packet passed to cpu
            """
        finally:
           
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
	    sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('l2')
class L2FdbGetSetEntryActionTransitToDeny(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry action from Transit to Deny,verify fdb set fdb action attribute
        steps:
	step1:create a  fdb entry,the action is Transit
	step2:check the entry action is right	          
	step3:set fdb action from Transit to Deny
	step4:check the entry type is right
	step5:clean up
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        result = 0;
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_TRANSIT

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, mac_action, SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_TRANSIT)
        
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)
        

        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            print "modify action from transit to deny"

        sai_thrift_set_fdb_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_DENY)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_DENY)
      
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)
            """
            TODO:check packet not passed to cpu
            """
        finally:
           
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('l2')
class L2FdbGetSetEntryActionLogToDeny(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry action from Log to Deny,verify fdb set fdb action attribute
        steps:
	step1:create a  fdb entry,the action is Log
	step2:check the entry action is right	          
	step3:set fdb action from Log to Deny
	step4:check the entry type is right
	step5:clean up
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        result = 0;
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, SAI_PACKET_ACTION_LOG, SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_LOG)
        
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)
        

        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
            """
            TODO:check packet passed to cpu
            """
            
        finally:
            print "modify action from log to deny"

        sai_thrift_set_fdb_action(self.client, vlan_oid, mac2,  SAI_PACKET_ACTION_DENY)
        result = sai_thrift_check_fdb_attribtue_action(self.client, vlan_oid, mac2, SAI_PACKET_ACTION_DENY)
      
        if(1 == result):
            print "fdb entry action is right"
        else:
            print "fdb entry action is wrong"
        assert(1 == result)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet(self, exp_pkt, 1, default_time_out)
            """
            TODO:check packet not passed to cpu
            """
        finally:
           
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('l2')
class L2FdbGetSetEntryPort(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set fdb entry port from port2 to port3,verify fdb set fdb port attribute
        steps:
	step1:create a  fdb entry,the port is port2
	step2:check the entry action is right	          
	step3:set fdb entry port from port2 to port3
	step4:check the entry port is right
	step5:clean up
	"""
        print
        print "Sending L2 packet - port 1 -> port 2 [trunk vlan=10])"
        switch_init(self.client)
        result = 0;
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac_action = SAI_PACKET_ACTION_TRANSIT

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb_new(self.client, vlan_oid, mac2, port2, mac_action, SAI_FDB_ENTRY_TYPE_STATIC)
        result = sai_thrift_check_fdb_attribtue_port(self.client, vlan_oid, mac2, port2)
        
        if(1 == result):
            print "fdb entry port is right"
        else:
            print "fdb entry port is wrong"
        assert(1 == result)
        

        pkt = simple_tcp_packet(eth_dst= mac2,
                                eth_src= mac1,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=10,
                                ip_id=102,
                                ip_ttl=64,
                                pktlen=104)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1])
        finally:
            print "modify port from port2 to port3"

        sai_thrift_set_fdb_port(self.client, vlan_oid, mac2, port3)
        result = sai_thrift_check_fdb_attribtue_port(self.client, vlan_oid, mac2, port3)
      
        if(1 == result):
            print "fdb entry port is right"
        else:
            print "fdb entry port is wrong"
        assert(1 == result)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [2])
        finally:
           
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port3)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)


@group('l2')
class L2VlanGetSetMaxLearnedAddress(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        set vlan max learned address ,verify vlan set  attribute
        steps:
	step1:set max learned address to be 1
	step2:send two packet with different src mac	          
	step3:can get the dynamic fdb entry of the first packet but can not get the secend's
	step4:clean up
	"""
	print "start test "
        switch_init(self.client)
        vlan_id = 10
        limit_num = 1
        result = 0
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        print "vlan_oid:%x" %vlan_oid
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)
        self.client.sai_thrift_set_port_attribute(port3, attr)
        
        attr_value = sai_thrift_attribute_value_t(u32=limit_num)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_MAX_LEARNED_ADDRESSES, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)

        result = sai_thrift_vlan_check_max_learned_address(self.client, vlan_oid, limit_num)
        assert(1 == result)
        pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt = simple_tcp_packet(eth_dst=mac2,
                                eth_src=mac1,
                                ip_dst='10.0.0.1',
                                ip_id=107,
                                ip_ttl=64)

        pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.2',
                                ip_id=107,
                                ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.2',
                                ip_id=107,
                                ip_ttl=64)

        warmboot(self.client)
        try:
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1, 2])
            send_packet(self, 1, str(pkt1))
            verify_packets(self, exp_pkt1, [0])
            result = sai_thrift_check_fdb_exist(self.client,vlan_oid, mac1)
            if(1 == result):
                print "fdb entry exist"
            else:
                print "fdb entry not exist"
            assert(1 == result)

            result = sai_thrift_check_fdb_exist(self.client,vlan_oid, mac2)
            if(1 == result):
                print "fdb entry exist"
            else:
                print "fdb entry not exist"
            assert(0 == result)
            
            send_packet(self, 0, str(pkt))
            verify_packets(self, exp_pkt, [1, 2])
        finally:
            
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            self.client.sai_thrift_set_port_attribute(port3, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan(vlan_oid)

class L2LagSetGetDropTagAttrTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        switch_init(self.client)
        vlan_id = 10
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD
        hash_id_lag = 0x201C
        field_list = [SAI_NATIVE_HASH_FIELD_DST_IP]

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

        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_LAG_ATTR_DROP_UNTAGGED, value=attr_value)
        self.client.sai_thrift_set_lag_attribute(lag_id1, attr)

        result = sai_thrift_lag_check_drop_untagged(self.client,lag_id1,1)
        if(1 == result):
            print "check success"
        else:
            print "check fail"
        assert(1 == result)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port4, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, lag_id1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port4, mac_action)
        
        # set lag hash: hash field default value to  ip_da
        # Hash field list
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
                print "rcv_idx:%u" %rcv_idx
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
            verify_no_packet(self, exp_pkt, 3, default_time_out)
            print "Sending packet port 2 (lag member) -> port 4"
            send_packet(self, 1, str(pkt))
            verify_no_packet(self, exp_pkt, 3, default_time_out)
            print "Sending packet port 3 (lag member) -> port 4"
            send_packet(self, 2, str(pkt))
            verify_no_packet(self, exp_pkt, 3, default_time_out)
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
           
class L2PortTransmitPropertyTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):

        print
        print "start test"
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 20
        vlan_id3 = 30
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        mac3 = '00:30:30:30:30:30'
        mac4 = '00:40:40:40:40:40'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)
        vlan_oid3 = sai_thrift_create_vlan(self.client, vlan_id3)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_oid1, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member4 = sai_thrift_create_vlan_member(self.client, vlan_oid2, port3, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id1)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        
        attr_value = sai_thrift_attribute_value_t(u16=vlan_id2)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port2, attr)
	
        attr_value = sai_thrift_attribute_value_t(u16=vlan_id3)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port3, attr)

        sai_thrift_create_fdb(self.client, vlan_oid1, mac2, port3, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid2, mac4, port3, mac_action)
                                
        warmboot(self.client)
        try:
            list = self.client.sai_thrift_get_port_attribute(port1)
            for each in list.attr_list:
                if each.id == SAI_PORT_ATTR_PKT_TX_ENABLE:
                    print "SAI_PORT_ATTR_PKT_TX_ENABLE: %s" % ("Ture" if each.value.booldata else "False")
                    assert (each.value.booldata == True)
            attr_value = sai_thrift_attribute_value_t(booldata=False)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PKT_TX_ENABLE, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            list = self.client.sai_thrift_get_port_attribute(port1)
            for each in list.attr_list:
                if each.id == SAI_PORT_ATTR_PKT_TX_ENABLE:
                    print "SAI_PORT_ATTR_PKT_TX_ENABLE: %s" % ("Ture" if each.value.booldata else "False")
                    assert (each.value.booldata == False)
            attr_value = sai_thrift_attribute_value_t(booldata=True)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PKT_TX_ENABLE, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            list = self.client.sai_thrift_get_port_attribute(port1)
            for each in list.attr_list:
                if each.id == SAI_PORT_ATTR_PKT_TX_ENABLE:
                    print "SAI_PORT_ATTR_PKT_TX_ENABLE: %s" % ("Ture" if each.value.booldata else "False")
                    assert (each.value.booldata == True)
        finally:
            sai_thrift_delete_fdb(self.client, vlan_oid1, mac2, port3)
            sai_thrift_delete_fdb(self.client, vlan_oid2, mac4, port3)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid1)
            sai_thrift_flush_fdb_by_vlan(self.client, vlan_oid2)

            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            self.client.sai_thrift_set_port_attribute(port3, attr)

            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan_member(vlan_member3)
            self.client.sai_thrift_remove_vlan_member(vlan_member4)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)
            self.client.sai_thrift_remove_vlan(vlan_oid3)

