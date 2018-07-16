/**
 @file ctc_sai_tam.h

 @author  Copyright (C) 2018 Centec Networks Inc.  All rights reserved.

 @date 2018-04-28

 @version v2.0

\p
 This module defines SAI TAM and Uburst.
\b
\p
 The TAM Module APIs supported by centec devices:
\p
\b
\t  |   API                                                 |   SUPPORT CHIPS LIST   |
\t  |  create_tam                                           |           -            |
\t  |  remove_tam                                           |           -            |
\t  |  set_tam_attribute                                    |           -            |
\t  |  get_tam_attribute                                    |           -            |
\t  |  create_tam_stat                                      |           -            |
\t  |  remove_tam_stat                                      |           -            |
\t  |  set_tam_stat_attribute                               |           -            |
\t  |  get_tam_stat_attribute                               |           -            |
\t  |  create_tam_threshold                                 |           -            |
\t  |  remove_tam_threshold                                 |           -            |
\t  |  set_tam_threshold_attribute                          |           -            |
\t  |  get_tam_threshold_attribute                          |           -            |
\t  |  create_tam_snapshot                                  |           -            |
\t  |  remove_tam_snapshot                                  |           -            |
\t  |  set_tam_snapshot_attribute                           |           -            |
\t  |  get_tam_snapshot_attribute                           |           -            |
\t  |  get_tam_snapshot_stats                               |           -            |
\t  |  create_tam_transporter                               |           -            |
\t  |  remove_tam_transporter                               |           -            |
\t  |  set_tam_transporter_attribute                        |           -            |
\t  |  get_tam_transporter_attribute                        |           -            |
\b
\p
 The TAM Stat attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_STAT_ATTR_PARENT_ID                          |           -            |
\t  |  SAI_TAM_STAT_ATTR_COUNTER_ID                         |           -            |
\b
\p
 The TAM attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_ATTR_BUFFER_TRACKING_ADMIN_STATE             |           -            |
\t  |  SAI_TAM_ATTR_BUFFER_REPORTING_MODE                   |           -            |
\t  |  SAI_TAM_ATTR_BUFFER_TRACKING_MODE                    |           -            |
\t  |  SAI_TAM_ATTR_TRACKING_OPTIONS                        |           -            |
\t  |  SAI_TAM_ATTR_TRANSPORTER                             |           -            |
\t  |  SAI_TAM_ATTR_CLEAR_ALL_THRESHOLDS                    |           -            |
\t  |  SAI_TAM_ATTR_TOTAL_NUM_STATISTICS                    |           -            |
\t  |  SAI_TAM_ATTR_LATEST_SNAPSHOT_ID                      |           -            |
\t  |  SAI_TAM_ATTR_MAX_NUM_SNAPSHOTS                       |           -            |
\t  |  SAI_TAM_ATTR_THRESHOLD_LIST                          |           -            |
\b
\p
 The TAM Threshold attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_THRESHOLD_ATTR_TAM_ID                        |           -            |
\t  |  SAI_TAM_THRESHOLD_ATTR_STATISTIC                     |           -            |
\t  |  SAI_TAM_THRESHOLD_ATTR_LEVEL                         |           -            |
\t  |  SAI_TAM_THRESHOLD_ATTR_TRANSPORTER                   |           -            |
\t  |  SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_ON_BREACH            |           -            |
\t  |  SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_STATS                |           -            |
\b
\p
 The TAM Snapshot attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_SNAPSHOT_ATTR_TAM_ID                         |           -            |
\t  |  SAI_TAM_SNAPSHOT_ATTR_STAT_TYPE                      |           -            |
\t  |  SAI_TAM_SNAPSHOT_ATTR_TRANSPORTER                    |           -            |
\b
\p
 The TAM Transporter attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_TRANSPORTER_ATTR_TYPE                        |           -            |
\t  |  SAI_TAM_TRANSPORTER_ATTR_MAX_SNAPSHOT_SIZE           |           -            |
\t  |  SAI_TAM_TRANSPORTER_ATTR_MONITOR_ID                  |           -            |
\b
\p
 The UBURST Module APIs supported by centec devices:
\p
\b
\t  |   API                                                 |   SUPPORT CHIPS LIST   |
\t  |  sai_create_tam_microburst_fn                         |           -            |
\t  |  sai_remove_tam_microburst_fn                         |           -            |
\t  |  sai_set_tam_microburst_attribute_fn                  |           -            |
\t  |  sai_get_tam_microburst_attribute_fn                  |           -            |
\t  |  sai_create_tam_histogram_fn                          |           -            |
\t  |  sai_remove_tam_histogram_fn                          |           -            |
\t  |  sai_set_tam_histogram_attribute_fn                   |           -            |
\t  |  sai_get_tam_histogram_attribute_fn                   |           -            |
\t  |  sai_get_tam_histogram_stats_fn                       |           -            |
\b
\p
 The TAM Microburst attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_MICROBURST_ATTR_TAM_ID                       |           -            |
\t  |  SAI_TAM_MICROBURST_ATTR_STATISTIC                    |           -            |
\t  |  SAI_TAM_MICROBURST_ATTR_LEVEL_A                      |           -            |
\t  |  SAI_TAM_MICROBURST_ATTR_LEVEL_B                      |           -            |
\t  |  SAI_TAM_MICROBURST_ATTR_TRANSPORTER                  |           -            |
\t  |  SAI_TAM_MICROBURST_ATTR_STATS                        |           -            |
\b
\p
 The TAM Histogram attributes supported by centec devices:
\p
\b
\t  |   ATTRIBUTE                                           |   SUPPORT CHIPS LIST   |
\t  |  SAI_TAM_HISTOGRAM_ATTR_TAM_ID                        |           -            |
\t  |  SAI_TAM_HISTOGRAM_ATTR_STAT_TYPE                     |           -            |
\t  |  SAI_TAM_HISTOGRAM_ATTR_BIN_BOUNDARY                  |           -            |
\t  |  SAI_TAM_HISTOGRAM_ATTR_RESOLUTION                    |           -            |
\t  |  SAI_TAM_HISTOGRAM_ATTR_CLEAR_MODE                    |           -            |
\t  |  SAI_TAM_HISTOGRAM_ATTR_TRANSPORTER                   |           -            |
\b
*/

#ifndef _CTC_SAI_TAM_H
#define _CTC_SAI_TAM_H


#include "ctc_sai.h"
#include "sal.h"
#include "ctcs_api.h"
/*don't need include other header files*/


extern sai_status_t
ctc_sai_tam_api_init();

extern sai_status_t
ctc_sai_tam_db_init(uint8 lchip);

#endif /*_CTC_SAI_TAM_H*/

