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
Thrift SAI interface PORT tests
"""
import socket
from switch import *
import sai_base_test

@group('port')
class PortMtuTest(sai_base_test.ThriftInterfaceDataPlane):
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
        
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        port4 = port_list[4]
        port5 = port_list[5]
        port6 = port_list[6]
        port7 = port_list[7]
        port8 = port_list[8]
        mtu = 1514
        mtu0 = 1514
        mtu1 = 9500
        mtu2 = 9400
        mtu3 = 9300
        mtu4 = 9200
        mtu5 = 9100
        mtu6 = 9000
        mtu7 = 8900
        mtu8 = 8800
        
        warmboot(self.client)
        try:
            attr_value = sai_thrift_attribute_value_t(u32=mtu0)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port0, attr)
            attrs = self.client.sai_thrift_get_port_attribute(port0)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_PORT_ATTR_MTU:
                    print "port 0x%lx mtu %d" %(port0, a.value.u32)
                    if mtu0 != a.value.u32:
                        raise NotImplementedError()
            attr_value = sai_thrift_attribute_value_t(u32=mtu1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            attrs = self.client.sai_thrift_get_port_attribute(port1)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_PORT_ATTR_MTU:
                    print "port 0x%lx mtu %d" %(port1, a.value.u32)
                    if mtu1 != a.value.u32:
                        raise NotImplementedError()
            attr_value = sai_thrift_attribute_value_t(u32=mtu2)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            attrs = self.client.sai_thrift_get_port_attribute(port2)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_PORT_ATTR_MTU:
                    print "port 0x%lx mtu %d" %(port2, a.value.u32)
                    if mtu2 != a.value.u32:
                        raise NotImplementedError()
        finally:
            attr_value = sai_thrift_attribute_value_t(u32=mtu)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_MTU, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port0, attr)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)

class PortIsolationAttrTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print "start test"
        switch_init(self.client)
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        port_list_isolation = [port1, port2, port3]
        
        port_egress_list = sai_thrift_object_list_t(count=len(port_list_isolation), object_id_list=port_list_isolation)
        attr_value = sai_thrift_attribute_value_t(objlist=port_egress_list)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST, value=attr_value)
        print "port attr id %d" %(SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST)
        self.client.sai_thrift_set_port_attribute(port0, attr)
        
        warmboot(self.client)
        
        try:
            attrs = self.client.sai_thrift_get_port_attribute(port0)
            print "success to get packet attribute"
            for a in attrs.attr_list:
                if a.id == SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST:
                    print "port 0x%lx block count %d" %(port0, a.value.objlist.count)
                    if 3 != a.value.objlist.count:
                        raise NotImplementedError()
        finally:
            port_list_isolation = []
            port_egress_list = sai_thrift_object_list_t(count=len(port_list_isolation), object_id_list=port_list_isolation)
            attr_value = sai_thrift_attribute_value_t(objlist=port_egress_list)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port0, attr)
            
class PortIsolationPacketTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print "start test"
        switch_init(self.client)
        mac1 = '00:10:10:10:10:10'
        mac2 = '00:20:20:20:20:20'
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        port_list_isolation = [port1, port2, port3]
        
        port_egress_list = sai_thrift_object_list_t(count=len(port_list_isolation), object_id_list=port_list_isolation)
        attr_value = sai_thrift_attribute_value_t(objlist=port_egress_list)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST, value=attr_value)
        print "port attr id %d" %(SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST)
        self.client.sai_thrift_set_port_attribute(port0, attr)
        
        warmboot(self.client)
        
        pkt = simple_tcp_packet(eth_dst=mac2,
                    eth_src=mac1,
                    ip_dst='10.0.0.1',
                    dl_vlan_enable=False,
                    ip_id=101,
                    ip_ttl=64)
        try:
            send_packet(self, 0, str(pkt))
            verify_no_packet_any(self, pkt, [1,2,3])
        finally:
            port_list_isolation = []
            port_egress_list = sai_thrift_object_list_t(count=len(port_list_isolation), object_id_list=port_list_isolation)
            attr_value = sai_thrift_attribute_value_t(objlist=port_egress_list)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_BLOCK_PORT_LIST, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port0, attr)
            
           