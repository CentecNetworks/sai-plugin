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
Thrift SAI interface basic tests
"""

import switch_sai_thrift
from sai_base_test import *
import time
import sys
import logging

import unittest
import random

import sai_base_test

from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *

import os

from switch_sai_thrift.ttypes import  *

from switch_sai_thrift.sai_headers import  *


this_dir = os.path.dirname(os.path.abspath(__file__))

class VlanObj:
    def __init__(self):
        self.oid = 0
        self.vid = 0

class SwitchObj:
    def __init__(self):
        self.default_1q_bridge = SAI_NULL_OBJECT_ID
        self.default_vlan = VlanObj()

"""
0xFFFF cannot pass the validation,
the reason is that sai u16 is mapped to thrift i16 which is checked to be in [-32768, 32767] range
but "-1" is serialized to 0xFFFF.
"""
U16MASKFULL = -1
U8MASKFULL = -1

switch_inited=0
warmbooten=0
port_list = {}
sai_port_list = []
table_attr_list = []
default_time_out = 5
router_mac='00:77:66:55:44:00'
rewrite_mac1='00:77:66:55:44:01'
rewrite_mac2='00:77:66:55:44:02'
profile_file = "/root/ctc_sai/test/saithrift/profile.ini"
switch = SwitchObj()

is_bmv2 = ('BMV2_TEST' in os.environ) and (int(os.environ['BMV2_TEST']) == 1)

def alter(client,file,old_str,new_str):
    file_data = ""
    with open(file, "r") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str,new_str)
            file_data += line
    with open(file,"w") as f:
        f.write(file_data)

def warmboot(client):
        print ""
        global warmbooten
        if warmbooten == 0:
            return;
        attr_value = sai_thrift_attribute_value_t(booldata=1)
        attr = sai_thrift_attribute_t(id=SAI_SWITCH_ATTR_RESTART_WARM, value=attr_value)
        client.sai_thrift_set_switch_attribute(attr)
        client.sai_thrift_remove_switch()
        alter(client,profile_file,"SAI_BOOT_TYPE=0","SAI_BOOT_TYPE=1")
        client.sai_thrift_create_switch()
        alter(client,profile_file,"SAI_BOOT_TYPE=1","SAI_BOOT_TYPE=0")

def switch_init(client):
    global switch_inited

    if switch_inited:
        return

    switch.default_1q_bridge = client.sai_thrift_get_default_1q_bridge_id()
    assert (switch.default_1q_bridge != SAI_NULL_OBJECT_ID)

    ret = client.sai_thrift_get_default_vlan_id()
    assert (ret.status == SAI_STATUS_SUCCESS), "Failed to get default vlan"
    switch.default_vlan.oid = ret.data.oid

    ret = client.sai_thrift_get_vlan_id(switch.default_vlan.oid)
    assert (ret.status == SAI_STATUS_SUCCESS), "Failed obtain default vlan id"
    switch.default_vlan.vid = ret.data.u16

    for interface,front in interface_to_front_mapping.iteritems():
    	sai_port_id = client.sai_thrift_get_port_id_by_front_port(front);
        #print sai_port_id
        #print front
        #print interface
    	port_list[int(interface)]=sai_port_id

    ids_list = [SAI_SWITCH_ATTR_PORT_NUMBER, SAI_SWITCH_ATTR_PORT_LIST]
    switch_attr_list = client.sai_thrift_get_switch_attribute(ids_list)
    attr_list = switch_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_SWITCH_ATTR_PORT_NUMBER:
            #print "max ports: " + attribute.value.u32
            print "max ports: %d" % attribute.value.u32
        elif attribute.id == SAI_SWITCH_ATTR_PORT_LIST:
            for port_id in attribute.value.objlist.object_id_list:
                if port_id in port_list.values():
                    attr_value = sai_thrift_attribute_value_t(booldata=1)
                    attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_ADMIN_STATE, value=attr_value)
                    client.sai_thrift_set_port_attribute(port_id, attr)
                    sai_port_list.append(port_id)
        else:
            print "unknown switch attribute"
    attr_value = sai_thrift_attribute_value_t(mac=router_mac)
    attr = sai_thrift_attribute_t(id=SAI_SWITCH_ATTR_SRC_MAC_ADDRESS, value=attr_value)
    client.sai_thrift_set_switch_attribute(attr)
    all_ports_are_up = True
    for num_of_tries in range(200):
        time.sleep(1)
        # wait till the port are up
        for port in sai_port_list:
            port_attr_list = client.sai_thrift_get_port_attribute(port)
            attr_list = port_attr_list.attr_list
            for attribute in attr_list:
                if attribute.id == SAI_PORT_ATTR_OPER_STATUS:
                    if attribute.value.s32 != SAI_PORT_OPER_STATUS_UP:
                        all_ports_are_up = False
                        print "port 0x%x is down" % port
        if all_ports_are_up:
            break
        else:
            all_ports_are_up = True
    if not all_ports_are_up:
        raise RuntimeError('Not all of the  ports are up')

    switch_inited = 1

def sai_thrift_get_bridge_port_by_port(client, port_id):
    ret = client.sai_thrift_get_bridge_port_list(switch.default_1q_bridge)
    assert (ret.status == SAI_STATUS_SUCCESS)
    print"port_id######:%lx" %port_id
    for bp in ret.data.objlist.object_id_list:
        attrs = client.sai_thrift_get_bridge_port_attribute(bp)
        bport = SAI_NULL_OBJECT_ID
        is_port = False
        for a in attrs.attr_list:
            if a.id == SAI_BRIDGE_PORT_ATTR_PORT_ID:
                bport = a.value.oid
            if a.id == SAI_BRIDGE_PORT_ATTR_TYPE:
                is_port = a.value.s32 == SAI_BRIDGE_PORT_TYPE_PORT

        if is_port and bport == port_id:
            return bp

    return SAI_NULL_OBJECT_ID

def sai_thrift_get_port_by_bridge_port(client, bp):
    attrs = client.sai_thrift_get_bridge_port_attribute(bp)
    port = SAI_NULL_OBJECT_ID

    for a in attrs.attr_list:
        if a.id == SAI_BRIDGE_PORT_ATTR_PORT_ID:
            return a.value.oid

    return SAI_NULL_OBJECT_ID

def sai_thrift_create_bridge_sub_port(client, port_id, bridge_id, vlan_id, admin_state = True):
    bport_oid = sai_thrift_get_bridge_port_by_port(client, port_id)
    assert (bport_oid != SAI_NULL_OBJECT_ID)

    status = client.sai_thrift_remove_bridge_port(bport_oid)
    assert (status == SAI_STATUS_SUCCESS)

    return sai_thrift_create_bridge_port(client, port_id, SAI_BRIDGE_PORT_TYPE_SUB_PORT, bridge_id, vlan_id, None, admin_state)

def sai_thrift_remove_bridge_sub_port(client, sub_port_id, port_id):
    bport_attr_admin_state_value = sai_thrift_attribute_value_t(booldata=False)
    bport_attr_admin_state = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_ADMIN_STATE,
                                                    value=bport_attr_admin_state_value)
    client.sai_thrift_set_bridge_port_attribute(sub_port_id, bport_attr_admin_state)

    sai_thrift_flush_fdb_by_bridge_port(client, sub_port_id)

    client.sai_thrift_remove_bridge_port(sub_port_id)
    sai_thrift_create_bridge_port(client, port_id)

def sai_thrift_create_bridge_rif_port(client, bridge_id, rif_id):
    return sai_thrift_create_bridge_port(client, None, SAI_BRIDGE_PORT_TYPE_1D_ROUTER, bridge_id, None, rif_id, True)

def sai_thrift_create_bridge_port(client, port_id = None, type = SAI_BRIDGE_PORT_TYPE_PORT, bridge_id = None, vlan_id = None, rif_id = None, admin_state = True):
    bport_attr_list = []

    bport_attr_type_value = sai_thrift_attribute_value_t(s32=type)
    bport_attr_type = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_TYPE,
                                             value=bport_attr_type_value)

    bport_attr_list.append(bport_attr_type)

    if port_id is not None:
         bport_attr_port_id_value = sai_thrift_attribute_value_t(oid=port_id)
         bport_attr_port_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_PORT_ID,
                                                value=bport_attr_port_id_value)
         bport_attr_list.append(bport_attr_port_id)
   
    bport_attr_admin_state_value = sai_thrift_attribute_value_t(booldata=admin_state)
    bport_attr_admin_state = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_ADMIN_STATE,
                                                    value=bport_attr_admin_state_value)
    bport_attr_list.append(bport_attr_admin_state)

    if bridge_id is not None:
        bport_attr_bridge_id_value = sai_thrift_attribute_value_t(oid=bridge_id)
    else:
        bport_attr_bridge_id_value = sai_thrift_attribute_value_t(oid=switch.default_1q_bridge)

    bport_attr_bridge_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_BRIDGE_ID,
                                                  value=bport_attr_bridge_id_value)
    bport_attr_list.append(bport_attr_bridge_id)

    if vlan_id is not None:
        bport_attr_vlan_id_value = sai_thrift_attribute_value_t(u16=vlan_id)
        bport_attr_vlan_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_VLAN_ID,
                                                    value=bport_attr_vlan_id_value)
        bport_attr_list.append(bport_attr_vlan_id)

    if rif_id is not None:
        bport_attr_rif_id_value = sai_thrift_attribute_value_t(oid=rif_id)
        bport_attr_rif_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_RIF_ID,
                                                value=bport_attr_rif_id_value)
        bport_attr_list.append(bport_attr_rif_id)    

    ret = client.sai_thrift_create_bridge_port(bport_attr_list)
    assert (ret.status == SAI_STATUS_SUCCESS)
    assert (ret.data.oid != SAI_NULL_OBJECT_ID)

    return ret.data.oid

def sai_thrift_create_bridge_tunnel_port(client, tunnel_id = None, bridge_id = None, admin_state = True):
    bport_attr_list = []

    bport_attr_type_value = sai_thrift_attribute_value_t(s32=SAI_BRIDGE_PORT_TYPE_TUNNEL)
    bport_attr_type = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_TYPE,
                                             value=bport_attr_type_value)

    bport_attr_list.append(bport_attr_type)

    if tunnel_id is not None:
         bport_attr_tunnel_id_value = sai_thrift_attribute_value_t(oid=tunnel_id)
         bport_attr_tunnel_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_TUNNEL_ID,
                                                value=bport_attr_tunnel_id_value)
         bport_attr_list.append(bport_attr_tunnel_id)
   
    bport_attr_admin_state_value = sai_thrift_attribute_value_t(booldata=admin_state)
    bport_attr_admin_state = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_ADMIN_STATE,
                                                    value=bport_attr_admin_state_value)
    bport_attr_list.append(bport_attr_admin_state)

    if bridge_id is not None:
        bport_attr_bridge_id_value = sai_thrift_attribute_value_t(oid=bridge_id)
    else:
        bport_attr_bridge_id_value = sai_thrift_attribute_value_t(oid=switch.default_1q_bridge)

    bport_attr_bridge_id = sai_thrift_attribute_t(id=SAI_BRIDGE_PORT_ATTR_BRIDGE_ID,
                                                  value=bport_attr_bridge_id_value)
    bport_attr_list.append(bport_attr_bridge_id)

    ret = client.sai_thrift_create_bridge_port(bport_attr_list)
    assert (ret.status == SAI_STATUS_SUCCESS)
    assert (ret.data.oid != SAI_NULL_OBJECT_ID)

    return ret.data.oid

def sai_thrift_create_bridge(client, type, max_learned_addresses = None, learn_disable = None, flood_disable = None):
    bridge_attrs = []

    bridge_attr_type_value = sai_thrift_attribute_value_t(s32=type)
    bridge_attr_type = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_TYPE,
                                              value=bridge_attr_type_value)
    bridge_attrs.append(bridge_attr_type)

    if max_learned_addresses is not None:
        bridge_attr_max_learned_addresses_value = sai_thrift_attribute_value_t(u32=max_learned_addresses)
        bridge_attr_max_learned_addresses = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_MAX_LEARNED_ADDRESSES,
                                                                   value=bridge_attr_max_learned_addresses_value)
        bridge_attrs.append(bridge_attr_max_learned_addresses)

    if learn_disable is not None:
        bridge_attr_learn_disable_value = sai_thrift_attribute_value_t(booldata=learn_disable)
        bridge_attr_learn_disable = sai_thrift_attribute_t(id=SAI_BRIDGE_ATTR_LEARN_DISABLE,
                                                           value=bridge_attr_learn_disable_value)
        bridge_attrs.append(bridge_attr_learn_disable)

    ret = client.sai_thrift_create_bridge(bridge_attrs)
    assert (ret.status == SAI_STATUS_SUCCESS)
    assert (ret.data.oid != SAI_NULL_OBJECT_ID)

    return ret.data.oid

def sai_thrift_get_cpu_port_id(client):
    cpu_port = client.sai_thrift_get_cpu_port_id()
    return cpu_port

def sai_thrift_get_default_vlan_id(client):
    vlan_id = client.sai_thrift_get_default_vlan_id()
    return vlan_id

def sai_thrift_get_default_router_id(client):
    default_router_id = client.sai_thrift_get_default_router_id()
    return default_router_id

def sai_thrift_create_fdb(client, bv_id, mac, port, mac_action):
    print "port:%x"  %port
    print "port:%lx"  %port
    bport = sai_thrift_get_bridge_port_by_port(client, port)
    assert (bport != SAI_NULL_OBJECT_ID)
    return sai_thrift_create_fdb_bport(client, bv_id, mac, bport, mac_action)

def sai_thrift_create_fdb_bport(client, bv_id, mac, bport_oid, mac_action):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    #value 0 represents static entry, id=0, represents entry type
    fdb_attribute1_value = sai_thrift_attribute_value_t(s32=SAI_FDB_ENTRY_TYPE_STATIC)
    fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_TYPE,
                                            value=fdb_attribute1_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute2_value = sai_thrift_attribute_value_t(oid=bport_oid)
    fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute2_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute3_value = sai_thrift_attribute_value_t(s32=mac_action)
    fdb_attribute3 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_PACKET_ACTION,
                                            value=fdb_attribute3_value)
    fdb_attr_list = [fdb_attribute1, fdb_attribute2, fdb_attribute3]
    client.sai_thrift_create_fdb_entry(thrift_fdb_entry=fdb_entry, thrift_attr_list=fdb_attr_list)

def sai_thrift_create_fdb_new(client, bv_id, mac, port, mac_action, type):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)
    bport = sai_thrift_get_bridge_port_by_port(client, port)
    assert (bport != SAI_NULL_OBJECT_ID)
    
    #value 0 represents static entry, id=0, represents entry type
    fdb_attribute1_value = sai_thrift_attribute_value_t(s32=type)
    fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_TYPE,
                                            value=fdb_attribute1_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute2_value = sai_thrift_attribute_value_t(oid=bport)
    fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute2_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute3_value = sai_thrift_attribute_value_t(s32=mac_action)
    fdb_attribute3 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_PACKET_ACTION,
                                            value=fdb_attribute3_value)
    fdb_attr_list = [fdb_attribute1, fdb_attribute2, fdb_attribute3]
    client.sai_thrift_create_fdb_entry(thrift_fdb_entry=fdb_entry, thrift_attr_list=fdb_attr_list)

def sai_thrift_create_fdb_tunnel(client, bv_id, mac, bport_oid, mac_action, ip_addr):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    #value 0 represents static entry, id=0, represents entry type
    fdb_attribute1_value = sai_thrift_attribute_value_t(s32=SAI_FDB_ENTRY_TYPE_STATIC)
    fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_TYPE,
                                            value=fdb_attribute1_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute2_value = sai_thrift_attribute_value_t(oid=bport_oid)
    fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute2_value)
    #value oid represents object id, id=1 represents port id
    fdb_attribute3_value = sai_thrift_attribute_value_t(s32=mac_action)
    fdb_attribute3 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_PACKET_ACTION,
                                            value=fdb_attribute3_value)
                                            
    #value oid represents object id, ip address
    addr = sai_thrift_ip_t(ip4=ip_addr)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    fdb_attribute4_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    fdb_attribute4 = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_ENDPOINT_IP,
                                             value=fdb_attribute4_value)
                                        
    fdb_attr_list = [fdb_attribute1, fdb_attribute2, fdb_attribute3, fdb_attribute4]
    client.sai_thrift_create_fdb_entry(thrift_fdb_entry=fdb_entry, thrift_attr_list=fdb_attr_list)
    
def sai_thrift_set_fdb_type(client, bv_id, mac, type):
    print "set fdb type"
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    #value 0 represents static entry, id=0, represents entry type
    fdb_attribute_value = sai_thrift_attribute_value_t(s32=type)
    fdb_attribute = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_TYPE,
                                            value=fdb_attribute_value)
                                            
    client.sai_thrift_set_fdb_entry_attribute(thrift_fdb_entry=fdb_entry, thrift_attr=fdb_attribute)

def sai_thrift_set_fdb_action(client, bv_id, mac, mac_action):
    print "set fdb action"
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    fdb_attribute_value = sai_thrift_attribute_value_t(s32=mac_action)
    fdb_attribute = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_PACKET_ACTION,
                                            value=fdb_attribute_value)
                                            
    client.sai_thrift_set_fdb_entry_attribute(thrift_fdb_entry=fdb_entry, thrift_attr=fdb_attribute)

def sai_thrift_set_fdb_port(client, bv_id, mac, port):
    print "set fdb port"
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)
    bport = sai_thrift_get_bridge_port_by_port(client, port)
    assert (bport != SAI_NULL_OBJECT_ID)

    #value oid represents object id, id=1 represents port id
    fdb_attribute_value = sai_thrift_attribute_value_t(oid=bport)
    fdb_attribute = sai_thrift_attribute_t(id=SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute_value)
    client.sai_thrift_set_fdb_entry_attribute(thrift_fdb_entry=fdb_entry, thrift_attr=fdb_attribute)

def sai_thrift_check_fdb_attribtue_type(client, bv_id, mac, type):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    fdb_attr_list = client.sai_thrift_get_fdb_entry_attribute(fdb_entry)
    attr_list = fdb_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_FDB_ENTRY_ATTR_TYPE:
            if attribute.value.s32 == type:
                return 1
            else:
                return 0
    print "SAI_FDB_ENTRY_ATTR_TYPE not found"
    return 0
def sai_thrift_check_fdb_attribtue_action(client, bv_id, mac, action):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    fdb_attr_list = client.sai_thrift_get_fdb_entry_attribute(fdb_entry)
    attr_list = fdb_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_FDB_ENTRY_ATTR_PACKET_ACTION:
            if attribute.value.s32 == action:
                return 1
            else:
                return 0
    print "SAI_FDB_ENTRY_ATTR_PACKET_ACTION not found"
    return 0
            
def sai_thrift_check_fdb_attribtue_port(client, bv_id, mac, port_oid):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)
    bport_oid = sai_thrift_get_bridge_port_by_port(client, port_oid)
    assert (bport_oid != SAI_NULL_OBJECT_ID)

    fdb_attr_list = client.sai_thrift_get_fdb_entry_attribute(fdb_entry)
    attr_list = fdb_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID:
            if attribute.value.oid == bport_oid:
                return 1
            else:
                return 0
    print "SAI_FDB_ENTRY_ATTR_BRIDGE_PORT_ID not found"
    return 0

def sai_thrift_check_fdb_exist(client, bv_id, mac):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)

    fdb_attr_list = client.sai_thrift_get_fdb_entry_attribute(fdb_entry)

    for attribute in fdb_attr_list.attr_list:
        print "found the entry"
        return 1

    print "not found the entry"
    return 0


def sai_thrift_delete_fdb(client, bv_id, mac, port):
    fdb_entry = sai_thrift_fdb_entry_t(mac_address=mac, bv_id=bv_id)
    client.sai_thrift_delete_fdb_entry(thrift_fdb_entry=fdb_entry)

def sai_thrift_flush_fdb_by_vlan(client, vlan_oid):
    fdb_attribute1_value = sai_thrift_attribute_value_t(oid=vlan_oid)
    fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_BV_ID,
                                            value=fdb_attribute1_value)
    fdb_attribute2_value = sai_thrift_attribute_value_t(s32=SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC)
    fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_ENTRY_TYPE,
                                            value=fdb_attribute2_value)
    fdb_attr_list = [fdb_attribute1, fdb_attribute2]
    client.sai_thrift_flush_fdb_entries(thrift_attr_list=fdb_attr_list)

def sai_thrift_flush_fdb_by_bridge_port(client, bport_id):
    fdb_attribute1_value = sai_thrift_attribute_value_t(oid=bport_id)
    fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute1_value)
    fdb_attribute2_value = sai_thrift_attribute_value_t(s32=SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC)
    fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_ENTRY_TYPE,
                                            value=fdb_attribute2_value)
    fdb_attr_list = [fdb_attribute1, fdb_attribute2]
    return client.sai_thrift_flush_fdb_entries(thrift_attr_list=fdb_attr_list)

def sai_thrift_flush_fdb(client,vlan_oid, bport_id, type):
    fdb_attr_list = []
    if SAI_NULL_OBJECT_ID != vlan_oid:
        fdb_attribute1_value = sai_thrift_attribute_value_t(oid=vlan_oid)
        fdb_attribute1 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_BV_ID,
                                            value=fdb_attribute1_value)
        fdb_attr_list.append(fdb_attribute1)
        
    if SAI_NULL_OBJECT_ID != bport_id:
        fdb_attribute2_value = sai_thrift_attribute_value_t(oid=bport_id)
        fdb_attribute2 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_BRIDGE_PORT_ID,
                                            value=fdb_attribute2_value)
        fdb_attr_list.append(fdb_attribute2)
    if type == SAI_FDB_FLUSH_ENTRY_TYPE_DYNAMIC or  type == SAI_FDB_FLUSH_ENTRY_TYPE_STATIC:
        fdb_attribute3_value = sai_thrift_attribute_value_t(s32=type)
        fdb_attribute3 = sai_thrift_attribute_t(id=SAI_FDB_FLUSH_ATTR_ENTRY_TYPE,
                                            value=fdb_attribute3_value)
        fdb_attr_list.append(fdb_attribute3)
    return client.sai_thrift_flush_fdb_entries(thrift_attr_list=fdb_attr_list)

def sai_thrift_create_virtual_router(client, v4_enabled, v6_enabled):
    #v4 enabled
    vr_attribute1_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
    vr_attribute1 = sai_thrift_attribute_t(id=SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V4_STATE,
                                           value=vr_attribute1_value)
    #v6 enabled
    vr_attribute2_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
    vr_attribute2 = sai_thrift_attribute_t(id=SAI_VIRTUAL_ROUTER_ATTR_ADMIN_V6_STATE,
                                           value=vr_attribute2_value)
    vr_attr_list = [vr_attribute1, vr_attribute2]
    vr_id = client.sai_thrift_create_virtual_router(thrift_attr_list=vr_attr_list)
    return vr_id

def sai_thrift_create_router_interface(client, vr_oid, type, port_oid, vlan_oid, v4_enabled, v6_enabled, mac, dot1d_bridge_id = 0, is_virtual = False):
    #vrf attribute
    rif_attr_list = []
    rif_attribute1_value = sai_thrift_attribute_value_t(oid=vr_oid)
    rif_attribute1 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID,
                                            value=rif_attribute1_value)
    rif_attr_list.append(rif_attribute1)
    rif_attribute2_value = sai_thrift_attribute_value_t(s32=type)
    rif_attribute2 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_TYPE,
                                            value=rif_attribute2_value)
    rif_attr_list.append(rif_attribute2)
    
    rif_attribute3_value = sai_thrift_attribute_value_t(oid=dot1d_bridge_id)
    rif_attribute3 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_BRIDGE_ID, value=rif_attribute3_value)
    rif_attr_list.append(rif_attribute3)
    
    rif_attribute_virtual_value = sai_thrift_attribute_value_t(booldata=is_virtual)
    rif_attribute_virtual = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_IS_VIRTUAL, value=rif_attribute_virtual_value)
    rif_attr_list.append(rif_attribute_virtual)

    if type == SAI_ROUTER_INTERFACE_TYPE_PORT:
        #port type and port id
        rif_attribute3_value = sai_thrift_attribute_value_t(oid=port_oid)
        rif_attribute3 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_PORT_ID,
                                                value=rif_attribute3_value)
        rif_attr_list.append(rif_attribute3)
    elif type == SAI_ROUTER_INTERFACE_TYPE_VLAN:
        #vlan type and vlan id
        rif_attribute3_value = sai_thrift_attribute_value_t(oid=vlan_oid)
        rif_attribute3 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_VLAN_ID,
                                                value=rif_attribute3_value)
        rif_attr_list.append(rif_attribute3)

    elif type == SAI_ROUTER_INTERFACE_TYPE_BRIDGE:
        #no need to specify port or vlan
        pass
    elif type == SAI_ROUTER_INTERFACE_TYPE_SUB_PORT:
        rif_attribute3_value = sai_thrift_attribute_value_t(oid=port_oid)
        rif_attribute3 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_PORT_ID,
                                                value=rif_attribute3_value)
        rif_attr_list.append(rif_attribute3)

        rif_attribute4_value = sai_thrift_attribute_value_t(oid=vlan_oid)
        rif_attribute4 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_VLAN_ID,
                                                value=rif_attribute4_value)
        rif_attr_list.append(rif_attribute4)

    if( not is_virtual):
        #v4_enabled
        rif_attribute4_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
        rif_attribute4 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE,
                                                value=rif_attribute4_value)
        rif_attr_list.append(rif_attribute4)
        
        rif_attribute4_1_value = sai_thrift_attribute_value_t(booldata=v4_enabled)
        rif_attribute4_1 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_V4_MCAST_ENABLE,
                                                value=rif_attribute4_1_value)
        rif_attr_list.append(rif_attribute4_1)
        #v6_enabled
        rif_attribute5_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
        rif_attribute5 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE,
                                                value=rif_attribute5_value)
        rif_attr_list.append(rif_attribute5)
        
        rif_attribute5_1_value = sai_thrift_attribute_value_t(booldata=v6_enabled)
        rif_attribute5_1 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_V6_MCAST_ENABLE,
                                                value=rif_attribute5_1_value)
        rif_attr_list.append(rif_attribute5_1)

    if mac:
        rif_attribute6_value = sai_thrift_attribute_value_t(mac=mac)
        rif_attribute6 = sai_thrift_attribute_t(id=SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS,
                                                value=rif_attribute6_value)
        rif_attr_list.append(rif_attribute6)

    rif_id = client.sai_thrift_create_router_interface(rif_attr_list)
    return rif_id

def sai_thrift_create_route(client, vr_id, addr_family, ip_addr, ip_mask, nhop, packet_action=None):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        mask = sai_thrift_ip_t(ip4=ip_mask)
        ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        mask = sai_thrift_ip_t(ip6=ip_mask)
        ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
    route_attribute1_value = sai_thrift_attribute_value_t(oid=nhop)
    route_attribute1 = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID,
                                              value=route_attribute1_value)

    route = sai_thrift_route_entry_t(vr_id, ip_prefix)
    route_attr_list = [route_attribute1]

    if packet_action != None:
        route_packet_action_value = sai_thrift_attribute_value_t(s32=packet_action)
        route_packet_action_attr = sai_thrift_attribute_t(id=SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION,
                                                          value=route_packet_action_value)
        route_attr_list.append(route_packet_action_attr)

    return client.sai_thrift_create_route(thrift_route_entry=route, thrift_attr_list=route_attr_list)
    

def sai_thrift_remove_route(client, vr_id, addr_family, ip_addr, ip_mask, nhop):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        mask = sai_thrift_ip_t(ip4=ip_mask)
        ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr, mask=mask)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        mask = sai_thrift_ip_t(ip6=ip_mask)
        ip_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr, mask=mask)
    route = sai_thrift_route_entry_t(vr_id, ip_prefix)
    return client.sai_thrift_remove_route(thrift_route_entry=route)

def sai_thrift_create_nhop(client, addr_family, ip_addr, rif_id):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    nhop_attribute1_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    nhop_attribute1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_IP,
                                             value=nhop_attribute1_value)
    nhop_attribute2_value = sai_thrift_attribute_value_t(oid=rif_id)
    nhop_attribute2 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID,
                                             value=nhop_attribute2_value)
    nhop_attribute3_value = sai_thrift_attribute_value_t(s32=SAI_NEXT_HOP_TYPE_IP)
    nhop_attribute3 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_TYPE,
                                             value=nhop_attribute3_value)
    nhop_attr_list = [nhop_attribute1, nhop_attribute2, nhop_attribute3]
    nhop = client.sai_thrift_create_next_hop(thrift_attr_list=nhop_attr_list)
    return nhop
    
def sai_thrift_create_mpls_nhop(client, addr_family, ip_addr, rif_id, label_list):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    nhop_attribute1_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    nhop_attribute1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_IP,
                                             value=nhop_attribute1_value)
    nhop_attribute2_value = sai_thrift_attribute_value_t(oid=rif_id)
    nhop_attribute2 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID,
                                             value=nhop_attribute2_value)
    nhop_attribute3_value = sai_thrift_attribute_value_t(s32=SAI_NEXT_HOP_TYPE_MPLS)
    nhop_attribute3 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_TYPE,
                                             value=nhop_attribute3_value)    
    #Label list
    #if label_list:
    #    mpls_label_list = sai_thrift_u32_list_t(count=len(label_list), u32list=label_list)
    #    nhop_attribute4_value = sai_thrift_attribute_value_t(u32list=mpls_label_list)
    #    nhop_attribute4 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_LABELSTACK,
    #                                        value=nhop_attribute4_value)
                                            
    mpls_label_list = sai_thrift_u32_list_t(count=len(label_list), u32list=label_list)
    nhop_attribute4_value = sai_thrift_attribute_value_t(u32list=mpls_label_list)
    nhop_attribute4 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_LABELSTACK,
                                            value=nhop_attribute4_value)
        
    nhop_attr_list = [nhop_attribute1, nhop_attribute2, nhop_attribute3, nhop_attribute4]
    nhop = client.sai_thrift_create_next_hop(thrift_attr_list=nhop_attr_list)
    return nhop

def sai_thrift_create_tunnel_nhop(client, addr_family, ip_addr, tunnel_id):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    nhop_attribute1_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    nhop_attribute1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_IP,
                                             value=nhop_attribute1_value)
    nhop_attribute2_value = sai_thrift_attribute_value_t(oid=tunnel_id)
    nhop_attribute2 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_TUNNEL_ID,
                                             value=nhop_attribute2_value)
    nhop_attribute3_value = sai_thrift_attribute_value_t(s32=SAI_NEXT_HOP_TYPE_TUNNEL_ENCAP)
    nhop_attribute3 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_ATTR_TYPE,
                                             value=nhop_attribute3_value)    
                                     
    nhop_attr_list = [nhop_attribute1, nhop_attribute2, nhop_attribute3]
    
    nhop = client.sai_thrift_create_next_hop(thrift_attr_list=nhop_attr_list)
    return nhop
    
def sai_thrift_remove_nhop(client, nhop_list):
    for nhop in nhop_list:
        client.sai_thrift_remove_next_hop(nhop)

def sai_thrift_create_neighbor(client, addr_family, rif_id, ip_addr, dmac):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    neighbor_attribute1_value = sai_thrift_attribute_value_t(mac=dmac)
    neighbor_attribute1 = sai_thrift_attribute_t(id=SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS,
                                                 value=neighbor_attribute1_value)
    neighbor_attr_list = [neighbor_attribute1]
    neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id, ip_address=ipaddr)
    return client.sai_thrift_create_neighbor_entry(neighbor_entry, neighbor_attr_list)

def sai_thrift_remove_neighbor(client, addr_family, rif_id, ip_addr, dmac):
    if addr_family == SAI_IP_ADDR_FAMILY_IPV4:
        addr = sai_thrift_ip_t(ip4=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    else:
        addr = sai_thrift_ip_t(ip6=ip_addr)
        ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    neighbor_entry = sai_thrift_neighbor_entry_t(rif_id=rif_id, ip_address=ipaddr)
    client.sai_thrift_remove_neighbor_entry(neighbor_entry)

def sai_thrift_create_next_hop_group(client):
    nhop_group_atr1_value = sai_thrift_attribute_value_t(s32=SAI_NEXT_HOP_GROUP_TYPE_ECMP)
    nhop_group_atr1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_ATTR_TYPE,
                                             value=nhop_group_atr1_value)
    nhop_group_attr_list = [nhop_group_atr1]
    return client.sai_thrift_create_next_hop_group(nhop_group_attr_list)

def sai_thrift_create_next_hop_protection_group(client):
    nhop_group_atr1_value = sai_thrift_attribute_value_t(s32=SAI_NEXT_HOP_GROUP_TYPE_PROTECTION)
    nhop_group_atr1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_ATTR_TYPE,
                                             value=nhop_group_atr1_value)
    nhop_group_attr_list = [nhop_group_atr1]
    return client.sai_thrift_create_next_hop_group(nhop_group_attr_list)

def sai_thrift_remove_next_hop_group(client, nhop_group_list):
    for nhop_group in nhop_group_list:
        client.sai_thrift_remove_next_hop_group(nhop_group)

def sai_thrift_create_next_hop_group_member(client, nhop_group, nhop, weight=None):
    nhop_gmember_atr1_value = sai_thrift_attribute_value_t(oid=nhop_group)
    nhop_gmember_atr1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID,
                                               value=nhop_gmember_atr1_value)
    nhop_gmember_atr2_value = sai_thrift_attribute_value_t(oid=nhop)
    nhop_gmember_atr2 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID,
                                               value=nhop_gmember_atr2_value)
    if weight != None:
        nhop_gmember_atr3_value = sai_thrift_attribute_value_t(u32=weight)
        nhop_gmember_atr3 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_WEIGHT,
                                                   value=nhop_gmember_atr3_value)
        nhop_gmember_attr_list = [nhop_gmember_atr1, nhop_gmember_atr2, nhop_gmember_atr3]
    else:
        nhop_gmember_attr_list = [nhop_gmember_atr1, nhop_gmember_atr2]
    return client.sai_thrift_create_next_hop_group_member(nhop_gmember_attr_list)

def sai_thrift_create_next_hop_protection_group_member(client, nhop_group, nhop, role):
    nhop_gmember_atr1_value = sai_thrift_attribute_value_t(oid=nhop_group)
    nhop_gmember_atr1 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_GROUP_ID,
                                               value=nhop_gmember_atr1_value)
    nhop_gmember_atr2_value = sai_thrift_attribute_value_t(oid=nhop)
    nhop_gmember_atr2 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_NEXT_HOP_ID,
                                               value=nhop_gmember_atr2_value)
    nhop_gmember_atr3_value = sai_thrift_attribute_value_t(s32=role)
    nhop_gmember_atr3 = sai_thrift_attribute_t(id=SAI_NEXT_HOP_GROUP_MEMBER_ATTR_CONFIGURED_ROLE,
                                               value=nhop_gmember_atr3_value)

    nhop_gmember_attr_list = [nhop_gmember_atr1, nhop_gmember_atr2, nhop_gmember_atr3]
    return client.sai_thrift_create_next_hop_group_member(nhop_gmember_attr_list)

def sai_thrift_remove_next_hop_group_member(client, nhop_gmember_list):
    for nhop_gmember in nhop_gmember_list:
        client.sai_thrift_remove_next_hop_group_member(nhop_gmember)

def sai_thrift_remove_next_hop_from_group(client, nhop_list):
    for hnop in nhop_list:
        client.sai_thrift_remove_next_hop_from_group(hnop)

def sai_thrift_create_lag(client, port_list, is_bridged=True):
    lag = client.sai_thrift_create_lag([])

    if is_bridged:
        sai_thrift_create_bridge_port(client, lag)

    return lag

def sai_thrift_remove_lag(client, lag_oid):
    bport_oid = sai_thrift_get_bridge_port_by_port(client, lag_oid)

    if bport_oid != SAI_NULL_OBJECT_ID:
        status = client.sai_thrift_remove_bridge_port(bport_oid)
        assert (status == SAI_STATUS_SUCCESS)

    status = client.sai_thrift_remove_lag(lag_oid)
    assert (status == SAI_STATUS_SUCCESS)

def sai_thrift_create_lag_member(client, lag_id, port_id):
    bport_oid = sai_thrift_get_bridge_port_by_port(client, port_id)
    assert (bport_oid != SAI_NULL_OBJECT_ID)

    status = client.sai_thrift_remove_bridge_port(bport_oid)
    assert (status == SAI_STATUS_SUCCESS)

    lag_member_attr1_value = sai_thrift_attribute_value_t(oid=lag_id)
    lag_member_attr1 = sai_thrift_attribute_t(id=SAI_LAG_MEMBER_ATTR_LAG_ID,
                                              value=lag_member_attr1_value)
    lag_member_attr2_value = sai_thrift_attribute_value_t(oid=port_id)
    lag_member_attr2 = sai_thrift_attribute_t(id=SAI_LAG_MEMBER_ATTR_PORT_ID,
                                              value=lag_member_attr2_value)
    lag_member_attr_list = [lag_member_attr1, lag_member_attr2]
    lag_member_id = client.sai_thrift_create_lag_member(lag_member_attr_list)
    return lag_member_id

def sai_thrift_remove_lag_member(client, lag_member_oid):
    attrs = client.sai_thrift_get_lag_member_attribute(lag_member_oid)
    port_id = SAI_NULL_OBJECT_ID

    for a in attrs.attr_list:
        if a.id == SAI_LAG_MEMBER_ATTR_PORT_ID:
	    port_id = a.value.oid
            break

    assert (port_id != SAI_NULL_OBJECT_ID)

    status = client.sai_thrift_remove_lag_member(lag_member_oid)
    assert (status == SAI_STATUS_SUCCESS)

    sai_thrift_create_bridge_port(client, port_id)

def sai_thrift_create_stp_entry(client, vlan_list):
    vlanlist=sai_thrift_vlan_list_t(vlan_count=len(vlan_list), vlan_list=vlan_list)
    stp_attribute1_value = sai_thrift_attribute_value_t(vlanlist=vlanlist)
    stp_attribute1 = sai_thrift_attribute_t(id=SAI_STP_ATTR_VLAN_LIST,
                                            value=stp_attribute1_value)
    stp_attr_list = [stp_attribute1]
    stp_id = client.sai_thrift_create_stp_entry(stp_attr_list)
    return stp_id

def sai_thrift_create_hostif(client,
                             hif_type,
                             hif_obj_id,
                             hif_name):
    attr_list=[]

    atr_value=sai_thrift_attribute_value_t(s32=hif_type)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_ATTR_TYPE,
                               value=atr_value)
    attr_list.append(atr)

    atr_value=sai_thrift_attribute_value_t(oid=hif_obj_id)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_ATTR_OBJ_ID,
                               value=atr_value)
    attr_list.append(atr)

    atr_value=sai_thrift_attribute_value_t(chardata=hif_name)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_ATTR_NAME,
                               value=atr_value)
    attr_list.append(atr)

    return client.sai_thrift_create_hostif(attr_list)

def sai_thrift_create_hostif_trap(client,
                                  trap_type,
                                  packet_action,
                                  trap_priority=None,
                                  exclude_port_list=None,
                                  trap_group=None):
    attr_list=[]

    atr_value=sai_thrift_attribute_value_t(s32=trap_type)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_TYPE,
                               value=atr_value)
    attr_list.append(atr)

    atr_value=sai_thrift_attribute_value_t(s32=packet_action)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_PACKET_ACTION,
                               value=atr_value)
    attr_list.append(atr)

    if trap_priority != None:
        atr_value=sai_thrift_attribute_value_t(u32=trap_priority)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_PRIORITY,
                                   value=atr_value)
        attr_list.append(atr)

    if trap_priority != None:
        atr_value=sai_thrift_attribute_value_t(objlist=exclude_port_list)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_EXCLUDE_PORT_LIST,
                                   value=atr_value)
        attr_list.append(atr)

    if trap_group != None:
        atr_value=sai_thrift_attribute_value_t(oid=trap_group)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_GROUP,
                                   value=atr_value)
        attr_list.append(atr)

    trap_id = client.sai_thrift_create_hostif_trap(attr_list)
    return trap_id

def sai_thrift_remove_hostif_trap(client,
                                  trap_id):
    client.sai_thrift_remove_hostif_trap(trap_id)

def sai_thrift_set_hostif_trap_attribute(client,
                                         trap_type,
                                         packet_action,
                                         trap_priority=None,
                                         exclude_port_list=None,
                                         trap_group=None):
    attr_list=[]

    atr_value=sai_thrift_attribute_value_t(s32=trap_type)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_TYPE,
                               value=atr_value)
    attr_list.append(atr)

    atr_value=sai_thrift_attribute_value_t(s32=packet_action)
    atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_PACKET_ACTION,
                               value=atr_value)
    attr_list.append(atr)

    if trap_priority != None:
        atr_value=sai_thrift_attribute_value_t(u32=trap_priority)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_PRIORITY,
                                   value=atr_value)
        attr_list.append(atr)

    if exclude_port_list != None:
        atr_value=sai_thrift_attribute_value_t(objlist=exclude_port_list)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_EXCLUDE_PORT_LIST,
                                   value=atr_value)
        attr_list.append(atr)

    if trap_group != None:
        atr_value=sai_thrift_attribute_value_t(oid=trap_group)
        atr=sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_ATTR_TRAP_GROUP,
                                   value=atr_value)
        attr_list.append(atr)

    client.sai_thrift_set_hostif_trap_attribute(attr_list)

def sai_thrift_create_hostif_trap_group(client, queue_id, policer_id=None):
    attr_list = []
    attribute_value = sai_thrift_attribute_value_t(u32=queue_id)
    attribute = sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_GROUP_ATTR_QUEUE, value=attribute_value)
    attr_list.append(attribute)

    if policer_id != None:
        policer_attr_value = sai_thrift_attribute_value_t(oid=policer_id)
        policer_attr = sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_GROUP_ATTR_POLICER, value=policer_attr_value)
        attr_list.append(policer_attr)

    trap_group = client.sai_thrift_create_hostif_trap_group(thrift_attr_list=attr_list)
    return trap_group

def sai_thrift_remove_hostif_trap_group(client,
                                        trap_group):
    client.sai_thrift_remove_hostif_trap_group(trap_group)

def sai_thrift_set_hostif_trap_group(client, trap_group_id, policer_id):
    policer_attr_value = sai_thrift_attribute_value_t(oid=policer_id)
    policer_attr = sai_thrift_attribute_t(id=SAI_HOSTIF_TRAP_GROUP_ATTR_POLICER, value=policer_attr_value)
    status = client.sai_thrift_set_hostif_trap_group(trap_group_id, thrift_attr=policer_attr)
    return status

def sai_thrift_create_policer(client,
                              meter_type,
                              mode,
                              cir,
                              red_action):
    attr_list = []

    meter_attr_value = sai_thrift_attribute_value_t(s32=meter_type)
    meter_attr = sai_thrift_attribute_t(id=SAI_POLICER_ATTR_METER_TYPE, value=meter_attr_value)

    mode_attr_value = sai_thrift_attribute_value_t(s32=mode)
    mode_attr = sai_thrift_attribute_t(id=SAI_POLICER_ATTR_MODE, value=mode_attr_value)

    cir_attr_value = sai_thrift_attribute_value_t(u64=cir)
    cir_attr = sai_thrift_attribute_t(id=SAI_POLICER_ATTR_CIR, value=cir_attr_value)

    red_action_attr_val = sai_thrift_attribute_value_t(s32=red_action)
    red_action_attr = sai_thrift_attribute_t(id=SAI_POLICER_ATTR_RED_PACKET_ACTION, value=red_action_attr_val)

    attr_list.append(meter_attr)
    attr_list.append(mode_attr)
    attr_list.append(cir_attr)
    attr_list.append(red_action_attr)
    policer_id = client.sai_thrift_create_policer(attr_list)

    return policer_id

def sai_thrift_create_acl_table(client,
                                table_stage,
                                table_bind_point_list,
                                addr_family,
                                mac_src, mac_dst,
                                ip_src, ip_dst,
                                ip_proto,
                                in_ports, out_ports,
                                in_port, out_port,
                                src_l4_port, dst_l4_port):

    acl_attr_list = []

    if table_stage != None:
        attribute_value = sai_thrift_attribute_value_t(s32=table_stage)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_ACL_STAGE,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if table_bind_point_list != None:
        acl_table_bind_point_list = sai_thrift_s32_list_t(count=len(table_bind_point_list), s32list=table_bind_point_list)
        attribute_value = sai_thrift_attribute_value_t(s32list=acl_table_bind_point_list)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_ACL_BIND_POINT_TYPE_LIST,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if mac_src != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_SRC_MAC,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if mac_dst != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_DST_MAC,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if ip_src != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_SRC_IP,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if ip_dst != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_DST_IP,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if ip_proto != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_IP_PROTOCOL,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if in_ports:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_IN_PORTS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if out_ports:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_OUT_PORTS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if in_port != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_IN_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if out_port != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_OUT_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if src_l4_port != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_L4_SRC_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if dst_l4_port != None:
        attribute_value = sai_thrift_attribute_value_t(booldata=1)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_ATTR_FIELD_L4_DST_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    acl_table_id = client.sai_thrift_create_acl_table(acl_attr_list)
    return acl_table_id

def sai_thrift_create_acl_entry(client,
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
                                in_port_list, out_port_list,
                                in_port, out_port,
                                src_l4_port, dst_l4_port,
                                ingress_mirror, egress_mirror,
                                new_svlan, new_scos,
                                new_cvlan, new_ccos,
                                deny_learn, ingress_samplepacket=None):
    acl_attr_list = []

    #ACL table OID
    attribute_value = sai_thrift_attribute_value_t(oid=acl_table_id)
    attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_TABLE_ID,
                                       value=attribute_value)
    acl_attr_list.append(attribute)

    #Priority
    if entry_priority != None:
        attribute_value = sai_thrift_attribute_value_t(u32=entry_priority)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_PRIORITY,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    # Admin State
    attribute_value = sai_thrift_attribute_value_t(booldata=admin_state)
    attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ADMIN_STATE,
                                           value=attribute_value)
    acl_attr_list.append(attribute)
    #MAC source
    if mac_src != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(mac=mac_src), mask = sai_thrift_acl_mask_t(mac=mac_src_mask)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_SRC_MAC,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #MAC destination
    if mac_dst != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(mac=mac_dst), mask = sai_thrift_acl_mask_t(mac=mac_dst_mask)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_DST_MAC,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #svlan id
    if svlan_id != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u16=svlan_id), mask =sai_thrift_acl_mask_t(u16=U16MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_OUTER_VLAN_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #svlan pri
    if svlan_pri != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=svlan_pri), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_OUTER_VLAN_PRI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #svlan cfi
    if svlan_cfi != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=svlan_cfi), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_OUTER_VLAN_CFI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #cvlan id
    if cvlan_id != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u16=cvlan_id), mask =sai_thrift_acl_mask_t(u16=U16MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_INNER_VLAN_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #cvlan pri
    if cvlan_pri != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=cvlan_pri), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_INNER_VLAN_PRI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #cvlan cfi
    if cvlan_cfi != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=cvlan_cfi), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_INNER_VLAN_CFI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Ip source
    if ip_src != None:
        if is_ipv6 == True:
            attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(ip6=ip_src), mask =sai_thrift_acl_mask_t(ip6=ip_src_mask)))
            attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_SRC_IPV6,
                                           value=attribute_value)
        else:
            attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(ip4=ip_src), mask =sai_thrift_acl_mask_t(ip4=ip_src_mask)))
            attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_SRC_IP,
                                               value=attribute_value)
        acl_attr_list.append(attribute)

    #Ip destination
    if ip_dst != None:
        if is_ipv6 == True:
            attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(ip6=ip_dst), mask =sai_thrift_acl_mask_t(ip6=ip_dst_mask)))
            attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_DST_IPV6,
                                               value=attribute_value)
        else:
            attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(ip4=ip_dst), mask =sai_thrift_acl_mask_t(ip4=ip_dst_mask)))
            attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_DST_IP,
                                               value=attribute_value)
        acl_attr_list.append(attribute)
    
    #Ip tos
    if ip_tos != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=ip_tos), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_TOS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #Ip ecn
    if ip_ecn != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=ip_ecn), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_ECN,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #Ip dscp
    if ip_dscp != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=ip_dscp), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_DSCP,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #Ip ttl
    if ip_ttl != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u8=ip_ttl), mask =sai_thrift_acl_mask_t(u8=U8MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_TTL,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #Input ports
    if in_port_list:
        acl_port_list = sai_thrift_object_list_t(count=len(in_port_list), object_id_list=in_port_list)
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(objlist=acl_port_list)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_IN_PORTS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Output ports
    if out_port_list:
        acl_port_list = sai_thrift_object_list_t(count=len(out_port_list), object_id_list=out_port_list)
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(objlist=acl_port_list)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_OUT_PORTS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Input port
    if in_port != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(oid=in_port)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_IN_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Output port
    if out_port != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(oid=out_port)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_OUT_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #L4 Source port
    if src_l4_port != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u16=src_l4_port),
                                                                                            mask = sai_thrift_acl_mask_t(u16=U16MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_L4_SRC_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #L4 Destination port
    if dst_l4_port != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(enable = True, data = sai_thrift_acl_data_t(u16=dst_l4_port),
                                                                                            mask = sai_thrift_acl_mask_t(u16=U16MASKFULL)))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_FIELD_L4_DST_PORT,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Packet action
    if action != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(s32=action),
                                                                                              enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_PACKET_ACTION,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
  
    #Ingress mirroring 
    if ingress_mirror:
        igs_mirror_list = sai_thrift_object_list_t(count=len(ingress_mirror), object_id_list=ingress_mirror)
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(enable = True,
                                                                                              parameter = sai_thrift_acl_parameter_t(objlist=igs_mirror_list))) 
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_MIRROR_INGRESS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Egress mirroring
    if egress_mirror:
        egs_mirror_list = sai_thrift_object_list_t(count=len(egress_mirror), object_id_list=egress_mirror)
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(objlist=egs_mirror_list),
                                                                                              enable = True)) 
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_MIRROR_EGRESS,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #new svlan
    if new_svlan != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(u16=new_svlan),
                                                                                              enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_SET_OUTER_VLAN_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #new scos
    if new_scos != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(u8=new_scos),
                                                                                              enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_SET_OUTER_VLAN_PRI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #new cvlan
    if new_cvlan != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(u16=new_cvlan),
                                                                                              enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_SET_INNER_VLAN_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #new ccos
    if new_ccos != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(u8=new_ccos),
                                                                                              enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_SET_INNER_VLAN_PRI,
                                           value=attribute_value)
        acl_attr_list.append(attribute)
        
    #deny learning
    if deny_learn != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_SET_DO_NOT_LEARN,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    #Ingress samplepacket
    if ingress_samplepacket != None:
        attribute_value = sai_thrift_attribute_value_t(aclaction=sai_thrift_acl_action_data_t(parameter = sai_thrift_acl_parameter_t(oid=ingress_samplepacket), enable = True))
        attribute = sai_thrift_attribute_t(id=SAI_ACL_ENTRY_ATTR_ACTION_INGRESS_SAMPLEPACKET_ENABLE, value=attribute_value)
        acl_attr_list.append(attribute)

    acl_entry_id = client.sai_thrift_create_acl_entry(acl_attr_list)
    return acl_entry_id

def sai_thrift_create_acl_table_group(client,
                                      group_stage,
                                      group_bind_point_list,
                                      group_type):
    acl_attr_list = []

    if group_stage != None:
        attribute_value = sai_thrift_attribute_value_t(s32=group_stage)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_ATTR_ACL_STAGE,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if group_bind_point_list != None:
        acl_group_bind_point_list = sai_thrift_s32_list_t(count=len(group_bind_point_list), s32list=group_bind_point_list)
        attribute_value = sai_thrift_attribute_value_t(s32list=acl_group_bind_point_list)

        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_ATTR_ACL_BIND_POINT_TYPE_LIST,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if group_type != None:
        attribute_value = sai_thrift_attribute_value_t(s32=group_type)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_ATTR_TYPE,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    acl_table_group_id = client.sai_thrift_create_acl_table_group(acl_attr_list)
    return acl_table_group_id

def sai_thrift_create_acl_table_group_member(client,
                                             acl_table_group_id,
                                             acl_table_id,
                                             group_member_priority):
    acl_attr_list = []

    if acl_table_group_id != None:
        attribute_value = sai_thrift_attribute_value_t(oid=acl_table_group_id)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_MEMBER_ATTR_ACL_TABLE_GROUP_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if acl_table_id != None:
        attribute_value = sai_thrift_attribute_value_t(oid=acl_table_id)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_MEMBER_ATTR_ACL_TABLE_ID,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    if group_member_priority != None:
        attribute_value = sai_thrift_attribute_value_t(u32=group_member_priority)
        attribute = sai_thrift_attribute_t(id=SAI_ACL_TABLE_GROUP_MEMBER_ATTR_PRIORITY,
                                           value=attribute_value)
        acl_attr_list.append(attribute)

    acl_table_group_member_id = client.sai_thrift_create_acl_table_group_member(acl_attr_list)
    return acl_table_group_member_id

def sai_thrift_create_hash(client, field_list, udf_group_list):
    hash_attr_list = []

    #Hash field list
    if field_list:
        hash_field_list = sai_thrift_s32_list_t(count=len(field_list), s32list=field_list)
        attribute1_value = sai_thrift_attribute_value_t(s32list=hash_field_list)
        attribute1 = sai_thrift_attribute_t(id=SAI_HASH_ATTR_NATIVE_HASH_FIELD_LIST,
                                            value=attribute1_value)
        hash_attr_list.append(attribute1)

    #UDF group list 
    if udf_group_list:
        hash_udf_group_list = sai_thrift_object_list_t(count=len(udf_group_list), object_id_list=udf_group_list)
        attribute2_value = sai_thrift_attribute_value_t(objlist=hash_udf_group_list)
        attribute2 = sai_thrift_attribute_t(id=SAI_HASH_ATTR_UDF_GROUP_LIST,
                                            value=attribute2_value)
        hash_attr_list.append(attribute2)
        
    hash_id = client.sai_thrift_create_hash(hash_attr_list)
    return hash_id
    
def sai_thrift_create_udf_group(client, group_type, group_length):
    udf_group_attr_list = []
    
    #group_type
    attribute1_value = sai_thrift_attribute_value_t(s32=group_type)
    attribute1 = sai_thrift_attribute_t(id=SAI_UDF_GROUP_ATTR_TYPE,
                                        value=attribute1_value)
    udf_group_attr_list.append(attribute1)
    
    #group_length
    attribute2_value = sai_thrift_attribute_value_t(u16=group_length)
    attribute2 = sai_thrift_attribute_t(id=SAI_UDF_GROUP_ATTR_LENGTH,
                                        value=attribute2_value)
    udf_group_attr_list.append(attribute2)
    
    udf_group_id = client.sai_thrift_create_udf_group(udf_group_attr_list)
    return udf_group_id
                                
def sai_thrift_create_udf_match(client, 
                               l2_type, l2_type_mask,
                               l3_type, l3_type_mask,
                               gre_type,gre_type_mask,
                               priority):
    udf_match_attr_list = []
        
    #l2_type
    if l2_type != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(data = sai_thrift_acl_data_t(u16=l2_type),
                                                                                            mask = sai_thrift_acl_mask_t(u16=l2_type_mask)))
        attribute = sai_thrift_attribute_t(id=SAI_UDF_MATCH_ATTR_L2_TYPE,
                                           value=attribute_value)
        udf_match_attr_list.append(attribute)
    
    #l3_type
    if l3_type != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(data = sai_thrift_acl_data_t(u8=l3_type),
                                                                                            mask = sai_thrift_acl_mask_t(u8=l3_type_mask)))
        attribute = sai_thrift_attribute_t(id=SAI_UDF_MATCH_ATTR_L3_TYPE,
                                           value=attribute_value)
        udf_match_attr_list.append(attribute)
        
    #gre_type
    if gre_type != None:
        attribute_value = sai_thrift_attribute_value_t(aclfield=sai_thrift_acl_field_data_t(data = sai_thrift_acl_data_t(u16=gre_type),
                                                                                            mask = sai_thrift_acl_mask_t(u16=gre_type_mask)))
        attribute = sai_thrift_attribute_t(id=SAI_UDF_MATCH_ATTR_GRE_TYPE,
                                           value=attribute_value)
        udf_match_attr_list.append(attribute)
        
    #priority
    attribute_value = sai_thrift_attribute_value_t(u8=priority)
    attribute = sai_thrift_attribute_t(id=SAI_UDF_MATCH_ATTR_PRIORITY,
                                        value=attribute_value)
    udf_match_attr_list.append(attribute)
    
    udf_match_id = client.sai_thrift_create_udf_match(udf_match_attr_list)
    return udf_match_id
        
def sai_thrift_create_udf(client, match_id, group_id, base, offset, 
                          hash_mask_list):
    udf_attr_list = []

    #match_id
    attribute1_value = sai_thrift_attribute_value_t(oid=match_id)
    attribute1 = sai_thrift_attribute_t(id=SAI_UDF_ATTR_MATCH_ID,
                                        value=attribute1_value)
    udf_attr_list.append(attribute1)
    
    #group_id
    attribute2_value = sai_thrift_attribute_value_t(oid=group_id)
    attribute2 = sai_thrift_attribute_t(id=SAI_UDF_ATTR_GROUP_ID,
                                        value=attribute2_value)
    udf_attr_list.append(attribute2)
    
    #base
    attribute3_value = sai_thrift_attribute_value_t(s32=base)
    attribute3 = sai_thrift_attribute_t(id=SAI_UDF_ATTR_BASE,
                                        value=attribute3_value)
    udf_attr_list.append(attribute3)
    
    #offset
    attribute4_value = sai_thrift_attribute_value_t(u16=offset)
    attribute4 = sai_thrift_attribute_t(id=SAI_UDF_ATTR_OFFSET,
                                        value=attribute4_value)
    udf_attr_list.append(attribute4)
    
    #Hash mask list
    if hash_mask_list:
        hash_mask_list_tmp = sai_thrift_u8_list_t(count=len(hash_mask_list), u8list=hash_mask_list)
        attribute5_value = sai_thrift_attribute_value_t(u8list=hash_mask_list_tmp)
        attribute5 = sai_thrift_attribute_t(id=SAI_UDF_ATTR_HASH_MASK,
                                            value=attribute5_value)
        udf_attr_list.append(attribute5)
    
    udf_id = client.sai_thrift_create_udf(udf_attr_list)
    return udf_id
    
def sai_thrift_create_mirror_session(client, mirror_type, port,
                                     vlan, vlan_priority, vlan_tpid, vlan_header_valid,
                                     src_mac, dst_mac,
                                     src_ip, dst_ip,
                                     encap_type, iphdr_version, ttl, tos, gre_type):
    mirror_attr_list = []

    #Mirror type
    attribute1_value = sai_thrift_attribute_value_t(s32=mirror_type)
    attribute1 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TYPE,
                                        value=attribute1_value)
    mirror_attr_list.append(attribute1)

    #Monitor port
    attribute2_value = sai_thrift_attribute_value_t(oid=port)
    attribute2 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_MONITOR_PORT,
                                        value=attribute2_value)
    mirror_attr_list.append(attribute2)

    if mirror_type == SAI_MIRROR_SESSION_TYPE_REMOTE:
        #vlan
        attribute3_value = sai_thrift_attribute_value_t(u16=vlan)
        attribute3 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_ID,
                                            value=attribute3_value)
        mirror_attr_list.append(attribute3)
        
        #vlan tpid
        if vlan_tpid is not None:
            attribute4_value = sai_thrift_attribute_value_t(u32=vlan_tpid)
            attribute4 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_TPID,
                                               value=attribute4_value)
            mirror_attr_list.append(attribute4)
        
        #vlan priority
        attribute5_value = sai_thrift_attribute_value_t(u8=vlan_priority)
        attribute5 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_PRI,
                                            value=attribute5_value)
        mirror_attr_list.append(attribute5)
    elif mirror_type == SAI_MIRROR_SESSION_TYPE_ENHANCED_REMOTE:
        #encap type
        attribute3_value = sai_thrift_attribute_value_t(s32=encap_type)
        attribute3 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_ERSPAN_ENCAPSULATION_TYPE,
                                            value=attribute3_value)
        mirror_attr_list.append(attribute3)

        #ip header version
        attribute4_value = sai_thrift_attribute_value_t(u8=iphdr_version)
        attribute4 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_IPHDR_VERSION,
                                            value=attribute4_value)
        mirror_attr_list.append(attribute4)

        assert((iphdr_version == 4) or (iphdr_version == 6))
        if iphdr_version == 4:
            addr_family = SAI_IP_ADDR_FAMILY_IPV4
        elif iphdr_version == 6:
            addr_family = SAI_IP_ADDR_FAMILY_IPV6

        #source ip
        addr = sai_thrift_ip_t(ip4=src_ip)
        src_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
        attribute5_value = sai_thrift_attribute_value_t(ipaddr=src_ip_addr)
        attribute5 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_IP_ADDRESS,
                                            value=attribute5_value)
        mirror_attr_list.append(attribute5)

        #dst ip
        addr = sai_thrift_ip_t(ip4=dst_ip)
        dst_ip_addr = sai_thrift_ip_address_t(addr_family=addr_family, addr=addr)
        attribute6_value = sai_thrift_attribute_value_t(ipaddr=dst_ip_addr)
        attribute6 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_IP_ADDRESS,
                                            value=attribute6_value)
        mirror_attr_list.append(attribute6)

        #source mac
        attribute7_value = sai_thrift_attribute_value_t(mac=src_mac)
        attribute7 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_SRC_MAC_ADDRESS,
                                            value=attribute7_value)
        mirror_attr_list.append(attribute7)
       
        #dst mac
        attribute8_value = sai_thrift_attribute_value_t(mac=dst_mac)
        attribute8 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_DST_MAC_ADDRESS,
                                            value=attribute8_value)
        mirror_attr_list.append(attribute8)

        attribute9_value = sai_thrift_attribute_value_t(u16=gre_type)
        attribute9 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_GRE_PROTOCOL_TYPE,value=attribute9_value)
        mirror_attr_list.append(attribute9)

        attribute10_value = sai_thrift_attribute_value_t(u8=ttl)
        attribute10 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TTL,value=attribute10_value)
        mirror_attr_list.append(attribute10)

        if vlan_tpid is not None:
            attribute11_value = sai_thrift_attribute_value_t(u32=vlan_tpid)
            attribute11 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_TPID,
                                                value=attribute11_value)
            mirror_attr_list.append(attribute11)

        #vlan
        if vlan is not None:
            attribute12_value = sai_thrift_attribute_value_t(u16=vlan)
            attribute12 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_ID,
                                                value=attribute12_value)
            mirror_attr_list.append(attribute12)

        #tos
        attribute13_value = sai_thrift_attribute_value_t(u8=tos)
        attribute13 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_TOS,
                                            value=attribute13_value)
        mirror_attr_list.append(attribute13)

        if vlan_header_valid is True:
            attribute14_value = sai_thrift_attribute_value_t(booldata=vlan_header_valid)
            attribute14 = sai_thrift_attribute_t(id=SAI_MIRROR_SESSION_ATTR_VLAN_HEADER_VALID,
                                                value=attribute14_value)
            mirror_attr_list.append(attribute14)

    mirror_id = client.sai_thrift_create_mirror_session(mirror_attr_list)
    return mirror_id
    
#def sai_thrift_create_inseg_entry(client, label, pop_nums, trip_prioroty=None, nhop, packet_action=None):
def sai_thrift_create_inseg_entry(client, label, pop_nums, trip_prioroty, nhop, packet_action):
    mpls_attr_list = []
    
    mpls = sai_thrift_inseg_entry_t(label)
     
    #pop_nums
    if pop_nums != None:
        mpls_attribute1_value = sai_thrift_attribute_value_t(u8=pop_nums)
        mpls_attribute1 = sai_thrift_attribute_t(id=SAI_INSEG_ENTRY_ATTR_NUM_OF_POP,
                                            value=mpls_attribute1_value)
        mpls_attr_list.append(mpls_attribute1)
    
    #trip_prioroty
    if trip_prioroty != None:
        mpls_attribute2_value = sai_thrift_attribute_value_t(u8=trip_prioroty)
        mpls_attribute2 = sai_thrift_attribute_t(id=SAI_INSEG_ENTRY_ATTR_TRAP_PRIORITY,
                                            value=mpls_attribute2_value)
        mpls_attr_list.append(mpls_attribute2)
    
    #nhop
    if nhop != None:
        mpls_attribute3_value = sai_thrift_attribute_value_t(oid=nhop)
        mpls_attribute3 = sai_thrift_attribute_t(id=SAI_INSEG_ENTRY_ATTR_NEXT_HOP_ID,
                                            value=mpls_attribute3_value)
        mpls_attr_list.append(mpls_attribute3)
    
    #packet_action
    if packet_action != None:
        mpls_action_value = sai_thrift_attribute_value_t(s32=packet_action)
        mpls_action_attr = sai_thrift_attribute_t(id=SAI_INSEG_ENTRY_ATTR_PACKET_ACTION,
                                                        value=mpls_action_value)
        mpls_attr_list.append(mpls_action_attr)
    
    return client.sai_thrift_create_inseg_entry(thrift_inseg_entry=mpls, thrift_attr_list=mpls_attr_list)
    
def sai_thrift_create_scheduler_profile(client, max_rate, algorithm=0):
    scheduler_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(u64=max_rate)
    attribute = sai_thrift_attribute_t(id=SAI_SCHEDULER_ATTR_MAX_BANDWIDTH_RATE ,
                                       value=attribute_value)
    scheduler_attr_list.append(attribute)
    attribute_value = sai_thrift_attribute_value_t(s32=algorithm)
    attribute = sai_thrift_attribute_t(id=SAI_SCHEDULER_ATTR_SCHEDULING_ALGORITHM ,
                                       value=attribute_value)
    scheduler_attr_list.append(attribute)
    scheduler_profile_id = client.sai_thrift_create_scheduler_profile(scheduler_attr_list)
    return scheduler_profile_id

def sai_thrift_create_buffer_profile(client, pool_id, size, threshold, xoff_th, xon_th):
    buffer_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(oid=pool_id)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_PROFILE_ATTR_POOL_ID ,
                                           value=attribute_value)
    buffer_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(u32=size)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_PROFILE_ATTR_BUFFER_SIZE ,
                                           value=attribute_value)
    buffer_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(u8=threshold)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_PROFILE_ATTR_SHARED_DYNAMIC_TH ,
                                           value=attribute_value)
    buffer_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(u32=xoff_th)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_PROFILE_ATTR_XOFF_TH ,
                                           value=attribute_value)
    buffer_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(u32=xon_th)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_PROFILE_ATTR_XON_TH ,
                                           value=attribute_value)
    buffer_attr_list.append(attribute)

    buffer_profile_id = client.sai_thrift_create_buffer_profile(buffer_attr_list)
    return buffer_profile_id

def sai_thrift_create_pool_profile(client, pool_type, size, threshold_mode):
    pool_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(s32=pool_type)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_POOL_ATTR_TYPE ,
                                           value=attribute_value)
    pool_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(u32=size)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_POOL_ATTR_SIZE ,
                                           value=attribute_value)
    pool_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(s32=threshold_mode)
    attribute = sai_thrift_attribute_t(id=SAI_BUFFER_POOL_ATTR_TH_MODE ,
                                           value=attribute_value)
    pool_attr_list.append(attribute)
    pool_id = client.sai_thrift_create_pool_profile(pool_attr_list)
    return pool_id

def sai_thrift_clear_all_counters(client):
    for port in sai_port_list:
        queue_list=[]
        client.sai_thrift_clear_port_all_stats(port)
        port_attr_list = client.sai_thrift_get_port_attribute(port)
        attr_list = port_attr_list.attr_list
        for attribute in attr_list:
            if attribute.id == SAI_PORT_ATTR_QOS_QUEUE_LIST:
                for queue_id in attribute.value.objlist.object_id_list:
                    queue_list.append(queue_id)

        cnt_ids=[]
        cnt_ids.append(SAI_QUEUE_STAT_PACKETS)
        for queue in queue_list:
            client.sai_thrift_clear_queue_stats(queue,cnt_ids,len(cnt_ids))

def sai_thrift_read_port_counters(client,port):
    port_cnt_ids=[]
    port_cnt_ids.append(SAI_PORT_STAT_IF_OUT_DISCARDS)
    port_cnt_ids.append(SAI_PORT_STAT_ETHER_STATS_DROP_EVENTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_0_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_1_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_2_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_3_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_4_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_5_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_6_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_PFC_7_TX_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_IF_OUT_OCTETS)
    port_cnt_ids.append(SAI_PORT_STAT_IF_OUT_UCAST_PKTS)
    port_cnt_ids.append(SAI_PORT_STAT_IF_IN_UCAST_PKTS)
    counters_results=[]
    counters_results = client.sai_thrift_get_port_stats(port,port_cnt_ids,len(port_cnt_ids))
    queue_list=[]
    port_attr_list = client.sai_thrift_get_port_attribute(port)
    attr_list = port_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_PORT_ATTR_QOS_QUEUE_LIST:
            for queue_id in attribute.value.objlist.object_id_list:
                queue_list.append(queue_id)
    cnt_ids=[]
    thrift_results=[]
    queue_counters_results=[]
    cnt_ids.append(SAI_QUEUE_STAT_PACKETS)
    queue1=0
    for queue in queue_list:
        if queue1 <= 7:
            thrift_results=client.sai_thrift_get_queue_stats(queue,cnt_ids,len(cnt_ids))
            queue_counters_results.append(thrift_results[0])
            queue1+=1
    return (counters_results, queue_counters_results)

def sai_thrift_create_vlan(client, vlan_id):
    vlan_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(u16=vlan_id)
    attribute = sai_thrift_attribute_t(id=SAI_VLAN_ATTR_VLAN_ID, value=attribute_value)
    vlan_attr_list.append(attribute)
    vlan_oid = client.sai_thrift_create_vlan(vlan_attr_list)
    return vlan_oid

def sai_thrift_create_vlan_member(client, vlan_oid, port_oid, tagging_mode):
    bport_oid = sai_thrift_get_bridge_port_by_port(client, port_oid)
    assert (bport_oid != SAI_NULL_OBJECT_ID)

    vlan_member_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(oid=vlan_oid)
    attribute = sai_thrift_attribute_t(id=SAI_VLAN_MEMBER_ATTR_VLAN_ID,
                                           value=attribute_value)
    vlan_member_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(oid=bport_oid)
    print bport_oid
    attribute = sai_thrift_attribute_t(id=SAI_VLAN_MEMBER_ATTR_BRIDGE_PORT_ID,
                                           value=attribute_value)
    vlan_member_attr_list.append(attribute)

    attribute_value = sai_thrift_attribute_value_t(s32=tagging_mode)
    attribute = sai_thrift_attribute_t(id=SAI_VLAN_MEMBER_ATTR_VLAN_TAGGING_MODE,
                                           value=attribute_value)
    vlan_member_attr_list.append(attribute)
    vlan_member_id = client.sai_thrift_create_vlan_member(vlan_member_attr_list)
    return vlan_member_id

def sai_thrift_vlan_remove_all_ports(client, vlan_oid):
        vlan_members_list = []

        vlan_attr_list = client.sai_thrift_get_vlan_attribute(vlan_oid)
        attr_list = vlan_attr_list.attr_list
        for attribute in attr_list:
            if attribute.id == SAI_VLAN_ATTR_MEMBER_LIST:
                for vlan_member in attribute.value.objlist.object_id_list:
                    vlan_members_list.append(vlan_member)

        for vlan_member in vlan_members_list:
            client.sai_thrift_remove_vlan_member(vlan_member)

def sai_thrift_vlan_remove_ports(client, vlan_oid, ports):
    vlan_members_list = []

    vlan_attr_list = client.sai_thrift_get_vlan_attribute(vlan_oid)
    attr_list = vlan_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_VLAN_ATTR_MEMBER_LIST:
            for vlan_member in attribute.value.objlist.object_id_list:
                attrs = client.sai_thrift_get_vlan_member_attribute(vlan_member)
                for a in attrs.attr_list:
                    if a.id == SAI_VLAN_MEMBER_ATTR_BRIDGE_PORT_ID:
                        port = sai_thrift_get_port_by_bridge_port(client, a.value.oid)
                        if port in ports:
                            vlan_members_list.append(vlan_member)

    for vlan_member in vlan_members_list:
        client.sai_thrift_remove_vlan_member(vlan_member)


def sai_thrift_lag_check_drop_untagged(client, lag_oid, flag):
    lag_attr_list = client.sai_thrift_get_lag_attribute(lag_oid)
    attr_list = lag_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_LAG_ATTR_DROP_UNTAGGED:
            if attribute.value.booldata == flag:
                return 1
            else:
                return 0
    print "SAI_LAG_ATTR_DROP_UNTAGGED not found"
    return 0

def sai_thrift_lag_check_drop_tagged(client, lag_oid, flag):
    lag_attr_list = client.sai_thrift_get_lag_attribute(lag_oid)
    attr_list = lag_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_LAG_ATTR_DROP_TAGGED:
            if attribute.value.booldata == flag:
                return 1
            else:
                return 0
    print "SAI_LAG_ATTR_DROP_TAGGED not found"
    return 0

def sai_thrift_lag_check_vlan_id(client, lag_oid, vlan_id):
    lag_attr_list = client.sai_thrift_get_lag_attribute(lag_oid)
    attr_list = lag_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_LAG_ATTR_PORT_VLAN_ID:
            if attribute.value.u16 == vlan_id:
                return 1
            else:
                return 0
    print "SAI_LAG_ATTR_PORT_VLAN_ID not found"
    return 0
def sai_thrift_set_port_shaper(client, port_id, max_rate):
    sched_prof_id=sai_thrift_create_scheduler_profile(client, max_rate)
    attr_value = sai_thrift_attribute_value_t(oid=sched_prof_id)
    attr = sai_thrift_attribute_t(id=SAI_PORT_ATTR_QOS_SCHEDULER_PROFILE_ID, value=attr_value)
    client.sai_thrift_set_port_attribute(port_id,attr)

def sai_thrift_vlan_check_max_learned_address(client, vlan_oid, max_num):
    print "check max learn address"
    vlan_attr_list = client.sai_thrift_get_vlan_attribute(vlan_oid)
    attr_list = vlan_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == SAI_VLAN_ATTR_MAX_LEARNED_ADDRESSES:
            print "max num%u" %attribute.value.u32
            if attribute.value.u32 == max_num:
                return 1
            else:
                return 0
    return 0
    
def sai_thrift_create_l2mc_group_member(client, grp_id, port_id):
    member_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
    attribute = sai_thrift_attribute_t(id=SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_GROUP_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    bport_oid = sai_thrift_get_bridge_port_by_port(client, port_id)
    assert (bport_oid != SAI_NULL_OBJECT_ID)
    
    attribute_value = sai_thrift_attribute_value_t(oid=bport_oid)
    attribute = sai_thrift_attribute_t(id=SAI_L2MC_GROUP_MEMBER_ATTR_L2MC_OUTPUT_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    member_id = client.sai_thrift_create_l2mc_group_member(member_attr_list)
    return member_id
	
def sai_thrift_create_l2mc_entry(client, l2mc_entry, grp_id = 0, packet_action = SAI_PACKET_ACTION_FORWARD):
    entry_attr_list = []
	
    attribute_value = sai_thrift_attribute_value_t(s32=packet_action)
    attribute = sai_thrift_attribute_t(id=SAI_L2MC_ENTRY_ATTR_PACKET_ACTION,
                                            value=attribute_value)
    entry_attr_list.append(attribute)

    if grp_id != 0:
        attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
        attribute = sai_thrift_attribute_t(id=SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID,
                                                value=attribute_value)
        entry_attr_list.append(attribute)

    return client.sai_thrift_create_l2mc_entry(l2mc_entry, entry_attr_list)

def sai_thrift_create_mcast_fdb_entry(client, mcast_fdb_entry, grp_id = 0, packet_action = SAI_PACKET_ACTION_FORWARD):
    entry_attr_list = []
	
    attribute_value = sai_thrift_attribute_value_t(s32=packet_action)
    attribute = sai_thrift_attribute_t(id=SAI_MCAST_FDB_ENTRY_ATTR_PACKET_ACTION,
                                            value=attribute_value)
    entry_attr_list.append(attribute)

    if grp_id != 0:
        attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
        attribute = sai_thrift_attribute_t(id=SAI_MCAST_FDB_ENTRY_ATTR_GROUP_ID,
                                                value=attribute_value)
        entry_attr_list.append(attribute)
	
    return client.sai_thrift_create_mcast_fdb_entry(mcast_fdb_entry, entry_attr_list)

def sai_thrift_create_ipmc_group_member(client, grp_id, output_id):
    member_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
    attribute = sai_thrift_attribute_t(id=SAI_IPMC_GROUP_MEMBER_ATTR_IPMC_GROUP_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    attribute_value = sai_thrift_attribute_value_t(oid=output_id)
    attribute = sai_thrift_attribute_t(id=SAI_IPMC_GROUP_MEMBER_ATTR_IPMC_OUTPUT_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    member_id = client.sai_thrift_create_ipmc_group_member(member_attr_list)
    return member_id

def sai_thrift_create_rpf_group_member(client, grp_id, l3if_id):
    member_attr_list = []
    attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
    attribute = sai_thrift_attribute_t(id=SAI_RPF_GROUP_MEMBER_ATTR_RPF_GROUP_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    attribute_value = sai_thrift_attribute_value_t(oid=l3if_id)
    attribute = sai_thrift_attribute_t(id=SAI_RPF_GROUP_MEMBER_ATTR_RPF_INTERFACE_ID,
                                           value=attribute_value)
    member_attr_list.append(attribute)
	
    member_id = client.sai_thrift_create_rpf_group_member(member_attr_list)
    return member_id
	
def sai_thrift_create_ipmc_entry(client, ipmc_entry, grp_id = 0, packet_action = SAI_PACKET_ACTION_FORWARD, rpf_grp_id = 0):
    entry_attr_list = []
    
    attribute_value = sai_thrift_attribute_value_t(s32=packet_action)
    attribute = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_PACKET_ACTION,
                                            value=attribute_value)
    entry_attr_list.append(attribute)

    if grp_id != 0:
        attribute_value = sai_thrift_attribute_value_t(oid=grp_id)
        attribute = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_OUTPUT_GROUP_ID,
                                                value=attribute_value)
        entry_attr_list.append(attribute)

    if rpf_grp_id != 0:
		attribute_value = sai_thrift_attribute_value_t(oid=rpf_grp_id)
		attribute = sai_thrift_attribute_t(id=SAI_IPMC_ENTRY_ATTR_RPF_GROUP_ID,
												value=attribute_value)
		entry_attr_list.append(attribute)
	
    return client.sai_thrift_create_ipmc_entry(ipmc_entry, entry_attr_list)

def sai_thrift_create_tunnel_map(client, type):
    tunnel_attr_list = []
    
    tunnel_attribute1_value = sai_thrift_attribute_value_t(s32=type)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ATTR_TYPE,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)
    
    return client.sai_thrift_create_tunnel_map(tunnel_attr_list)

def sai_thrift_create_tunnel_map_entry(client, type, tunnel_map_oid, key, value):
    tunnel_attr_list = []
    
    tunnel_attribute1_value = sai_thrift_attribute_value_t(s32=type)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_TUNNEL_MAP_TYPE,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)
    
    if SAI_TUNNEL_MAP_TYPE_VNI_TO_VLAN_ID == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(u16=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VLAN_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(u32=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)
    elif SAI_TUNNEL_MAP_TYPE_VLAN_ID_TO_VNI == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(u32=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(u16=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VLAN_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)
    elif SAI_TUNNEL_MAP_TYPE_VNI_TO_BRIDGE_IF == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(oid=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_BRIDGE_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(u32=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)
    elif SAI_TUNNEL_MAP_TYPE_BRIDGE_IF_TO_VNI == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(u32=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(oid=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_BRIDGE_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)
    elif SAI_TUNNEL_MAP_TYPE_VNI_TO_VIRTUAL_ROUTER_ID == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(oid=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VIRTUAL_ROUTER_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(u32=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)
    elif SAI_TUNNEL_MAP_TYPE_VIRTUAL_ROUTER_ID_TO_VNI == type:
        tunnel_attribute2_value = sai_thrift_attribute_value_t(u32=value)
        tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VNI_ID_VALUE,
                                            value=tunnel_attribute2_value)
        tunnel_attr_list.append(tunnel_attribute2)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(oid=key)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_VIRTUAL_ROUTER_ID_KEY,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)

    tunnel_attribute5_value = sai_thrift_attribute_value_t(oid=tunnel_map_oid)
    tunnel_attribute5 = sai_thrift_attribute_t(id=SAI_TUNNEL_MAP_ENTRY_ATTR_TUNNEL_MAP,
                                            value=tunnel_attribute5_value)
    tunnel_attr_list.append(tunnel_attribute5)
 
    return client.sai_thrift_create_tunnel_map_entry(tunnel_attr_list)

def sai_thrift_create_tunnel(client, underlay_if, overlay_if, ip_addr, encap_ttl_mode=SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL, encap_ttl_val=0, encap_dscp_mode=SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL, encap_dscp_val=0):
    tunnel_attr_list = []
    
    tunnel_attribute1_value = sai_thrift_attribute_value_t(s32=SAI_TUNNEL_TYPE_IPINIP)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_TYPE,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)
    tunnel_attribute2_value = sai_thrift_attribute_value_t(oid=underlay_if)
    tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_UNDERLAY_INTERFACE,
                                            value=tunnel_attribute2_value)
    tunnel_attr_list.append(tunnel_attribute2)
    tunnel_attribute3_value = sai_thrift_attribute_value_t(oid=overlay_if)
    tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_OVERLAY_INTERFACE,
                                            value=tunnel_attribute3_value)
    tunnel_attr_list.append(tunnel_attribute3)
    
    addr = sai_thrift_ip_t(ip4=ip_addr)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    tunnel_attribute4_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    tunnel_attribute4 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_SRC_IP,
                                             value=tunnel_attribute4_value)
    tunnel_attr_list.append(tunnel_attribute4)
    
    if encap_ttl_mode != SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL:
        tunnel_attribute5_value = sai_thrift_attribute_value_t(s32=encap_ttl_mode)
        tunnel_attribute5 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_TTL_MODE,
                                                value=tunnel_attribute5_value)
        tunnel_attr_list.append(tunnel_attribute5)
    
        tunnel_attribute_ttl_value = sai_thrift_attribute_value_t(u8=encap_ttl_val)
        tunnel_attribute_ttl = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_TTL_VAL,
                                                value=tunnel_attribute_ttl_value)
        tunnel_attr_list.append(tunnel_attribute_ttl)
    
    if encap_dscp_mode != SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL:
        tunnel_attribute6_value = sai_thrift_attribute_value_t(s32=encap_dscp_mode)
        tunnel_attribute6 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_DSCP_MODE,
                                                value=tunnel_attribute6_value)
        tunnel_attr_list.append(tunnel_attribute6)

        tunnel_attribute_dscp_value = sai_thrift_attribute_value_t(u8=encap_dscp_val)
        tunnel_attribute_dscp = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_DSCP_VAL,
                                                value=tunnel_attribute_dscp_value)
        tunnel_attr_list.append(tunnel_attribute_dscp)

    tunnel_attribute7_value = sai_thrift_attribute_value_t(s32=SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL)
    tunnel_attribute7 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_DECAP_TTL_MODE,
                                        value=tunnel_attribute7_value)
    tunnel_attr_list.append(tunnel_attribute7)
    
    tunnel_attribute8_value = sai_thrift_attribute_value_t(s32=SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL)
    tunnel_attribute8 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_DECAP_DSCP_MODE,
                                        value=tunnel_attribute8_value)
    tunnel_attr_list.append(tunnel_attribute8)
    
    return client.sai_thrift_create_tunnel(tunnel_attr_list)

def sai_thrift_create_tunnel_gre(client, underlay_if, overlay_if, ip_addr, gre_key, decap_ttl_mode=SAI_TUNNEL_TTL_MODE_UNIFORM_MODEL, decap_descp_mode=SAI_TUNNEL_DSCP_MODE_UNIFORM_MODEL):
    tunnel_attr_list = []
    
    tunnel_attribute1_value = sai_thrift_attribute_value_t(s32=SAI_TUNNEL_TYPE_IPINIP_GRE)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_TYPE,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)
    tunnel_attribute2_value = sai_thrift_attribute_value_t(oid=underlay_if)
    tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_UNDERLAY_INTERFACE,
                                            value=tunnel_attribute2_value)
    tunnel_attr_list.append(tunnel_attribute2)
    tunnel_attribute3_value = sai_thrift_attribute_value_t(oid=overlay_if)
    tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_OVERLAY_INTERFACE,
                                            value=tunnel_attribute3_value)
    tunnel_attr_list.append(tunnel_attribute3)
    
    addr = sai_thrift_ip_t(ip4=ip_addr)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    tunnel_attribute4_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    tunnel_attribute4 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_SRC_IP,
                                             value=tunnel_attribute4_value)
    tunnel_attr_list.append(tunnel_attribute4)
    tunnel_attribute5_value = sai_thrift_attribute_value_t(s32=decap_ttl_mode)
    tunnel_attribute5 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_DECAP_TTL_MODE,
                                            value=tunnel_attribute5_value)
    tunnel_attr_list.append(tunnel_attribute5)
    tunnel_attribute6_value = sai_thrift_attribute_value_t(s32=decap_descp_mode)
    tunnel_attribute6 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_DECAP_DSCP_MODE,
                                            value=tunnel_attribute6_value)
    tunnel_attr_list.append(tunnel_attribute6)

    tunnel_attribute7_value = sai_thrift_attribute_value_t(booldata=1)
    tunnel_attribute7 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_GRE_KEY_VALID,
                                            value=tunnel_attribute7_value)
    tunnel_attr_list.append(tunnel_attribute7)
 
    tunnel_attribute8_value = sai_thrift_attribute_value_t(u32=gre_key)
    tunnel_attribute8 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_GRE_KEY,
                                            value=tunnel_attribute8_value)
    tunnel_attr_list.append(tunnel_attribute8)
    
    return client.sai_thrift_create_tunnel(tunnel_attr_list)

def sai_thrift_create_tunnel_vxlan(client, ip_addr, encap_mapper_list, decap_mapper_list, underlay_if):
    tunnel_attr_list = []
    
    tunnel_attribute1_value = sai_thrift_attribute_value_t(s32=SAI_TUNNEL_TYPE_VXLAN)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_TYPE,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)

    tunnel_attribute2_value = sai_thrift_attribute_value_t(oid=underlay_if)
    tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_UNDERLAY_INTERFACE,
                                            value=tunnel_attribute2_value)
    tunnel_attr_list.append(tunnel_attribute2)
    
    addr = sai_thrift_ip_t(ip4=ip_addr)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    tunnel_attribute3_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_SRC_IP,
                                             value=tunnel_attribute3_value)
    tunnel_attr_list.append(tunnel_attribute3)

    #Encap mapper list
    if encap_mapper_list:
        tunnel_encap_mapper_list = sai_thrift_object_list_t(count=len(encap_mapper_list), object_id_list=encap_mapper_list)
        tunnel_attribute3_value = sai_thrift_attribute_value_t(objlist=tunnel_encap_mapper_list)
        tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_ENCAP_MAPPERS,
                                            value=tunnel_attribute3_value)
        tunnel_attr_list.append(tunnel_attribute3)

    #Decap mapper list 
    if decap_mapper_list:
        tunnel_decap_mapper_list = sai_thrift_object_list_t(count=len(decap_mapper_list), object_id_list=decap_mapper_list)
        tunnel_attribute4_value = sai_thrift_attribute_value_t(objlist=tunnel_decap_mapper_list)
        tunnel_attribute4 = sai_thrift_attribute_t(id=SAI_TUNNEL_ATTR_DECAP_MAPPERS,
                                            value=tunnel_attribute4_value)
        tunnel_attr_list.append(tunnel_attribute4)
        
    return client.sai_thrift_create_tunnel(tunnel_attr_list)
    
def sai_thrift_create_tunnel_term_table_entry(client, vr_id, ip_sa, ip_da, tunnel_id, type=SAI_TUNNEL_TERM_TABLE_ENTRY_TYPE_P2P, tunnel_type=SAI_TUNNEL_TYPE_IPINIP):
    tunnel_attr_list = []
    tunnel_attribute1_value = sai_thrift_attribute_value_t(oid=vr_id)
    tunnel_attribute1 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_VR_ID,
                                            value=tunnel_attribute1_value)
    tunnel_attr_list.append(tunnel_attribute1)
    tunnel_attribute2_value = sai_thrift_attribute_value_t(s32=type)
    tunnel_attribute2 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_TYPE,
                                            value=tunnel_attribute2_value)
    tunnel_attr_list.append(tunnel_attribute2)
    addr = sai_thrift_ip_t(ip4=ip_sa)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    tunnel_attribute3_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    tunnel_attribute3 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_SRC_IP,
                                             value=tunnel_attribute3_value)
    tunnel_attr_list.append(tunnel_attribute3)

    addr = sai_thrift_ip_t(ip4=ip_da)
    ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4, addr=addr)
    #addr = sai_thrift_ip_t(ip6=ip_addr)
    #ipaddr = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6, addr=addr)
    tunnel_attribute4_value = sai_thrift_attribute_value_t(ipaddr=ipaddr)
    tunnel_attribute4 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_DST_IP,
                                             value=tunnel_attribute4_value)
    tunnel_attr_list.append(tunnel_attribute4)
    tunnel_attribute5_value = sai_thrift_attribute_value_t(s32=tunnel_type)
    tunnel_attribute5 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_TUNNEL_TYPE,
                                            value=tunnel_attribute5_value)
    tunnel_attr_list.append(tunnel_attribute5)
    tunnel_attribute6_value = sai_thrift_attribute_value_t(oid=tunnel_id)
    tunnel_attribute6 = sai_thrift_attribute_t(id=SAI_TUNNEL_TERM_TABLE_ENTRY_ATTR_ACTION_TUNNEL_ID,
                                            value=tunnel_attribute6_value)
    tunnel_attr_list.append(tunnel_attribute6)

    return client.sai_thrift_create_tunnel_term_table_entry(tunnel_attr_list)
    
def sai_thrift_create_isolation_group(client, type):
    attr_list = []
    
    attr_value = sai_thrift_attribute_value_t(u32=type)
    attr = sai_thrift_attribute_t(id=SAI_ISOLATION_GROUP_ATTR_TYPE,
                                            value=attr_value)
    attr_list.append(attr)                                      
    return client.sai_thrift_create_isolation_group(attr_list)                                 

def sai_thrift_remove_isolation_group(client, iso_grp_oid):                                      
    return client.sai_thrift_remove_isolation_group(iso_grp_oid)   

def sai_thrift_create_isolation_group_member(client, group_oid, member_oid):
    attr_list = []
    
    attr_value = sai_thrift_attribute_value_t(oid=group_oid)
    attr = sai_thrift_attribute_t(id=SAI_ISOLATION_GROUP_MEMBER_ATTR_ISOLATION_GROUP_ID, value=attr_value)
    attr_list.append(attr)

    attr_value = sai_thrift_attribute_value_t(oid=member_oid)
    attr = sai_thrift_attribute_t(id=SAI_ISOLATION_GROUP_MEMBER_ATTR_ISOLATION_OBJECT, value=attr_value)
    attr_list.append(attr)
    
    return client.sai_thrift_create_isolation_group_member(attr_list)

def sai_thrift_remove_isolation_group_member(client, member_oid):                                      
    return client.sai_thrift_remove_isolation_group_member(member_oid)  
    
def sai_thrift_get_isolation_group_attributes(client, isolation_group_oid):  
    attr_list = client.sai_thrift_get_isolation_group_attributes(isolation_group_oid)
    return attr_list
    
def sai_thrift_get_isolation_group_member_attributes(client, member_oid):
    return client.sai_thrift_get_isolation_group_member_attributes(member_oid)