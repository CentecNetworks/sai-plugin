/**
 @file ctc_sai_bridge.h

 @author  Copyright (C) 2018 Centec Networks Inc.  All rights reserved.

 @date 2017-11-09

 @version v2.0

\p
 This module defines SAI Bridge.
\b
\p
 The Bridge Module APIs supported by centec devices:
\p
\b
\t  |   API                                        |   SUPPORT CHIPS LIST   |
\t  |  create_bridge                               |    CTC8096,CTC7148     |
\t  |  remove_bridge                               |    CTC8096,CTC7148     |
\t  |  set_bridge_attribute                        |    CTC8096,CTC7148     |
\t  |  get_bridge_attribute                        |    CTC8096,CTC7148     |
\t  |  get_bridge_stats                            |           -            |
\t  |  get_bridge_stats_ext                        |           -            |
\t  |  clear_bridge_stats                          |           -            |
\t  |  create_bridge_port                          |    CTC8096,CTC7148     |
\t  |  remove_bridge_port                          |    CTC8096,CTC7148     |
\t  |  set_bridge_port_attribute                   |    CTC8096,CTC7148     |
\t  |  get_bridge_port_attribute                   |    CTC8096,CTC7148     |
\t  |  get_bridge_port_stats                       |    CTC8096,CTC7148     |
\t  |  get_bridge_port_stats_ext                   |    CTC8096,CTC7148     |
\t  |  clear_bridge_port_stats                     |           -            |
\b
\p
 The Bridge attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_BRIDGE_ATTR_TYPE                                 |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_PORT_LIST                            |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_MAX_LEARNED_ADDRESSES                |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_LEARN_DISABLE                        |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_UNKNOWN_UNICAST_FLOOD_CONTROL_TYPE   |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_UNKNOWN_UNICAST_FLOOD_GROUP          |           -            |
\t  |  SAI_BRIDGE_ATTR_UNKNOWN_MULTICAST_FLOOD_CONTROL_TYPE |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_UNKNOWN_MULTICAST_FLOOD_GROUP        |           -            |
\t  |  SAI_BRIDGE_ATTR_BROADCAST_FLOOD_CONTROL_TYPE         |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_ATTR_BROADCAST_FLOOD_GROUP                |           -            |
\b
\p
 The Bridge port attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                                       |   SUPPORT CHIPS LIST   |
\t  |  SAI_BRIDGE_PORT_ATTR_TYPE                                        |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_PORT_ID                                     |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_TAGGING_MODE                                |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_VLAN_ID                                     |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_RIF_ID                                      |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_TUNNEL_ID                                   |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_BRIDGE_ID                                   |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_FDB_LEARNING_MODE                           |           -            |
\t  |  SAI_BRIDGE_PORT_ATTR_MAX_LEARNED_ADDRESSES                       |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_FDB_LEARNING_LIMIT_VIOLATION_PACKET_ACTION  |           -            |
\t  |  SAI_BRIDGE_PORT_ATTR_ADMIN_STATE                                 |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_INGRESS_FILTERING                           |    CTC8096,CTC7148     |
\t  |  SAI_BRIDGE_PORT_ATTR_EGRESS_FILTERING                            |    CTC8096,CTC7148     |
\b
*/

#ifndef _CTC_SAI_BRIDGE_H
#define _CTC_SAI_BRIDGE_H

#include "ctc_sai.h"

#include "sal.h"
#include "ctcs_api.h"

/*don't need include other header files*/

typedef struct ctc_sai_bridge_port_s
{
    uint8         port_type;
    bool          admin_state;
    uint8         tag_mode;
    uint8         rsv;
    uint16        gport;
    uint16        vlan_id;
    uint16        bridge_id;
    uint16        l3if_id;
    uint16        logic_port;
    uint32        nh_id;
    uint32        limit_num;
    uint32        limit_action;
    sai_object_id_t  tunnel_id;
}
ctc_sai_bridge_port_t;


extern sai_status_t
ctc_sai_bridge_api_init();

extern sai_status_t
ctc_sai_bridge_db_init(uint8 lchip);

extern sai_status_t
ctc_sai_bridge_get_fid(sai_object_id_t bv_id, uint16 *fid);

extern sai_status_t
ctc_sai_bridge_get_bridge_port_oid(uint8 lchip, uint32 gport, uint8 is_logic, sai_object_id_t* bridge_port_id);

extern sai_status_t
ctc_sai_bridge_traverse_get_bridge_port_info(uint8 lchip, uint16 bridge_id, uint16 logic_port, uint32* gport, uint16* vlan_id);

extern void
ctc_sai_bridge_dump(uint8 lchip, sal_file_t p_file, ctc_sai_dump_grep_param_t *dump_grep_param);

#endif  /*_CTC_SAI_BRIDGE_H*/

