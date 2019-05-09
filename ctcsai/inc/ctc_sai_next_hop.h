/**
 @file ctc_sai_next_hop.h

  @author  Copyright (C) 2018 Centec Networks Inc.  All rights reserved.

 @date 2018-02-1

 @version v2.0

   This file contains all sai vlan data structure, enum, macro and proto.

\p
This module defines SAI Next Hop.
\b
\p
 The Next Hop Module APIs supported by centec devices:
\p
\b
\t  |   API                                       |       SUPPORT CHIPS LIST       |
\t  |  create_next_hop                            |    CTC8096,CTC7148,CTC7132     |
\t  |  remove_next_hop                            |    CTC8096,CTC7148,CTC7132     |
\t  |  set_next_hop_attribute                     |    CTC8096,CTC7148,CTC7132     |
\t  |  get_next_hop_attribute                     |    CTC8096,CTC7148,CTC7132     |
\b
\p
 The Next Hop attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                        |       SUPPORT CHIPS LIST       |
\t  |  SAI_NEXT_HOP_ATTR_TYPE                            |    CTC8096,CTC7148,CTC7132     |
\t  |  SAI_NEXT_HOP_ATTR_IP                              |    CTC8096,CTC7148,CTC7132     |
\t  |  SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID             |    CTC8096,CTC7148,CTC7132     |
\t  |  SAI_NEXT_HOP_ATTR_TUNNEL_ID                       |    CTC8096,CTC7148,CTC7132     |
\t  |  SAI_NEXT_HOP_ATTR_SEGMENTROUTE_SIDLIST_ID         |              -                 |
\t  |  SAI_NEXT_HOP_ATTR_SEGMENTROUTE_ENDPOINT_TYPE      |              -                 |
\t  |  SAI_NEXT_HOP_ATTR_SEGMENTROUTE_ENDPOINT_POP_TYPE  |              -                 |
\t  |  SAI_NEXT_HOP_ATTR_LABELSTACK                      |    CTC8096,CTC7148,CTC7132     |
\b

*/

#ifndef _CTC_SAI_NEXT_HOP_H
#define _CTC_SAI_NEXT_HOP_H


#include "ctc_sai.h"
#include "sal.h"
#include "ctcs_api.h"
/*don't need include other header files*/

typedef struct  ctc_sai_next_hop_s
{
    sai_object_id_t rif_id;
    sai_ip_address_t ip_address;
    sai_u32_list_t label;
    sai_object_id_t tunnel_id;
    uint16 ctc_mpls_tunnel_id;
}ctc_sai_next_hop_t;


extern sai_status_t
ctc_sai_next_hop_api_init();

extern sai_status_t
ctc_sai_next_hop_db_init(uint8 lchip);

extern sai_status_t
ctc_sai_next_hop_get_arp_id(sai_object_id_t next_hop_id, uint16* ctc_arp_id);

extern sai_status_t
ctc_sai_next_hop_update_by_neighbor(sai_object_id_t next_hop_id, sai_object_id_t rif_id, sai_ip_address_t ip_address);

extern sai_status_t
ctc_sai_next_hop_get_tunnel_nh(sai_object_id_t tunnel_id, const sai_ip_address_t* ip_addr, uint32* tunnel_nh_id);

extern void
ctc_sai_next_hop_dump(uint8 lchip, sal_file_t p_file, ctc_sai_dump_grep_param_t *dump_grep_param);

#endif /*_CTC_SAI_NEXT_HOP_H*/

