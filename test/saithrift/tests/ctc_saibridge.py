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

@group('Bridge')
class BridgeCreate1DBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)

            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_TYPE:
                    print "type %d" %a.value.s32
                    if SAI_BRIDGE_TYPE_1D != a.value.s32:
                        raise NotImplementedError()

        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeRemove1DBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        self.client.sai_thrift_remove_bridge(bridge_id)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            assert (attrs.status == SAI_STATUS_SUCCESS)

        finally:
            print "Success!"

class BridgeGet1DBridgeTypeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_TYPE:
                    print "1d bridgetype %d" %a.value.s32
                    if SAI_BRIDGE_TYPE_1Q == a.value.s32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeGet1QBridgeTypeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_attribute(switch.default_1q_bridge)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_TYPE:
                    print "default 1q bridge type %d" %a.value.s32
                    if SAI_BRIDGE_TYPE_1D == a.value.s32:
                        raise NotImplementedError()
        finally:
            print "default 1q bridge type test!\n"

class BridgeMaxLearnAddressBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_MAX_LEARNED_ADDRESSES:
                    print "Max learn address %d" %a.value.u32
                    if 0 != a.value.u32:
                        raise NotImplementedError()
             
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            attr_value = sai_thrift_attribute_value_t(u32=20)
            attr = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_MAX_LEARNED_ADDRESSES, value=attr_value)
            self.client.sai_thrift_set_bridge_attribute(bridge_id, attr)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_MAX_LEARNED_ADDRESSES:
                    print "Max learn address %d" %a.value.u32
                    if 20 != a.value.u32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeLearnDisableBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_LEARN_DISABLE:
                    print "Learn Disable %d" %a.value.booldata
                    if 0 != a.value.booldata:
                        raise NotImplementedError()
             
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            attr_value = sai_thrift_attribute_value_t(booldata=1)
            attr = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_LEARN_DISABLE, value=attr_value)
            self.client.sai_thrift_set_bridge_attribute(bridge_id, attr)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_LEARN_DISABLE:
                    print "Learn Disable %d" %a.value.booldata
                    if 1 != a.value.booldata:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeUnknownUnicastFloodBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_UNKNOWN_UNICAST_FLOOD_CONTROL_TYPE:
                    print "unknown unicast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_SUB_PORTS != a.value.s32:
                        raise NotImplementedError()
             
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            attr_value = sai_thrift_attribute_value_t(s32=SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE)
            attr = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_UNKNOWN_UNICAST_FLOOD_CONTROL_TYPE, value=attr_value)
            self.client.sai_thrift_set_bridge_attribute(bridge_id, attr)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_UNKNOWN_UNICAST_FLOOD_CONTROL_TYPE:
                    print "unknown unicast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE != a.value.s32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeUnknownMcastFloodBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_UNKNOWN_MULTICAST_FLOOD_CONTROL_TYPE:
                    print "unknown mcast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_SUB_PORTS != a.value.s32:
                        raise NotImplementedError()
             
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            attr_value = sai_thrift_attribute_value_t(s32=SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE)
            attr = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_UNKNOWN_MULTICAST_FLOOD_CONTROL_TYPE, value=attr_value)
            self.client.sai_thrift_set_bridge_attribute(bridge_id, attr)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_UNKNOWN_MULTICAST_FLOOD_CONTROL_TYPE:
                    print "unknown mcast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE != a.value.s32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeBcastFloodBridgeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)

        warmboot(self.client)
        try:
            bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_BROADCAST_FLOOD_CONTROL_TYPE:
                    print "unknown unicast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_SUB_PORTS != a.value.s32:
                        raise NotImplementedError()
             
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            attr_value = sai_thrift_attribute_value_t(s32=SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE)
            attr = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_BROADCAST_FLOOD_CONTROL_TYPE, value=attr_value)
            self.client.sai_thrift_set_bridge_attribute(bridge_id, attr)
            attrs = self.client.sai_thrift_get_bridge_attribute(bridge_id)
            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_ATTR_BROADCAST_FLOOD_CONTROL_TYPE:
                    print "unknown unicast flood %d" %a.value.s32
                    if SAI_BRIDGE_FLOOD_CONTROL_TYPE_NONE != a.value.s32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeSubPortNumTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print ""
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 15
        vlan_id3 = 20
        vlan_id4 = 25
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]

        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'

        bridge_id1 = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        bridge_id2 = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        
        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port1, bridge_id1, vlan_id1)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id1, vlan_id2)
        bport3_id = sai_thrift_create_bridge_sub_port(self.client, port3, bridge_id1, vlan_id3)
        bport4_id = sai_thrift_create_bridge_sub_port(self.client, port4, bridge_id2, vlan_id4)

        warmboot(self.client)
        try:
            ret = self.client.sai_thrift_get_bridge_port_list(bridge_id1)
            assert (ret.status == SAI_STATUS_SUCCESS)

            index = len(ret.data.objlist.object_id_list)
            print "Bridge id1 %x count %d\n" %(bridge_id1,index)
            for bp in ret.data.objlist.object_id_list:
                print "port id %x\n" %bp

            if 3 != index:
                raise NotImplementedError()

        finally:
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port1)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port2)
            sai_thrift_remove_bridge_sub_port(self.client, bport3_id, port3)
            sai_thrift_remove_bridge_sub_port(self.client, bport4_id, port4)
            self.client.sai_thrift_remove_bridge(bridge_id1)
            self.client.sai_thrift_remove_bridge(bridge_id2)
         
class BridgeSubPortFloodTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print ""
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 15
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        port4 = port_list[3]

        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'

        sai_thrift_vlan_remove_all_ports(self.client, switch.default_vlan.oid)

        vlan_oid1 = sai_thrift_create_vlan(self.client, vlan_id1)
        vlan_oid2 = sai_thrift_create_vlan(self.client, vlan_id2)

        bridge_id1 = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        bridge_id2 = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)

        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port1, bridge_id1, vlan_id1)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id1, vlan_id2)
        bport3_id = sai_thrift_create_bridge_sub_port(self.client, port3, bridge_id2, vlan_id1)
        bport4_id = sai_thrift_create_bridge_sub_port(self.client, port4, bridge_id2, vlan_id2)

        pkt1 = simple_tcp_packet(eth_dst=mac1,
                                eth_src=mac2,
                                ip_dst='10.0.0.1',
                                ip_id=102,
                                ip_ttl=64,
                                dl_vlan_enable=True,
                                vlan_vid=vlan_id1)

        pkt2 = simple_tcp_packet(eth_dst=mac1,
                                 eth_src=mac2,
                                 ip_dst='10.0.0.1',
                                 ip_id=102,
                                 ip_ttl=64,
                                 dl_vlan_enable=True,
                                 vlan_vid=vlan_id2)

        warmboot(self.client)
        try:
            print "Sending packet to Sub-port [port 1 : vlan {}] (bridge 1)".format(vlan_id1)
            send_packet(self, 0, str(pkt1))
            verify_packets(self, pkt2, [1])
            print "Success"
            print "Sending packet to Sub-port [port 3 : vlan {}] (bridge 2)".format(vlan_id1)
            send_packet(self, 2, str(pkt1))
            verify_packets(self, pkt2, [3])
            print "Success"

        finally:
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port1)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port2)
            sai_thrift_remove_bridge_sub_port(self.client, bport3_id, port3)
            sai_thrift_remove_bridge_sub_port(self.client, bport4_id, port4)
            self.client.sai_thrift_remove_bridge(bridge_id1)
            self.client.sai_thrift_remove_bridge(bridge_id2)
            self.client.sai_thrift_remove_vlan(vlan_oid1)
            self.client.sai_thrift_remove_vlan(vlan_oid2)

            for port in sai_port_list:
                sai_thrift_create_vlan_member(self.client, switch.default_vlan.oid, port, SAI_VLAN_TAGGING_MODE_UNTAGGED)

                
@group('BridgePort')
class BridgeGetBridgePortTypeTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 15
        port1 = port_list[0]
        port2 = port_list[1]

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port1, bridge_id, vlan_id1)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id, vlan_id2)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_port_attribute(bport1_id)

            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_PORT_ATTR_TYPE:
                    print "type %d" %a.value.s32
                    if SAI_BRIDGE_PORT_TYPE_SUB_PORT != a.value.s32:
                        raise NotImplementedError()

        finally:
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port1)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port2)
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeGetBridgePortPortIdTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 15
        port1 = port_list[0]
        port2 = port_list[1]

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port1, bridge_id, vlan_id1)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id, vlan_id2)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_port_attribute(bport1_id)

            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_PORT_ATTR_PORT_ID:
                    print "gport id %x" %a.value.oid
                    if port1 != a.value.oid:
                        raise NotImplementedError()

        finally:
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port1)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port2)
            self.client.sai_thrift_remove_bridge(bridge_id)

class BridgeGetBridgePortVlanIdTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Bridge Create and Remove test. Verify 1D Bridge. 
        Steps:
        1. create 1D Bridge
        2. Test Bridge
        3. clean up.
        """
        print ""
        switch_init(self.client)
        vlan_id1 = 10
        vlan_id2 = 15
        port1 = port_list[0]
        port2 = port_list[1]

        bridge_id = sai_thrift_create_bridge(self.client, SAI_BRIDGE_TYPE_1D)
        bport1_id = sai_thrift_create_bridge_sub_port(self.client, port1, bridge_id, vlan_id1)
        bport2_id = sai_thrift_create_bridge_sub_port(self.client, port2, bridge_id, vlan_id2)
        
        warmboot(self.client)
        try:
            attrs = self.client.sai_thrift_get_bridge_port_attribute(bport1_id)

            for a in attrs.attr_list:
                if a.id == SAI_BRIDGE_PORT_ATTR_VLAN_ID:
                    print "vlan id %x" %a.value.u16
                    if vlan_id1 != a.value.u16:
                        raise NotImplementedError()

        finally:
            sai_thrift_remove_bridge_sub_port(self.client, bport1_id, port1)
            sai_thrift_remove_bridge_sub_port(self.client, bport2_id, port2)
            self.client.sai_thrift_remove_bridge(bridge_id)
 