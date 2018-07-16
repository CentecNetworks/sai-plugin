
/**
 @file ctc_sai_stp.h

  @author  Copyright (C) 2018 Centec Networks Inc.  All rights reserved.

 @date 2018-02-1

 @version v2.0

\p
This module defines SAI STP.
\b
\p
 The STP Module APIs supported by centec devices:
\p
\b
\t  |   API                                                 |   SUPPORT CHIPS LIST   |
\t  |  create_stp                                           |    CTC8096,CTC7148     |
\t  |  remove_stp                                           |    CTC8096,CTC7148     |
\t  |  set_stp_attribute                                    |    CTC8096,CTC7148     |
\t  |  get_stp_attribute                                    |    CTC8096,CTC7148     |
\t  |  create_stp_port                                      |    CTC8096,CTC7148     |
\t  |  remove_stp_port                                      |    CTC8096,CTC7148     |
\t  |  sai_set_stp_port_attribute                           |    CTC8096,CTC7148     |
\t  |  sai_get_stp_port_attribute                           |    CTC8096,CTC7148     |
\t  |  create_stp_ports                                     |    CTC8096,CTC7148     |
\t  |  remove_stp_ports                                     |    CTC8096,CTC7148     |
\b

\p
 The STP attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_STP_ATTR_VLAN_LIST                               |    CTC8096,CTC7148     |
\t  |  SAI_STP_ATTR_BRIDGE_ID                               |    CTC8096,CTC7148     |
\t  |  SAI_STP_ATTR_PORT_LIST                               |    CTC8096,CTC7148     |
\b

\p
 The STP PORT attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_STP_PORT_ATTR_STP                                |    CTC8096,CTC7148     |
\t  |  SAI_STP_PORT_ATTR_BRIDGE_PORT                        |    CTC8096,CTC7148     |
\t  |  SAI_STP_PORT_ATTR_STATE                              |    CTC8096,CTC7148     |
\b

*/

#ifndef _CTC_SAI_STP_H
#define _CTC_SAI_STP_H


#include "ctc_sai.h"
#include "sal.h"
#include "ctcs_api.h"
/*don't need include other header files*/

extern sai_status_t
ctc_sai_stp_api_init();
extern sai_status_t
ctc_sai_stp_deinit();
extern sai_status_t
ctc_sai_stp_db_init(uint8 lchip);
extern sai_status_t
ctc_sai_stp_set_instance(uint8 lchip, uint16 vlan_ptr, sai_object_id_t stp_oid, uint8 is_add);
extern void
ctc_sai_stp_dump(uint8 lchip, sal_file_t p_file, ctc_sai_dump_grep_param_t *dump_grep_param);
#endif
