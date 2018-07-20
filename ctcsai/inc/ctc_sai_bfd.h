/**
 @file ctc_sai_bfd.h

 @author  Copyright (C) 2018 Centec Networks Inc.  All rights reserved.

 @date 2018-06-21

 @version v2.0

\p
 This module defines SAI Bfd.
\b
\p
 The BFD Module APIs supported by centec devices:
\p
\b
\t  |   API                                                     |   SUPPORT CHIPS LIST   |
\t  |  create_bfd_session                                       |           -            |
\t  |  remove_bfd_session                                       |           -            |
\t  |  set_bfd_session_attribute                                |           -            |
\t  |  get_bfd_session_attribute                                |           -            |
\t  |  get_bfd_session_stats                                    |           -            |
\t  |  get_bfd_session_stats_ext                                |           -            |
\t  |  clear_bfd_session_stats                                  |           -            |
\b
\p
 The BFD Session attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                               |   SUPPORT CHIPS LIST   |
\t  |  SAI_BFD_SESSION_ATTR_TYPE                                |           -            |
\t  |  SAI_BFD_SESSION_ATTR_HW_LOOKUP_VALID                     |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VIRTUAL_ROUTER                      |           -            |
\t  |  SAI_BFD_SESSION_ATTR_PORT                                |           -            |
\t  |  SAI_BFD_SESSION_ATTR_LOCAL_DISCRIMINATOR                 |           -            |
\t  |  SAI_BFD_SESSION_ATTR_REMOTE_DISCRIMINATOR                |           -            |
\t  |  SAI_BFD_SESSION_ATTR_UDP_SRC_PORT                        |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TC                                  |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VLAN_TPID                           |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VLAN_ID                             |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VLAN_PRI                            |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VLAN_CFI                            |           -            |
\t  |  SAI_BFD_SESSION_ATTR_VLAN_HEADER_VALID                   |           -            |
\t  |  SAI_BFD_SESSION_ATTR_BFD_ENCAPSULATION_TYPE              |           -            |
\t  |  SAI_BFD_SESSION_ATTR_IPHDR_VERSION                       |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TOS                                 |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TTL                                 |           -            |
\t  |  SAI_BFD_SESSION_ATTR_SRC_IP_ADDRESS                      |           -            |
\t  |  SAI_BFD_SESSION_ATTR_DST_IP_ADDRESS                      |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TUNNEL_TOS                          |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TUNNEL_TTL                          |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TUNNEL_SRC_IP_ADDRESS               |           -            |
\t  |  SAI_BFD_SESSION_ATTR_TUNNEL_DST_IP_ADDRESS               |           -            |
\t  |  SAI_BFD_SESSION_ATTR_ECHO_ENABLE                         |           -            |
\t  |  SAI_BFD_SESSION_ATTR_MULTIHOP                            |           -            |
\t  |  SAI_BFD_SESSION_ATTR_CBIT                                |           -            |
\t  |  SAI_BFD_SESSION_ATTR_MIN_TX                              |           -            |
\t  |  SAI_BFD_SESSION_ATTR_MIN_RX                              |           -            |
\t  |  SAI_BFD_SESSION_ATTR_MULTIPLIER                          |           -            |
\t  |  SAI_BFD_SESSION_ATTR_REMOTE_MIN_TX                       |           -            |
\t  |  SAI_BFD_SESSION_ATTR_REMOTE_MIN_RX                       |           -            |
\t  |  SAI_BFD_SESSION_ATTR_STATE                               |           -            |
\b
*/

#ifndef _CTC_SAI_BFD_H
#define _CTC_SAI_BFD_H


#include "ctc_sai.h"
#include "sal.h"
#include "ctcs_api.h"
/*don't need include other header files*/


extern sai_status_t
ctc_sai_bfd_api_init();

extern sai_status_t
ctc_sai_bfd_db_init(uint8 lchip);

#endif /*_CTC_SAI_BFD_H*/

