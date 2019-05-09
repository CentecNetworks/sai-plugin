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

@group('mirror')
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
    
class LocalMirrorCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Local Mirror Create Test. Verify mirror port and mirror type. 
        Steps:
        1. create local mirror with dst port 3 and mirror type SAI_MIRROR_SESSION_TYPE_LOCAL
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        truncate_size = 100 
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = 0x%x" %ingress_localmirror_id
        
        warmboot(self.client)
        try:
            print "Set mirror session: truncate_size = 100"
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %monitor_port
                    print "get monitor_port = %d" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)
            
class LocalMirrorRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Local Mirror Remove Test. 
        Steps:
        1. create Local Mirror
        2. remove Local Mirror
        3. get attribute and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = %d" %ingress_localmirror_id
              
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            print "Remove mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3"
            status=self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)
            print "sai_thrift_remove_mirror_session; status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
        finally:
            print "Success!"
            
class LocalMirrorSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Local Mirror Set Test. Verify mirror port ,mirror type and truncate_size. 
        Steps:
        1. create local mirror with dst port 3 and mirror type SAI_MIRROR_SESSION_TYPE_LOCAL
        2. get attribute
        3. set attribute
        4. get attribute
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        port2 = port_list[2]
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        truncate_size = 100 
        sample_rate = 7 
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = 0x%lx" %ingress_localmirror_id
        
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%lx" %monitor_port
                    print "get monitor_port = 0x%lx" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
            print "Set mirror session: monitor_port = 2"
            attr_value = sai_thrift_attribute_value_t(oid=port2)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: truncate_size = 100"
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: sample_rate = 1/8"
            attr_value = sai_thrift_attribute_value_t(u32=sample_rate)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SAMPLE_RATE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 2, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = 0x%lx" %port2
                    print "get monitor_port = 0x%lx" %a.value.oid
                    if port2 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SAMPLE_RATE: 
                    print "set sample_rate = %d" %sample_rate
                    print "get sample_rate = %d" %a.value.u32
                    if sample_rate != a.value.u32:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)

class RspanMirrorCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Remote Mirror Create Test. Verify mirror port and mirror type. 
        Steps:
        1. create remote mirror with dst port 3 and mirror type SAI_MIRROR_SESSION_TYPE_REMOTE
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        vlan_id = 10
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE
        monitor_port = port3
        truncate_size = 100 
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3 "
        ingress_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            vlan_id, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_remotemirror_id = %d" %ingress_remotemirror_id
        
        warmboot(self.client)
        try:
            print "Set mirror session: truncate_size = 100"
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %monitor_port
                    print "get monitor_port = %d" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_VLAN_ID: 
                    print "set vlan_id = %d" %vlan_id
                    print "get vlan_id = %d" %a.value.u16
                    if vlan_id != a.value.u16:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_remotemirror_id)
  
class RspanMirrorRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Rspan Mirror Remove Test. 
        Steps:
        1. create Remote Mirror
        2. remove Remote Mirror
        3. get attribute and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE
        monitor_port = port3
        vlan_id = 10
        
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3 "
        ingress_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            vlan_id, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_remotemirror_id = %d" %ingress_remotemirror_id
              
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_remotemirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            print "Remove mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3"
            status=self.client.sai_thrift_remove_mirror_session(ingress_remotemirror_id)
            print "sai_thrift_remove_mirror_session; status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_remotemirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
        finally:
            print "Success!"
  
class RspanMirrorSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Remote Mirror Set Test. Verify mirror port ,mirror type,truncate_size and vlan_id. 
        Steps:
        1. create Remote mirror with dst port 3 and mirror type SAI_MIRROR_SESSION_TYPE_REMOTE
        2. get attribute
        3. set attribute
        4. get attribute
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port3 = port_list[3]
        port2 = port_list[2]
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE
        monitor_port = port3
        truncate_size = 100 
        vlan_id_create = 10
        vlan_id_set = 20
        
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 3 "
        ingress_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            vlan_id_create, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_remotemirror_id = %d" %ingress_remotemirror_id
        
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = %d" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = %d" %monitor_port
                    print "get monitor_port = %d" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_VLAN_ID: 
                    print "create vlan_id_create = %d" %vlan_id_create
                    print "get vlan_id_create = %d" %a.value.u16
                    if vlan_id_create != a.value.u16:
                        raise NotImplementedError()
            print "Set mirror session: monitor_port = %d" %port2
            attr_value = sai_thrift_attribute_value_t(oid=port2)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: truncate_size = %d" %truncate_size
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: vlan_id = %d" %vlan_id_set
            attr_value = sai_thrift_attribute_value_t(u16=vlan_id_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_ID, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_REMOTE, monitor_port = ptf_intf 2, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %port2
                    print "get monitor_port = %d" %a.value.oid
                    if port2 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_VLAN_ID: 
                    print "set vlan_id_set = %d" %vlan_id_set
                    print "get vlan_id_set = %d" %a.value.u16
                    if vlan_id_set != a.value.u16:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_remotemirror_id)

class ERspanMirrorCreateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Enhanced Remote Mirror Create Test. Verify mirror port and mirror type. 
        Steps:
        1. create Enhanced remote mirror with dst port 3 and mirror type SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE
        2. get attribute and check
        3. clean up.
        """
        print ""
        switch_init(self.client)
    
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac3='00:00:00:00:00:33'
        mac2='00:00:00:00:00:22'
        monitor_port=port1
        source_port=port2
        truncate_size = 100 
        mirror_type=SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE
        src_mac='00:00:00:00:11:22'
        dst_mac='00:00:00:00:11:33'
        encap_type=SAI_ERSPAN_ENCAPSULATION_TYPE_MIRROR_L3_GRE_TUNNEL
        ip_version=0x4
        tos=0x3c
        ttl=0x20
        #gre_type=0x88be  buff = pack("!h", i16) error: 'h' format requires -32768 <= number <= 32767
        #gre_type=0x88be
        gre_type=0x22eb
        src_ip='17.18.19.0'
        dst_ip='33.19.20.0'
        addr_family=0
        
        # setup local mirror session
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d " %monitor_port
        ingress_enhanced_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None, None, 
            src_mac=src_mac,dst_mac=dst_mac,src_ip=src_ip,dst_ip=dst_ip,encap_type=encap_type,iphdr_version=ip_version,ttl=ttl,tos=tos,gre_type=gre_type)
        print "ingress_enhanced_remotemirror_id = %d" %ingress_enhanced_remotemirror_id      
        
        warmboot(self.client)
        try:
            print "Set mirror session: truncate_size = %d" %truncate_size
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = ptf_intf 3, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_enhanced_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
        
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %monitor_port
                    print "get monitor_port = %d" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_ERSPAN_ENCAPSULATION_TYPE:
                    print "set encap_type = %d" %encap_type
                    print "get encap_type = %d" %a.value.s32
                    if encap_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_IPHDR_VERSION: 
                    print "set ip_version = %d" %ip_version
                    print "get ip_version = %d" %a.value.u8
                    if ip_version != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TOS: 
                    print "set tos = %d" %tos
                    print "get tos = %d" %a.value.u8
                    if tos != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TTL: 
                    print "set ttl = %d" %ttl
                    print "get ttl = %lu" %a.value.u8
                    if ttl != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS: 
                    print "set src_ip = %s" %src_ip 
                    print "get src_ip = %s" %a.value.ipaddr.addr.ip4
                    if src_ip != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS: 
                    print "set dst_ip = %s" %dst_ip
                    print "get dst_ip = %s" %a.value.ipaddr.addr.ip4
                    if dst_ip != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS: 
                    print "set src_mac = %s" %src_mac
                    print "get src_mac = %s" %a.value.mac
                    if src_mac != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS: 
                    print "set dst_mac = %s" %dst_mac
                    print "get dst_mac = %s" %a.value.mac
                    if dst_mac != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE: # gg error
                    print "set gre_type = %d" %gre_type
                    print "get gre_type = %d" %a.value.u16
                    if gre_type != a.value.u16:
                        raise NotImplementedError()
        
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_enhanced_remotemirror_id)    
          

class ERspanMirrorRemoveTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        ERspan Mirror Remove Test. 
        Steps:
        1. create Enhanced Remote Mirror
        2. remove Enhanced Remote Mirror
        3. get attribute and check
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac3='00:00:00:00:00:33'
        mac2='00:00:00:00:00:22'
        monitor_port=port1
        source_port=port2
        truncate_size = 100 
        mirror_type=SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE
        src_mac='00:00:00:00:11:22'
        dst_mac='00:00:00:00:11:33'
        encap_type=SAI_ERSPAN_ENCAPSULATION_TYPE_MIRROR_L3_GRE_TUNNEL
        ip_version=0x4
        tos=0x3c
        ttl=0x20
        #gre_type=0x88be  buff = pack("!h", i16) error: 'h' format requires -32768 <= number <= 32767
        gre_type=0x22eb
        src_ip='17.18.19.0'
        dst_ip='33.19.20.0'
        addr_family=0
        
        # setup local mirror session
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d " %monitor_port
        ingress_enhanced_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None, None, 
            src_mac=src_mac,dst_mac=dst_mac,src_ip=src_ip,dst_ip=dst_ip,encap_type=encap_type,iphdr_version=ip_version,ttl=ttl,tos=tos,gre_type=gre_type)
        print "ingress_enhanced_remotemirror_id = %d" %ingress_enhanced_remotemirror_id    
              
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_enhanced_remotemirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            print "Remove mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d" %monitor_port
            status=self.client.sai_thrift_remove_mirror_session(ingress_enhanced_remotemirror_id)
            print "sai_thrift_remove_mirror_session; status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_enhanced_remotemirror_id)
            print "sai_thrift_get_mirror_attribute; status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_ITEM_NOT_FOUND)
        finally:
            print "Success!"
            
class ERspanMirrorSetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        """
        Enhanced Remote Mirror Set Test. Verify mirror port ,mirror type,truncate_size... 
        Steps:
        1. create Enhanced Remote mirror 
        2. get attribute
        3. set attribute
        4. get attribute
        5. clean up.
        """
        print ""
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        src_mac_set='00:00:00:00:00:33'
        dst_mac_set='00:00:00:00:00:22'
        monitor_port=port1
        source_port=port2
        truncate_size = 100 
        mirror_type=SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE
        src_mac='00:00:00:00:11:22'
        dst_mac='00:00:00:00:11:33'
        encap_type=SAI_ERSPAN_ENCAPSULATION_TYPE_MIRROR_L3_GRE_TUNNEL
        ip_version=0x4
        ip_version_set=0x4
        tos=0x3c
        ttl=0x20
        tos_set=0x3d
        ttl_set=0x2d
        #gre_type=0x88be  buff = pack("!h", i16) error: 'h' format requires -32768 <= number <= 32767
        gre_type=0x22eb
        gre_type_set=0x2222
        src_ip='17.18.19.0'
        dst_ip='33.19.20.0'
        src_ip_set='11.12.13.14'
        dst_ip_set='21.22.23.24'
        addr_family=0
        
        # setup local mirror session
        print "Create mirror session: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d " %monitor_port
        ingress_enhanced_remotemirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None, None, 
            src_mac=src_mac,dst_mac=dst_mac,src_ip=src_ip,dst_ip=dst_ip,encap_type=encap_type,iphdr_version=ip_version,ttl=ttl,tos=tos,gre_type=gre_type)
        print "ingress_enhanced_remotemirror_id = %d" %ingress_enhanced_remotemirror_id    
        
        warmboot(self.client)
        try:
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_enhanced_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = %d" %monitor_port
                    print "get monitor_port = %d" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
            print "Set mirror session: monitor_port = %d" %port2
            attr_value = sai_thrift_attribute_value_t(oid=port2)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: truncate_size = %d" %truncate_size
            attr_value = sai_thrift_attribute_value_t(u16=truncate_size)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: src_mac_set = %s" %src_mac_set
            attr_value = sai_thrift_attribute_value_t(mac=src_mac_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: dst_mac_set = %s" %dst_mac_set
            attr_value = sai_thrift_attribute_value_t(mac=dst_mac_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            #source ip
            print "Set mirror session: src_ip_set = %s" %src_ip_set
            addr = sai_thrift_ip_t(ip4=src_ip_set)
            src_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            attribute5_value = sai_thrift_attribute_value_t(ipaddr=src_ip_addr)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS,
                                            value=attribute5_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #dst ip
            print "Set mirror session: dst_ip_set = %s" %dst_ip_set
            addr = sai_thrift_ip_t(ip4=dst_ip_set)
            dst_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            attribute6_value = sai_thrift_attribute_value_t(ipaddr=dst_ip_addr)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS,
                                            value=attribute6_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: ip_version_set = %s" %ip_version_set
            attr_value = sai_thrift_attribute_value_t(u8=ip_version_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_IPHDR_VERSION, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: tos_set = %s" %tos_set
            attr_value = sai_thrift_attribute_value_t(u8=tos_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TOS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: ttl_set = %s" %ttl_set
            attr_value = sai_thrift_attribute_value_t(u8=ttl_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TTL, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Set mirror session: gre_type_set = %s" %gre_type_set
            attr_value = sai_thrift_attribute_value_t(u16=gre_type_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_enhanced_remotemirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = ptf_intf 2, truncate_size = 100"
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_enhanced_remotemirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %port2
                    print "get monitor_port = %d" %a.value.oid
                    if port2 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TRUNCATE_SIZE: 
                    print "set truncate_size = %d" %truncate_size
                    print "get truncate_size = %d" %a.value.u16
                    if truncate_size != a.value.u16:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS: 
                    print "set src_mac_set = %s" %src_mac_set
                    print "get src_mac_set = %s" %a.value.mac
                    if src_mac_set != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS: 
                    print "set dst_mac_set = %s" %dst_mac_set
                    print "get dst_mac_set = %s" %a.value.mac
                    if dst_mac_set != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS: 
                    print "set src_ip_set = %s" %src_ip_set
                    print "get src_ip_set = %s" %a.value.ipaddr.addr.ip4
                    if src_ip_set != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS: 
                    print "set dst_ip_set = %s" %dst_ip_set
                    print "get dst_ip_set = %s" %a.value.ipaddr.addr.ip4
                    if dst_ip_set != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_IPHDR_VERSION: 
                    print "set ip_version_set = %d" %ip_version_set
                    print "get ip_version_set = %d" %a.value.u8
                    if ip_version_set != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TOS: 
                    print "set tos_set = %d" %tos_set
                    print "get tos_set = %d" %a.value.u8
                    if tos_set != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TTL: 
                    print "set ttl_set = %d" %ttl_set
                    print "get ttl_set = %d" %a.value.u8
                    if ttl_set != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE: 
                    print "set gre_type_set = %d" %gre_type_set
                    print "get gre_type_set = %d" %a.value.u16
                    if gre_type_set != a.value.u16:
                        raise NotImplementedError()
        finally:
            self.client.sai_thrift_remove_mirror_session(ingress_enhanced_remotemirror_id)
            
@group('mirror')
class IngressLocalMirrorSetTestPkt(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 1 -> ptf_intf 2, ptf_intf 3 (local mirror)"
        print "Sending packet ptf_intf 2 -> ptf_intf 1, ptf_intf 3 (local mirror)"

        switch_init(self.client)
        vlan_id = 10
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, port1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)

        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = 0x%lx" %ingress_localmirror_id

        attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=1,object_id_list=[ingress_localmirror_id]))
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)
        
        warmboot(self.client)
        
        try:
            assert ingress_localmirror_id > 0, 'ingress_localmirror_id is <= 0'

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

            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            verify_each_packet_on_each_port(self, [exp_pkt1, pkt1], [2, 3])

            time.sleep(1)

            pkt2 = simple_tcp_packet(eth_dst=mac1,
                eth_src=mac2,
                ip_dst='10.0.0.1',
                ip_src='192.168.0.1',
                vlan_vid=10,
                dl_vlan_enable=True,
                ip_id=102,
                ip_ttl=64,
                pktlen=104)
            exp_pkt2 = simple_tcp_packet(eth_dst=mac1,
                eth_src=mac2,
                ip_dst='10.0.0.1',
                ip_src='192.168.0.1',
                ip_id=102,
                ip_ttl=64,
                pktlen=100)

            print '#### Sending 00:11:11:11:11:11 | 00:22:22:22:22:22 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 2 ####'
            send_packet(self, 2, str(pkt2))
            verify_each_packet_on_each_port(self, [exp_pkt2, pkt2], [1, 3])
            
            ##Get Set Get
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
            print "Set mirror session: monitor_port = 0x%x" %port0
            attr_value = sai_thrift_attribute_value_t(oid=port0)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = %d" %port0
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %port0
                    print "get monitor_port = %d" %a.value.oid
                    if port0 != a.value.oid:
                        raise NotImplementedError()
            
            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            verify_each_packet_on_each_port(self, [exp_pkt1, pkt1], [2, 0])
            
            time.sleep(1)
            
            print '#### Sending 00:11:11:11:11:11 | 00:22:22:22:22:22 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 2 ####'
            send_packet(self, 2, str(pkt2))
            verify_each_packet_on_each_port(self, [exp_pkt2, pkt2], [1, 0])
        finally:
            attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=0,object_id_list=[]))
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)
            
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mirror') 
class ERspan_novlan_monitor_SetTestPkt(sai_base_test.ThriftInterfaceDataPlane):
    '''
    This test performs erspan monitoring
    From port2(source port) we send traffic to port 3
    erspan mirror packets are expected on port 1(monitor port)
    goldengate add mirror id, time stamp 16 bytes; duet2 add mirror id, time stamp 16 bytes; 
    '''
    def runTest(self):
        print       
        switch_init(self.client)
        
        if 'goldengate' == testutils.test_params_get()['chipname']:    # goldengate 
            print "Goldengate not ERspan_novlan_monitor_SetTestPkt, just pass for case"
            return
        
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        mac3='00:00:00:00:00:33'
        mac2='00:00:00:00:00:22'
        monitor_port=port1
        source_port=port2
        mirror_type=SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE
        src_mac='00:00:00:00:11:22'
        dst_mac='00:00:00:00:11:33'
        encap_type=SAI_ERSPAN_ENCAPSULATION_TYPE_MIRROR_L3_GRE_TUNNEL
        ip_version=0x4
        tos=0x3c
        #ttl=0xf0
        ttl=0x22
        #gre_type=0x88be
        gre_type=0x22be
        src_ip='17.18.19.0'
        dst_ip='33.19.20.0'
        addr_family=0
        vlan_remote_id = 3
        mac_action = SAI_PACKET_ACTION_FORWARD  
        
        # set value
        src_mac_set='00:00:00:00:34:56'
        dst_mac_set='00:00:00:00:67:89'
        tos_set=0x3d
        ttl_set=0x2d
        #gre_type=0x88be  buff = pack("!h", i16) error: 'h' format requires -32768 <= number <= 32767
        gre_type_set=0x2222
        src_ip_set='11.12.13.14'
        dst_ip_set='21.22.23.24'        

        # Put ports under test in VLAN 3
        vlan_id = 1
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_remote_oid = sai_thrift_create_vlan(self.client, vlan_remote_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_remote_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member1a = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_remote_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member2a = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3 = sai_thrift_create_vlan_member(self.client, vlan_remote_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        vlan_member3a = sai_thrift_create_vlan_member(self.client, vlan_oid, port3, SAI_VLAN_TAGGING_MODE_TAGGED)
        
        # add self
        sai_thrift_create_fdb(self.client, vlan_remote_oid, mac3, port3, mac_action)
        sai_thrift_create_fdb(self.client, vlan_remote_oid, mac2, port2, mac_action)

        # Remove ports from default VLAN
        self.client.sai_thrift_remove_vlan_member(vlan_member1a)
        self.client.sai_thrift_remove_vlan_member(vlan_member2a)
        self.client.sai_thrift_remove_vlan_member(vlan_member3a)

        # Set PVID
        attr_value = sai_thrift_attribute_value_t(u16=1)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)
        self.client.sai_thrift_set_port_attribute(port3, attr)

        erspanid=sai_thrift_create_mirror_session(self.client,mirror_type=mirror_type,port=monitor_port,vlan=None,vlan_priority=None,vlan_tpid=None,vlan_header_valid=False,src_mac=src_mac,dst_mac=dst_mac,src_ip=src_ip,dst_ip=dst_ip,encap_type=encap_type,iphdr_version=ip_version,ttl=ttl,tos=tos,gre_type=gre_type)
        print "erspanid = 0x%lx" %erspanid
        
        attrb_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=1,object_id_list=[erspanid]))

        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attrb_value)
        self.client.sai_thrift_set_port_attribute(port2, attr)

        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_MIRROR_SESSION, value=attrb_value)
        self.client.sai_thrift_set_port_attribute(port2, attr)

        pkt = simple_tcp_packet(eth_dst='00:00:00:00:00:33',
                                eth_src='00:22:22:22:22:22',
                                ip_dst='10.0.0.1',
                                dl_vlan_enable=True,
                                vlan_vid=3,
                                ip_id=101,
                                ip_ttl=64)

        pkt2 = simple_tcp_packet(eth_dst='00:00:00:00:00:22',
                                eth_src='00:33:33:33:33:33',
                                dl_vlan_enable=True,
                                vlan_vid=3,
                                ip_dst='10.0.0.1',
                                ip_id=101,
                                ip_ttl=64)

        pkt3 = simple_tcp_packet(eth_dst='00:00:00:00:00:22',
                                eth_src='00:33:33:33:33:33',
                                dl_vlan_enable=True,
                                vlan_vid=3,
                                ip_dst='10.0.0.1',
                                ip_id=101,
                                ip_ttl=64)

        exp_pkt1= ipv4_erspan_platform_pkt(pktlen=142,
                                    eth_dst='00:00:00:00:11:33',
                                    eth_src='00:00:00:00:11:22',
                                    ip_id=0,
                                    ip_ttl=0x22,
                                    ip_tos=0xF0,
                                    ip_ihl=5,
                                    ip_src='17.18.19.0',
                                    ip_dst='33.19.20.0',
                                    version=2,
                                    mirror_id=(erspanid & 0x3FFFFFFF),
                                    inner_frame=pkt
                                    )

        exp_pkt2= ipv4_erspan_platform_pkt(pktlen=142,
                                    eth_dst='00:00:00:00:11:33',
                                    eth_src='00:00:00:00:11:22',
                                    ip_id=0,
                                    ip_ttl=0x22,
                                    ip_tos=0xF0,
                                    ip_ihl=5,
                                    ip_src='17.18.19.0',
                                    ip_dst='33.19.20.0',
                                    version=2,
                                    mirror_id=(erspanid & 0x3FFFFFFF),
                                    inner_frame=pkt3
                                    )
                                    
        exp_pkt1_set= ipv4_erspan_platform_pkt(pktlen=142,
                                    eth_dst='00:00:00:00:67:89',
                                    eth_src='00:00:00:00:34:56',
                                    ip_id=0,
                                    ip_ttl=0x2d,
                                    ip_tos=0x3d,
                                    ip_ihl=5,
                                    ip_src='11.12.13.14',
                                    ip_dst='21.22.23.24',
                                    version=2,
                                    mirror_id=(erspanid & 0x3FFFFFFF),
                                    inner_frame=pkt
                                    )

        exp_pkt2_set= ipv4_erspan_platform_pkt(pktlen=142,
                                    eth_dst='00:00:00:00:67:89',
                                    eth_src='00:00:00:00:34:56',
                                    ip_id=0,
                                    ip_ttl=0x2d,
                                    ip_tos=0x3d,
                                    ip_ihl=5,
                                    ip_src='11.12.13.14',
                                    ip_dst='21.22.23.24',
                                    version=2,
                                    mirror_id=(erspanid & 0x3FFFFFFF),
                                    inner_frame=pkt3
                                    )

        m1=Mask(exp_pkt1)
        m1.set_do_not_care_scapy(ptf.packet.IP,'tos')
        m1.set_do_not_care_scapy(ptf.packet.IP,'frag')
        m1.set_do_not_care_scapy(ptf.packet.IP,'flags')
        m1.set_do_not_care_scapy(ptf.packet.IP,'chksum')
        m1.set_do_not_care_scapy(ptf.packet.IP,'id')
        m1.set_do_not_care_scapy(ptf.packet.GRE,'proto')
        m1.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'platf_id')
        m1.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info1')
        m1.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info2')
            
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'span_id')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'timestamp')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'sgt_other')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'direction')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'version')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'vlan')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'priority')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'truncated')
        m1.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'unknown2')

        m2=Mask(exp_pkt2)
        m2.set_do_not_care_scapy(ptf.packet.IP,'tos')
        m2.set_do_not_care_scapy(ptf.packet.IP,'frag')
        m2.set_do_not_care_scapy(ptf.packet.IP,'flags')
        m2.set_do_not_care_scapy(ptf.packet.IP,'chksum')
        m2.set_do_not_care_scapy(ptf.packet.IP,'id')
        m2.set_do_not_care_scapy(ptf.packet.GRE,'proto')
        m2.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'platf_id')
        m2.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info1')
        m2.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info2')
            
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'span_id')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'timestamp')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'sgt_other')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'direction')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'version')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'vlan')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'priority')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'truncated')
        m2.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'unknown2')
        
        m1_set=Mask(exp_pkt1_set)
        m1_set.set_do_not_care_scapy(ptf.packet.IP,'tos')
        m1_set.set_do_not_care_scapy(ptf.packet.IP,'frag')
        m1_set.set_do_not_care_scapy(ptf.packet.IP,'flags')
        m1_set.set_do_not_care_scapy(ptf.packet.IP,'chksum')
        m1_set.set_do_not_care_scapy(ptf.packet.IP,'id')
        m1_set.set_do_not_care_scapy(ptf.packet.GRE,'proto')
        m1_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'platf_id')
        m1_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info1')
        m1_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info2')
 
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'span_id')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'timestamp')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'sgt_other')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'direction')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'version')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'vlan')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'priority')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'truncated')
        m1_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'unknown2')

        m2_set=Mask(exp_pkt2_set)
        m2_set.set_do_not_care_scapy(ptf.packet.IP,'tos')
        m2_set.set_do_not_care_scapy(ptf.packet.IP,'frag')
        m2_set.set_do_not_care_scapy(ptf.packet.IP,'flags')
        m2_set.set_do_not_care_scapy(ptf.packet.IP,'chksum')
        m2_set.set_do_not_care_scapy(ptf.packet.IP,'id')
        m2_set.set_do_not_care_scapy(ptf.packet.GRE,'proto')
        m2_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'platf_id')
        m2_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info1')
        m2_set.set_do_not_care_scapy(ptf.packet.PlatformSpecific, 'info2')

        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'span_id')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'timestamp')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'sgt_other')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'direction')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'version')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'vlan')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'priority')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'truncated')
        m2_set.set_do_not_care_scapy(ptf.packet.ERSPAN_III, 'unknown2')

        n=Mask(pkt2)
        n.set_do_not_care_scapy(ptf.packet.IP,'len')
        n.set_do_not_care_scapy(ptf.packet.IP,'chksum')

        warmboot(self.client)
        try:
            # in tuple: 0 is device number, 2 is port number
            # this tuple uniquely identifies a port
            # for ingress mirroring
            print "Checking INGRESS ERSPAN Mirroring"
            print "Sending packet port 2 -> port 3 (00:22:22:22:22:22 -> 00:00:00:00:00:33)"
            send_packet(self, 2, pkt)
            verify_each_packet_on_each_port(self, [m1,pkt], ports=[1,3])#FIXME need to properly implement

            time.sleep(1)
            
            # for egress mirroring
            print "Checking EGRESS ERSPAN Mirroring"
            print "Sending packet port 3 -> port 2 (00:33:33:33:33:33 -> 00:00:00:00:00:22)"
            send_packet(self, 3, pkt2)
            verify_each_packet_on_each_port(self, [pkt2,m2], ports=[2,1])#FIXME need to properly implement
            
            #Get Set Get 1
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = %d" %monitor_port
            attrs = self.client.sai_thrift_get_mirror_attribute(erspanid)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port != a.value.oid:
                        raise NotImplementedError()
            print "Set mirror session: monitor_port = 0x%x" %port0
            attr_value = sai_thrift_attribute_value_t(oid=port0)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            # Get 1
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = %d" %port0
            attrs = self.client.sai_thrift_get_mirror_attribute(erspanid)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %port0
                    print "get monitor_port = %d" %a.value.oid
                    if port0 != a.value.oid:
                        raise NotImplementedError()        
            
            print "Checking INGRESS ERSPAN Mirroring set after"
            print "Sending packet port 2 -> port 3 (00:22:22:22:22:22 -> 00:00:00:00:00:33)"
            send_packet(self, 2, pkt)
            verify_each_packet_on_each_port(self, [m1,pkt], ports=[0,3])#FIXME need to properly implement
            
            time.sleep(1)
            
            # for egress mirroring
            print "Checking EGRESS ERSPAN Mirroring set after"
            print "Sending packet port 3 -> port 2 (00:33:33:33:33:33 -> 00:00:00:00:00:22)"
            send_packet(self, 3, pkt2)
            verify_each_packet_on_each_port(self, [pkt2,m2], ports=[2,0])#FIXME need to properly implement
            
            ##Get Set Get 2
            #source mac
            print "Set mirror session: src_mac_set = %s" %src_mac_set
            attr_value = sai_thrift_attribute_value_t(mac=src_mac_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #dst mac
            print "Set mirror session: dst_mac_set = %s" %dst_mac_set
            attr_value = sai_thrift_attribute_value_t(mac=dst_mac_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            #source ip
            print "Set mirror session: src_ip_set = %s" %src_ip_set
            addr = sai_thrift_ip_t(ip4=src_ip_set)
            src_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            attribute5_value = sai_thrift_attribute_value_t(ipaddr=src_ip_addr)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS,
                                            value=attribute5_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #dst ip
            print "Set mirror session: dst_ip_set = %s" %dst_ip_set
            addr = sai_thrift_ip_t(ip4=dst_ip_set)
            dst_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
            attribute6_value = sai_thrift_attribute_value_t(ipaddr=dst_ip_addr)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS,
                                            value=attribute6_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #tos
            print "Set mirror session: tos_set = %s" %tos_set
            attr_value = sai_thrift_attribute_value_t(u8=tos_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TOS, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #ttl
            print "Set mirror session: ttl_set = %s" %ttl_set
            attr_value = sai_thrift_attribute_value_t(u8=ttl_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TTL, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            #gre type
            print "Set mirror session: gre_type_set = %s" %gre_type_set
            attr_value = sai_thrift_attribute_value_t(u16=gre_type_set)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(erspanid, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            
            ## Get 2
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE, monitor_port = ptf_intf 0 "
            attrs = self.client.sai_thrift_get_mirror_attribute(erspanid)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "set mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "set monitor_port = %d" %port0
                    print "get monitor_port = %d" %a.value.oid
                    if port0 != a.value.oid:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS: 
                    print "set src_mac_set = %s" %src_mac_set
                    print "get src_mac_set = %s" %a.value.mac
                    if src_mac_set != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS: 
                    print "set dst_mac_set = %s" %dst_mac_set
                    print "get dst_mac_set = %s" %a.value.mac
                    if dst_mac_set != a.value.mac:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS: 
                    print "set src_ip_set = %s" %src_ip_set
                    print "get src_ip_set = %s" %a.value.ipaddr.addr.ip4
                    if src_ip_set != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS: 
                    print "set dst_ip_set = %s" %dst_ip_set
                    print "get dst_ip_set = %s" %a.value.ipaddr.addr.ip4
                    if dst_ip_set != a.value.ipaddr.addr.ip4:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TOS: 
                    print "set tos_set = %d" %tos_set
                    print "get tos_set = %d" %a.value.u8
                    if tos_set != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_TTL: 
                    print "set ttl_set = %d" %ttl_set
                    print "get ttl_set = %d" %a.value.u8
                    if ttl_set != a.value.u8:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE: 
                    print "set gre_type_set = %d" %gre_type_set
                    print "get gre_type_set = %d" %a.value.u16
                    if gre_type_set != a.value.u16:
                        raise NotImplementedError()
             
            # for ingress mirroring             
            print "Checking INGRESS ERSPAN Mirroring set after"
            print "Sending packet port 2 -> port 3 (00:22:22:22:22:22 -> 00:00:00:00:00:33)"
            send_packet(self, 2, pkt)
            verify_each_packet_on_each_port(self, [m1_set,pkt], ports=[0,3])#FIXME need to properly implement
            
            time.sleep(1)
            
            # for egress mirroring
            print "Checking EGRESS ERSPAN Mirroring set after"
            print "Sending packet port 3 -> port 2 (00:33:33:33:33:33 -> 00:00:00:00:00:22)"
            send_packet(self, 3, pkt2)
            verify_each_packet_on_each_port(self, [pkt2,m2_set], ports=[2,0])#FIXME need to properly implement
            
        finally:
           print "Sucess,now clear up config"
           sai_thrift_delete_fdb(self.client, vlan_remote_oid, mac2, port2)
           sai_thrift_delete_fdb(self.client, vlan_remote_oid, mac3, port3)
           
           # Remove ports from mirror destination
           attrb_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=0,object_id_list=[]))
           attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attrb_value)
           self.client.sai_thrift_set_port_attribute(port2, attr)
           attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_EGRESS_MIRROR_SESSION, value=attrb_value)
           self.client.sai_thrift_set_port_attribute(port2, attr)
           
           # Now you can remove destination
           self.client.sai_thrift_remove_mirror_session(erspanid)
           
           # Remove ports from VLAN 3
           self.client.sai_thrift_remove_vlan_member(vlan_member1)
           self.client.sai_thrift_remove_vlan_member(vlan_member2)
           self.client.sai_thrift_remove_vlan_member(vlan_member3)
           self.client.sai_thrift_remove_vlan(vlan_remote_oid)
           
           # Add ports back to default VLAN
           vlan_member1a = sai_thrift_create_vlan_member(self.client, 1, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
           vlan_member2a = sai_thrift_create_vlan_member(self.client, 1, port2, SAI_VLAN_TAGGING_MODE_UNTAGGED)
           vlan_member3a = sai_thrift_create_vlan_member(self.client, 1, port3, SAI_VLAN_TAGGING_MODE_UNTAGGED)
           
           attr_value = sai_thrift_attribute_value_t(u16=1)
           attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
           self.client.sai_thrift_set_port_attribute(port1, attr)
           self.client.sai_thrift_set_port_attribute(port2, attr)
           self.client.sai_thrift_set_port_attribute(port3, attr)
           
@group('mirror')
class FlowMirrorTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 2 -> ptf_intf 1 (192.168.0.1 ---> 10.10.10.1 [id = 105])"

        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        
        mac_src = '00:11:11:11:11:11'
        mac_dst = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        # the relationship between vlan id and vlan_oid
        vlan_id = 20
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)

        sai_thrift_create_fdb(self.client, vlan_oid, mac_dst, port2, mac_action)
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = 0x%lx" %ingress_localmirror_id
        
        # send the test packet(s)
        pkt = simple_qinq_tcp_packet(pktlen=100,
            eth_dst=mac_dst,
            eth_src=mac_src,
            dl_vlan_outer=20,
            dl_vlan_pcp_outer=4,
            dl_vlan_cfi_outer=1,
            vlan_vid=10,
            vlan_pcp=2,
            dl_vlan_cfi=1,
            ip_dst='10.10.10.1',
            ip_src='192.168.0.1',
            ip_tos=5,
            ip_ecn=1,
            ip_dscp=1,
            ip_ttl=64,
            tcp_sport=1234,
            tcp_dport=80)
            
        print "Sending packet ptf_intf 2 -[acl]-> ptf_intf 1 (192.168.0.1 -[acl]-> 10.10.10.1 [id = 105])"
        # setup ACL to block based on Source IP
        table_stage = SAI_ACL_STAGE_INGRESS
        table_bind_point_list = [SAI_ACL_BIND_POINT_TYPE_VLAN]
        entry_priority = SAI_SWITCH_ATTR_ACL_ENTRY_MINIMUM_PRIORITY
        action = SAI_PACKET_ACTION_FORWARD
        in_ports = [port1, port2]
        mac_src_mask = "ff:ff:ff:ff:ff:ff"
        mac_dst_mask = "ff:ff:ff:ff:ff:ff"
        svlan_id=None
        svlan_pri=4
        svlan_cfi=1
        cvlan_id=10
        cvlan_pri=2
        cvlan_cfi=None
        ip_src = "192.168.0.1"
        ip_src_mask = "255.255.255.255"
        ip_dst = '10.10.10.1'
        ip_dst_mask = "255.255.255.255"
        is_ipv6 = False
        ip_tos=5
        ip_ecn=1
        ip_dscp=1
        ip_ttl=None
        ip_proto = None
        in_port = None
        out_port = None
        out_ports = None
        src_l4_port = 1234
        dst_l4_port = 80
        ingress_mirror_id_list=[ingress_localmirror_id]
        egress_mirror_id = None
        admin_state = True
        #add vlan edit action
        new_svlan = None
        new_scos = None
        new_cvlan = None
        new_ccos = None
        #deny learning
        deny_learn = None
        addr_family = None

        acl_table_id = sai_thrift_create_acl_table(self.client,
            table_stage,
            table_bind_point_list,
            addr_family,
            mac_src,
            mac_dst,
            ip_src,
            ip_dst,
            ip_proto,
            in_ports,
            out_ports,
            in_port,
            out_port,
            src_l4_port,
            dst_l4_port)
        acl_entry_id = sai_thrift_create_acl_entry(self.client,
            acl_table_id,
            entry_priority,
            admin_state,
            action, addr_family,
            mac_src, mac_src_mask,
            mac_dst, mac_dst_mask,
            svlan_id, svlan_pri,
            svlan_cfi, cvlan_id,
            cvlan_pri, cvlan_cfi,
            ip_src, ip_src_mask,
            ip_dst, ip_dst_mask,
            is_ipv6,
            ip_tos, ip_ecn,
            ip_dscp, ip_ttl,
            ip_proto,
            in_ports, out_ports,
            in_port, out_port,
            src_l4_port, dst_l4_port,
            ingress_mirror_id_list,
            egress_mirror_id,
            new_svlan, new_scos,
            new_cvlan, new_ccos,
            deny_learn)

        # bind this ACL table to port2s object id
        attr_value = sai_thrift_attribute_value_t(oid=acl_table_id)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_INGRESS_ACL, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        self.client.sai_thrift_clear_cpu_packet_info()
        warmboot(self.client)

        try:
            assert acl_table_id > 0, 'acl_entry_id is <= 0'
            assert acl_entry_id > 0, 'acl_entry_id is <= 0'
            print '#### ACL \'DROP, src 192.168.0.1/255.255.255.0, in_ports[ptf_intf_1,2]\' Applied ####'
            print '#### Sending      ', router_mac, '| 00:22:22:22:22:22 | 10.10.10.1 | 192.168.0.1 | @ ptf_intf 2'
            
            send_packet(self, 0, str(pkt))
            time.sleep(1)
            #verify_packets(self, pkt, [1])
            verify_each_packet_on_each_port(self, [pkt, pkt], [1, 2])
            
        finally:
            print "sucess, just for cleanup config"
            # unbind this ACL table from vlan object id
            attr_value = sai_thrift_attribute_value_t(oid=SAI_NULL_OBJECT_ID)
            attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_INGRESS_ACL, value=attr_value)
            self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
            
            # cleanup ACL
            self.client.sai_thrift_remove_acl_entry(acl_entry_id)
            self.client.sai_thrift_remove_acl_table(acl_table_id)
            # remove ingress_localmirror_id
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)
            # cleanup FDB
            sai_thrift_delete_fdb(self.client, vlan_oid, mac_dst, port2)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)

@group('mirror')           
class IngressLocalMirror1to2Test(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 1 -> ptf_intf 2, ptf_intf 3 (local mirror)"
        print "Sending packet ptf_intf 2 -> ptf_intf 1, ptf_intf 3 (local mirror)"

        switch_init(self.client)
        vlan_id = 10
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        port4 = port_list[4]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac1, port1, mac_action)
        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)

        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port1 = port3
        monitor_port2 = port4
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id1 = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port1,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id1 = 0x%lx" %ingress_localmirror_id1
        
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 4 "
        ingress_localmirror_id2 = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port2,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id2 = 0x%lx" %ingress_localmirror_id2

        attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=2,object_id_list=[ingress_localmirror_id1, ingress_localmirror_id2]))
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        self.client.sai_thrift_set_port_attribute(port2, attr)

        warmboot(self.client)
        try:
            assert ingress_localmirror_id1 > 0, 'ingress_localmirror_id1 is <= 0'
            assert ingress_localmirror_id2 > 0, 'ingress_localmirror_id2 is <= 0'
            
            #Get
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port1
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port1
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port1 != a.value.oid:
                        raise NotImplementedError()
                        
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port2
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id2)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port2
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port2 != a.value.oid:
                        raise NotImplementedError()

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

            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            time.sleep(1)
            verify_each_packet_on_each_port(self, [exp_pkt1, pkt1, pkt1], [2, 3, 4])

            pkt2 = simple_tcp_packet(eth_dst=mac1,
                eth_src=mac2,
                ip_dst='10.0.0.1',
                ip_src='192.168.0.1',
                vlan_vid=10,
                dl_vlan_enable=True,
                ip_id=102,
                ip_ttl=64,
                pktlen=104)
            exp_pkt2 = simple_tcp_packet(eth_dst=mac1,
                eth_src=mac2,
                ip_dst='10.0.0.1',
                ip_src='192.168.0.1',
                ip_id=102,
                ip_ttl=64,
                pktlen=100)

            print '#### Sending 00:11:11:11:11:11 | 00:22:22:22:22:22 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 2 ####'
            send_packet(self, 2, str(pkt2))
            verify_each_packet_on_each_port(self, [exp_pkt2, pkt2, pkt2], [1, 3, 4])

        finally:
            attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=0,object_id_list=[]))
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            self.client.sai_thrift_set_port_attribute(port2, attr)
            
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id1)
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id2)
            
            sai_thrift_delete_fdb(self.client, vlan_oid, mac1, port1)
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)
            
@group('mirror')
class IngressLocalMirror1to2SetTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 1 -> ptf_intf 2, ptf_intf 3 (local mirror)"
        print "Sending packet ptf_intf 2 -> ptf_intf 1, ptf_intf 3 (local mirror)"

        switch_init(self.client)
        vlan_id = 10
        port0 = port_list[0]
        port1 = port_list[1]
        port2 = port_list[2]
        port3 = port_list[3]
        port4 = port_list[4]
        port5 = port_list[5]
        mac1 = '00:11:11:11:11:11'
        mac2 = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)
        vlan_member1 = sai_thrift_create_vlan_member(self.client, vlan_oid, port1, SAI_VLAN_TAGGING_MODE_UNTAGGED)
        vlan_member2 = sai_thrift_create_vlan_member(self.client, vlan_oid, port2, SAI_VLAN_TAGGING_MODE_TAGGED)

        attr_value = sai_thrift_attribute_value_t(u16=vlan_id)
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)

        sai_thrift_create_fdb(self.client, vlan_oid, mac2, port2, mac_action)

        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port1 = port3
        monitor_port2 = port4
        monitor_port3 = port5
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id1 = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port1,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id1 = 0x%lx" %ingress_localmirror_id1
        
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 4 "
        ingress_localmirror_id2 = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port2,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id2 = 0x%lx" %ingress_localmirror_id2
        
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 4 "
        ingress_localmirror_id3 = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port3,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id3 = 0x%lx" %ingress_localmirror_id3

        attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=3,object_id_list=[ingress_localmirror_id1,ingress_localmirror_id2,ingress_localmirror_id3]))
        attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
        self.client.sai_thrift_set_port_attribute(port1, attr)
        
        warmboot(self.client)
        
        try:
            assert ingress_localmirror_id1 > 0, 'ingress_localmirror_id1 is <= 0'
            assert ingress_localmirror_id2 > 0, 'ingress_localmirror_id2 is <= 0'
            
            #Get
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port1
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id1)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port1
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port1 != a.value.oid:
                        raise NotImplementedError()
                        
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port2
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id2)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port2
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port2 != a.value.oid:
                        raise NotImplementedError()
                        
            print "Get mirror session attribute: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = 0x%lx" %monitor_port3
            attrs = self.client.sai_thrift_get_mirror_attribute(ingress_localmirror_id3)
            print "status = %d" %attrs.status
            assert (attrs.status == SAI_STATUS_SUCCESS)
            for a in attrs.attr_list:
                if a.id == SAI_MIRROR_SESSION_ATTR_TYPE:
                    print "create mirror_type = %d" %mirror_type
                    print "get mirror_type = %d" %a.value.s32
                    if mirror_type != a.value.s32:
                        raise NotImplementedError()
                if a.id == SAI_MIRROR_SESSION_ATTR_MONITOR_PORT: 
                    print "create monitor_port = 0x%x" %monitor_port3
                    print "get monitor_port = 0x%x" %a.value.oid
                    if monitor_port3 != a.value.oid:
                        raise NotImplementedError()

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

            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            time.sleep(1)
            verify_each_packet_on_each_port(self, [exp_pkt1, pkt1, pkt1, pkt1], [2, 3, 4, 5])
            
            attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=1,object_id_list=[ingress_localmirror_id1]))
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            print '#### Sending 00:22:22:22:22:22 | 00:11:11:11:11:11 | 10.0.0.1 | 192.168.0.1 | @ ptf_intf 1 ####'
            send_packet(self, 1, str(pkt1))
            time.sleep(1)
            verify_each_packet_on_each_port(self, [exp_pkt1, pkt1], [2, 3])

        finally:
            attr_value = sai_thrift_attribute_value_t(objlist=sai_thrift_object_list_t(count=0,object_id_list=[]))
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_INGRESS_MIRROR_SESSION, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id1)
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id2)
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id3)
            
            sai_thrift_delete_fdb(self.client, vlan_oid, mac2, port2)
            
            attr_value = sai_thrift_attribute_value_t(u16=1)
            attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_PORT_VLAN_ID, value=attr_value)
            self.client.sai_thrift_set_port_attribute(port1, attr)
            
            self.client.sai_thrift_remove_vlan_member(vlan_member1)
            self.client.sai_thrift_remove_vlan_member(vlan_member2)
            self.client.sai_thrift_remove_vlan(vlan_oid)

            
@group('mirror')
class FlowMirrorSampleRateTest(sai_base_test.ThriftInterfaceDataPlane):
    def runTest(self):
        print
        print '----------------------------------------------------------------------------------------------'
        print "Sending packet ptf_intf 2 -> ptf_intf 1 (192.168.0.1 ---> 10.10.10.1 [id = 105])"

        switch_init(self.client)
        port1 = port_list[0]
        port2 = port_list[1]
        port3 = port_list[2]
        
        mac_src = '00:11:11:11:11:11'
        mac_dst = '00:22:22:22:22:22'
        mac_action = SAI_PACKET_ACTION_FORWARD

        # the relationship between vlan id and vlan_oid
        vlan_id = 20
        vlan_oid = sai_thrift_create_vlan(self.client, vlan_id)

        sai_thrift_create_fdb(self.client, vlan_oid, mac_dst, port2, mac_action)
        
        # setup local mirror session
        mirror_type = SAI_MIRROR_SESSION_TYPE_LOCAL
        monitor_port = port3
        print "Create mirror session: mirror_type = SAI_MIRROR_TYPE_LOCAL, monitor_port = ptf_intf 3 "
        ingress_localmirror_id = sai_thrift_create_mirror_session(self.client,
            mirror_type,
            monitor_port,
            None, None, None,
            None, None, None,
            None, None, None,
            None, None, None,
            None)
        print "ingress_localmirror_id = 0x%lx" %ingress_localmirror_id
        
        # send the test packet(s)
        pkt = simple_qinq_tcp_packet(pktlen=100,
            eth_dst=mac_dst,
            eth_src=mac_src,
            dl_vlan_outer=20,
            dl_vlan_pcp_outer=4,
            dl_vlan_cfi_outer=1,
            vlan_vid=10,
            vlan_pcp=2,
            dl_vlan_cfi=1,
            ip_dst='10.10.10.1',
            ip_src='192.168.0.1',
            ip_tos=5,
            ip_ecn=1,
            ip_dscp=1,
            ip_ttl=64,
            tcp_sport=1234,
            tcp_dport=80)
            
        print "Sending packet ptf_intf 2 -[acl]-> ptf_intf 1 (192.168.0.1 -[acl]-> 10.10.10.1 [id = 105])"
        # setup ACL to block based on Source IP
        table_stage = SAI_ACL_STAGE_INGRESS
        table_bind_point_list = [SAI_ACL_BIND_POINT_TYPE_VLAN]
        entry_priority = SAI_SWITCH_ATTR_ACL_ENTRY_MINIMUM_PRIORITY
        action = SAI_PACKET_ACTION_FORWARD
        in_ports = [port1, port2]
        mac_src_mask = "ff:ff:ff:ff:ff:ff"
        mac_dst_mask = "ff:ff:ff:ff:ff:ff"
        svlan_id=None
        svlan_pri=4
        svlan_cfi=1
        cvlan_id=10
        cvlan_pri=2
        cvlan_cfi=None
        ip_src = "192.168.0.1"
        ip_src_mask = "255.255.255.255"
        ip_dst = '10.10.10.1'
        ip_dst_mask = "255.255.255.255"
        is_ipv6 = False
        ip_tos=5
        ip_ecn=1
        ip_dscp=1
        ip_ttl=None
        ip_proto = None
        in_port = None
        out_port = None
        out_ports = None
        src_l4_port = 1234
        dst_l4_port = 80
        ingress_mirror_id_list=[ingress_localmirror_id]
        egress_mirror_id = None
        admin_state = True
        #add vlan edit action
        new_svlan = None
        new_scos = None
        new_cvlan = None
        new_ccos = None
        #deny learning
        deny_learn = None
        addr_family = None

        acl_table_id = sai_thrift_create_acl_table(self.client,
            table_stage,
            table_bind_point_list,
            addr_family,
            mac_src,
            mac_dst,
            ip_src,
            ip_dst,
            ip_proto,
            in_ports,
            out_ports,
            in_port,
            out_port,
            src_l4_port,
            dst_l4_port)
        acl_entry_id = sai_thrift_create_acl_entry(self.client,
            acl_table_id,
            entry_priority,
            admin_state,
            action, addr_family,
            mac_src, mac_src_mask,
            mac_dst, mac_dst_mask,
            svlan_id, svlan_pri,
            svlan_cfi, cvlan_id,
            cvlan_pri, cvlan_cfi,
            ip_src, ip_src_mask,
            ip_dst, ip_dst_mask,
            is_ipv6,
            ip_tos, ip_ecn,
            ip_dscp, ip_ttl,
            ip_proto,
            in_ports, out_ports,
            in_port, out_port,
            src_l4_port, dst_l4_port,
            ingress_mirror_id_list,
            egress_mirror_id,
            new_svlan, new_scos,
            new_cvlan, new_ccos,
            deny_learn)

        # bind this ACL table to port2s object id
        attr_value = sai_thrift_attribute_value_t(oid=acl_table_id)
        attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_INGRESS_ACL, value=attr_value)
        self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
        self.client.sai_thrift_clear_cpu_packet_info()
        warmboot(self.client)

        try:
            count = [0, 0]
            assert acl_table_id > 0, 'acl_entry_id is <= 0'
            assert acl_entry_id > 0, 'acl_entry_id is <= 0'
            print '#### ACL \'DROP, src 192.168.0.1/255.255.255.0, in_ports[ptf_intf_1,2]\' Applied ####'
            print '#### Sending      ', router_mac, '| 00:22:22:22:22:22 | 10.10.10.1 | 192.168.0.1 | @ ptf_intf 2'
            
            #send_packet(self, 0, str(pkt))
            #time.sleep(1)
            #verify_packets(self, pkt, [1])

            print "Set mirror session: sample_rate = 1/8"
            sample_rate = 1
            attr_value = sai_thrift_attribute_value_t(u32=sample_rate)
            attr = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SAMPLE_RATE, value=attr_value)
            status=self.client.sai_thrift_set_mirror_attribute(ingress_localmirror_id, attr)
            print "status = %d" %status
            assert (status == SAI_STATUS_SUCCESS)
            
            #send_packet(self, 0, str(pkt), 1) 
            send_packet(self, 0, str(pkt))
            time.sleep(1)
            rev_pkt_cnt = count_matched_packets(self, pkt, 2)
            print"*********************** rev_pkt_cnt:%d" %rev_pkt_cnt
            print"count:####################################"
            print"mirror rate 1/8(160 pkt):####################################"
            
        finally:
            print "sucess, just for cleanup config"
            # unbind this ACL table from vlan object id
            attr_value = sai_thrift_attribute_value_t(oid=SAI_NULL_OBJECT_ID)
            attr = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_INGRESS_ACL, value=attr_value)
            self.client.sai_thrift_set_vlan_attribute(vlan_oid, attr)
            
            # cleanup ACL
            self.client.sai_thrift_remove_acl_entry(acl_entry_id)
            self.client.sai_thrift_remove_acl_table(acl_table_id)
            # remove ingress_localmirror_id
            self.client.sai_thrift_remove_mirror_session(ingress_localmirror_id)
            # cleanup FDB
            sai_thrift_delete_fdb(self.client, vlan_oid, mac_dst, port2)
            
            self.client.sai_thrift_remove_vlan(vlan_oid)
