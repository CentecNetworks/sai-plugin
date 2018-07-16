/*sai include file*/
#include "sai.h"
#include "saitypes.h"
#include "saistatus.h"

/*ctc_sai include file*/
#include "ctc_sai.h"
#include "ctc_sai_oid.h"
#include "ctc_sai_db.h"
#include "ctc_sai_tam.h"

/*sdk include file*/
#include "ctcs_api.h"

typedef struct  ctc_sai_tam_s
{
    uint8 admin_state;
    uint8 reporting_mode;/*sai_tam_reporting_mode_t*/
    uint8 tracking_mode;/*sai_tam_tracking_mode_t*/
    uint8 clear_all_thresholds;
    sai_object_id_t latest_snapshot;
    sai_object_list_t stat_list;
}ctc_sai_tam_t;
typedef struct  ctc_sai_stat_s
{
    sai_object_id_t parent_id;
    uint32 counter_id;
}ctc_sai_stat_t;
typedef struct  ctc_sai_threshold_s
{
    sai_object_id_t tam_id;
    sai_object_id_t stat_id;
    uint64 level;
    uint8 snapshot_on_breach;
}ctc_sai_threshold_t;
typedef struct  ctc_sai_snapshot_s
{
    sai_object_id_t tam_id;
    sai_object_list_t stat_list;
}ctc_sai_snapshot_t;
typedef struct  ctc_sai_transporter_s
{

}ctc_sai_transporter_t;
typedef struct  ctc_sai_microburst_s
{
    sai_object_id_t tam_id;
    sai_object_id_t stat_id;
    uint64 level_a;
    uint64 level_b;
}ctc_sai_microburst_t;
typedef struct  ctc_sai_histogram_s
{
    sai_object_id_t tam_id;
    sai_object_list_t microburst;
    sai_u32_list_t boundary;
    uint8 clear_on_read;
}ctc_sai_histogram_t;


static sai_status_t
_ctc_sai_tam_build_db(uint8 lchip, sai_object_type_t type, sai_object_id_t oid, void** oid_property)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    void* p_info = NULL;
    uint32 size = 0;

    switch (type)
    {
    case SAI_OBJECT_TYPE_TAM:
        size = sizeof(ctc_sai_tam_t);
        break;
    case SAI_OBJECT_TYPE_TAM_STAT:
        size = sizeof(ctc_sai_stat_t);
        break;
    case SAI_OBJECT_TYPE_TAM_SNAPSHOT:
        size = sizeof(ctc_sai_snapshot_t);
        break;
    case SAI_OBJECT_TYPE_TAM_TRANSPORTER:
        size = sizeof(ctc_sai_transporter_t);
        break;
    case SAI_OBJECT_TYPE_TAM_THRESHOLD:
        size = sizeof(ctc_sai_threshold_t);
        break;
    case SAI_OBJECT_TYPE_TAM_HISTOGRAM:
        size = sizeof(ctc_sai_histogram_t);
        break;
    case SAI_OBJECT_TYPE_TAM_MICROBURST:
        size = sizeof(ctc_sai_microburst_t);
        break;
    default:
        return SAI_STATUS_INVALID_PARAMETER;
        break;
    }

    p_info = mem_malloc(MEM_MONITOR_MODULE, size);
    if (NULL == p_info)
    {
        CTC_SAI_LOG_ERROR(SAI_API_TAM, "no memory\n");
        return SAI_STATUS_NO_MEMORY;
    }

    sal_memset(p_info, 0, size);
    status = ctc_sai_db_add_object_property(lchip, oid, p_info);
    if (CTC_SAI_ERROR(status))
    {
        mem_free(p_info);
    }
    *oid_property = p_info;
    return status;
}

static sai_status_t
_ctc_sai_tam_remove_db(uint8 lchip, sai_object_id_t oid)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    void* p_info = NULL;

    CTC_SAI_LOG_ENTER(SAI_API_VIRTUAL_ROUTER);
    p_info = ctc_sai_db_get_object_property(lchip, oid);
    if (NULL == p_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }
    ctc_sai_db_remove_object_property(lchip, oid);
    mem_free(p_info);
    return status;
}

static sai_status_t
_ctc_sai_tam_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_tam_t* p_tam_info = NULL;
    void* p_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_tam_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_tam_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_ATTR_BUFFER_TRACKING_ADMIN_STATE:
        p_tam_info->admin_state = attr->value.booldata;
        break;
    case SAI_TAM_ATTR_BUFFER_REPORTING_MODE:
        p_tam_info->reporting_mode = attr->value.s32;
        break;
    case SAI_TAM_ATTR_BUFFER_TRACKING_MODE:
        p_tam_info->tracking_mode = attr->value.s32;
        break;
    case SAI_TAM_ATTR_TRACKING_OPTIONS:
        {
            sai_object_id_t *list = NULL;
            uint32_t count = attr->value.objlist.count;
            if (count)
            {
                uint32 i = 0;
                for (i = 0; i < count; i++)
                {
                    p_info = ctc_sai_db_get_object_property(lchip, attr->value.objlist.list[i]);
                    if (NULL == p_info)
                    {
                        return SAI_STATUS_ITEM_NOT_FOUND;
                    }
                }
                list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*count);
                if (NULL == list)
                {
                    return SAI_STATUS_NO_MEMORY;
                }
                sal_memcpy(list, attr->value.objlist.list, sizeof(sai_object_id_t)*count);
                if (p_tam_info->stat_list.count)
                {
                    mem_free(p_tam_info->stat_list.list);
                }
                p_tam_info->stat_list.count = count;
                p_tam_info->stat_list.list = list;
            }
        }
        break;
    case SAI_TAM_ATTR_TRANSPORTER:
        break;
    case SAI_TAM_ATTR_CLEAR_ALL_THRESHOLDS:
        p_tam_info->clear_all_thresholds = attr->value.booldata;
        break;
    case SAI_TAM_ATTR_TOTAL_NUM_STATISTICS:
    case SAI_TAM_ATTR_LATEST_SNAPSHOT_ID:
    case SAI_TAM_ATTR_MAX_NUM_SNAPSHOTS:
    case SAI_TAM_ATTR_THRESHOLD_LIST:
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_tam_t* p_tam_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_tam_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_tam_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_ATTR_BUFFER_TRACKING_ADMIN_STATE:
        attr->value.booldata = p_tam_info->admin_state;
        break;
    case SAI_TAM_ATTR_BUFFER_REPORTING_MODE:
        attr->value.s32 = p_tam_info->reporting_mode;
        break;
    case SAI_TAM_ATTR_BUFFER_TRACKING_MODE:
        attr->value.s32 = p_tam_info->tracking_mode;
        break;
    case SAI_TAM_ATTR_TRACKING_OPTIONS:
        CTC_SAI_ERROR_RETURN(ctc_sai_fill_object_list(sizeof(sai_object_id_t),
                  p_tam_info->stat_list.list, p_tam_info->stat_list.count, &attr->value.objlist));
        break;
    case SAI_TAM_ATTR_TRANSPORTER:
        break;
    case SAI_TAM_ATTR_CLEAR_ALL_THRESHOLDS:
        attr->value.booldata = p_tam_info->clear_all_thresholds;
        break;
    case SAI_TAM_ATTR_TOTAL_NUM_STATISTICS:
        break;
    case SAI_TAM_ATTR_LATEST_SNAPSHOT_ID:
        attr->value.oid = p_tam_info->latest_snapshot;
        break;
    case SAI_TAM_ATTR_MAX_NUM_SNAPSHOTS:
        break;
    case SAI_TAM_ATTR_THRESHOLD_LIST:
        break;
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_stat_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_stat_t* p_stat_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_stat_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_stat_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_STAT_ATTR_PARENT_ID:
        p_stat_info->parent_id = attr->value.oid;
        break;
    case SAI_TAM_STAT_ATTR_COUNTER_ID:
        p_stat_info->counter_id = attr->value.u32;
        break;
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_stat_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_stat_t* p_stat_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_stat_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_stat_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_STAT_ATTR_PARENT_ID:
        attr->value.oid = p_stat_info->parent_id;
        break;
    case SAI_TAM_STAT_ATTR_COUNTER_ID:
        attr->value.u32= p_stat_info->counter_id;
        break;
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_threshold_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_threshold_t* p_threshold_info = NULL;
    void* p_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_threshold_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_threshold_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_THRESHOLD_ATTR_TAM_ID:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_threshold_info->tam_id = attr->value.oid;
        break;
    case SAI_TAM_THRESHOLD_ATTR_STATISTIC:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_threshold_info->stat_id = attr->value.oid;
        break;
    case SAI_TAM_THRESHOLD_ATTR_LEVEL:
        p_threshold_info->level = attr->value.u64;
        break;
    case SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_ON_BREACH:
        p_threshold_info->snapshot_on_breach = attr->value.booldata;
        break;
    case SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_STATS:
        break;
    case SAI_TAM_THRESHOLD_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_threshold_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_threshold_t* p_threshold_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_threshold_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_threshold_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_THRESHOLD_ATTR_TAM_ID:
        attr->value.oid = p_threshold_info->tam_id;
        break;
    case SAI_TAM_THRESHOLD_ATTR_STATISTIC:
        attr->value.oid = p_threshold_info->stat_id;
        break;
    case SAI_TAM_THRESHOLD_ATTR_LEVEL:
        attr->value.u64 = p_threshold_info->level;
        break;
    case SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_ON_BREACH:
        attr->value.booldata = p_threshold_info->snapshot_on_breach;
        break;
    case SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_STATS:
        break;
     case SAI_TAM_THRESHOLD_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_snapshot_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_snapshot_t* p_snapshot_info = NULL;
    void* p_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_snapshot_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_snapshot_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_SNAPSHOT_ATTR_TAM_ID:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_snapshot_info->tam_id = attr->value.oid;
        break;
    case SAI_TAM_SNAPSHOT_ATTR_STAT_TYPE:
        {
            sai_object_id_t *list = NULL;
            uint32_t count = attr->value.objlist.count;
            if (count)
            {
                uint32 i = 0;
                for (i = 0; i < count; i++)
                {
                    p_info = ctc_sai_db_get_object_property(lchip, attr->value.objlist.list[i]);
                    if (NULL == p_info)
                    {
                        return SAI_STATUS_ITEM_NOT_FOUND;
                    }
                }
                list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*count);
                if (NULL == list)
                {
                    return SAI_STATUS_NO_MEMORY;
                }
                sal_memcpy(list, attr->value.objlist.list, sizeof(sai_object_id_t)*count);
                if (p_snapshot_info->stat_list.count)
                {
                    mem_free(p_snapshot_info->stat_list.list);
                }
                p_snapshot_info->stat_list.count = count;
                p_snapshot_info->stat_list.list = list;
            }
        }
        break;
    case SAI_TAM_SNAPSHOT_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_snapshot_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_snapshot_t* p_snapshot_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_snapshot_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_snapshot_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_SNAPSHOT_ATTR_TAM_ID:
        attr->value.oid = p_snapshot_info->tam_id;
        break;
    case SAI_TAM_SNAPSHOT_ATTR_STAT_TYPE:
        CTC_SAI_ERROR_RETURN(ctc_sai_fill_object_list(sizeof(sai_object_id_t),
                  p_snapshot_info->stat_list.list, p_snapshot_info->stat_list.count, &attr->value.objlist));
        break;
    case SAI_TAM_SNAPSHOT_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_transporter_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_transporter_t* p_transporter_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_transporter_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_transporter_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_TRANSPORTER_ATTR_TYPE:
        break;
    case SAI_TAM_TRANSPORTER_ATTR_MAX_SNAPSHOT_SIZE:
        break;
    case SAI_TAM_TRANSPORTER_ATTR_MONITOR_ID:
        break;
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_tam_transporter_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_transporter_t* p_transporter_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_transporter_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_transporter_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_TRANSPORTER_ATTR_TYPE:
        break;
    case SAI_TAM_TRANSPORTER_ATTR_MAX_SNAPSHOT_SIZE:
        break;
    case SAI_TAM_TRANSPORTER_ATTR_MONITOR_ID:
        break;
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_uburst_microburst_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_microburst_t* p_microburst_info = NULL;
    void* p_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_microburst_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_microburst_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_MICROBURST_ATTR_TAM_ID:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_microburst_info->tam_id = attr->value.oid;
        break;
    case SAI_TAM_MICROBURST_ATTR_STATISTIC:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_microburst_info->stat_id= attr->value.oid;
        break;
    case SAI_TAM_MICROBURST_ATTR_LEVEL_A:
        p_microburst_info->level_a = attr->value.u64;
        break;
    case SAI_TAM_MICROBURST_ATTR_LEVEL_B:
        p_microburst_info->level_a = attr->value.u64;
        break;
    case SAI_TAM_MICROBURST_ATTR_TRANSPORTER:
    case SAI_TAM_MICROBURST_ATTR_STATS:
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_uburst_microburst_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_microburst_t* p_microburst_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_microburst_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_microburst_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_MICROBURST_ATTR_TAM_ID:
        attr->value.oid = p_microburst_info->tam_id;
        break;
    case SAI_TAM_MICROBURST_ATTR_STATISTIC:
        attr->value.oid = p_microburst_info->stat_id;
        break;
    case SAI_TAM_MICROBURST_ATTR_LEVEL_A:
        attr->value.u64 = p_microburst_info->level_a;
        break;
    case SAI_TAM_MICROBURST_ATTR_LEVEL_B:
        attr->value.u64 = p_microburst_info->level_b;
        break;
    case SAI_TAM_MICROBURST_ATTR_TRANSPORTER:
    case SAI_TAM_MICROBURST_ATTR_STATS:
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_uburst_histogram_set_attr(sai_object_key_t* key, const sai_attribute_t* attr)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_histogram_t* p_histogram_info = NULL;
    void* p_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_histogram_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_histogram_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_HISTOGRAM_ATTR_TAM_ID:
        p_info = ctc_sai_db_get_object_property(lchip, attr->value.oid);
        if (NULL == p_info)
        {
            return SAI_STATUS_ITEM_NOT_FOUND;
        }
        p_histogram_info->tam_id = attr->value.oid;
        break;
    case SAI_TAM_HISTOGRAM_ATTR_STAT_TYPE:
        {
            sai_object_id_t *list = NULL;
            void* p_info = NULL;
            uint32 i = 0;
            uint32_t count = attr->value.objlist.count;
            if (count)
            {
                for(i = 0;i<count;i++)
                {
                    p_info = ctc_sai_db_get_object_property(lchip, attr->value.objlist.list[i]);
                    if (NULL == p_info)
                    {
                        return  SAI_STATUS_ITEM_NOT_FOUND;
                    }
                }
                list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*count);
                if (NULL == list)
                {
                    return SAI_STATUS_NO_MEMORY;
                }
                sal_memcpy(list, attr->value.objlist.list, sizeof(sai_object_id_t)*count);
                if (p_histogram_info->microburst.count)
                {
                    mem_free(p_histogram_info->microburst.list);
                }
                p_histogram_info->microburst.count = count;
                p_histogram_info->microburst.list = list;
            }
        }
        break;
    case SAI_TAM_HISTOGRAM_ATTR_BIN_BOUNDARY:
        {
            uint32_t *list = NULL;
            uint32_t count = attr->value.u32list.count;
            if (count)
            {
                list = mem_malloc(MEM_MONITOR_MODULE, sizeof(uint32_t)*count);
                if (NULL == list)
                {
                    return SAI_STATUS_NO_MEMORY;
                }
                sal_memcpy(list, attr->value.u32list.list, sizeof(uint32_t)*count);
                if (p_histogram_info->boundary.count)
                {
                    mem_free(p_histogram_info->boundary.list);
                }
                p_histogram_info->boundary.count = count;
                p_histogram_info->boundary.list = list;
            }
        }
        break;
    case SAI_TAM_HISTOGRAM_ATTR_CLEAR_MODE:
        p_histogram_info->clear_on_read= attr->value.booldata;
        break;
    case SAI_TAM_HISTOGRAM_ATTR_RESOLUTION:
    case SAI_TAM_HISTOGRAM_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_NOT_SUPPORTED;
        break;
    }
    return status;
}

static sai_status_t
_ctc_sai_uburst_histogram_get_attr(sai_object_key_t* key, sai_attribute_t* attr, uint32 attr_idx)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_sai_histogram_t* p_histogram_info = NULL;

    ctc_sai_oid_get_lchip(key->key.object_id, &lchip);
    p_histogram_info = ctc_sai_db_get_object_property(lchip, key->key.object_id);
    if (NULL == p_histogram_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    switch (attr->id)
    {
    case SAI_TAM_HISTOGRAM_ATTR_TAM_ID:
        attr->value.oid = p_histogram_info->tam_id;
        break;
    case SAI_TAM_HISTOGRAM_ATTR_STAT_TYPE:
        CTC_SAI_ERROR_RETURN(ctc_sai_fill_object_list(sizeof(sai_object_id_t),
                  p_histogram_info->microburst.list, p_histogram_info->microburst.count, &attr->value.objlist));
        break;
    case SAI_TAM_HISTOGRAM_ATTR_BIN_BOUNDARY:
        CTC_SAI_ERROR_RETURN(ctc_sai_fill_object_list(sizeof(uint32_t),
                  p_histogram_info->boundary.list, p_histogram_info->boundary.count, &attr->value.u32list));
        break;
    case SAI_TAM_HISTOGRAM_ATTR_CLEAR_MODE:
        attr->value.booldata= p_histogram_info->clear_on_read;
        break;
    case SAI_TAM_HISTOGRAM_ATTR_RESOLUTION:
    case SAI_TAM_HISTOGRAM_ATTR_TRANSPORTER:
    default:
        return SAI_STATUS_ATTR_NOT_SUPPORTED_0 + attr_idx;
        break;
    }
    return status;
}


static  ctc_sai_attr_fn_entry_t tam_attr_fn_entries[] = {
    {SAI_TAM_ATTR_BUFFER_TRACKING_ADMIN_STATE,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_BUFFER_REPORTING_MODE,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_BUFFER_TRACKING_MODE,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_TRACKING_OPTIONS,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_TRANSPORTER,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_CLEAR_ALL_THRESHOLDS,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_TOTAL_NUM_STATISTICS,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_LATEST_SNAPSHOT_ID,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_MAX_NUM_SNAPSHOTS,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {SAI_TAM_ATTR_THRESHOLD_LIST,
     _ctc_sai_tam_get_attr,
     _ctc_sai_tam_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t stat_attr_fn_entries[] = {
    {SAI_TAM_STAT_ATTR_PARENT_ID,
     _ctc_sai_tam_stat_get_attr,
     _ctc_sai_tam_stat_set_attr},
    {SAI_TAM_STAT_ATTR_COUNTER_ID,
     _ctc_sai_tam_stat_get_attr,
     _ctc_sai_tam_stat_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t threshold_attr_fn_entries[] = {
    {SAI_TAM_THRESHOLD_ATTR_TAM_ID,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {SAI_TAM_THRESHOLD_ATTR_STATISTIC,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {SAI_TAM_THRESHOLD_ATTR_LEVEL,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {SAI_TAM_THRESHOLD_ATTR_TRANSPORTER,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_ON_BREACH,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_STATS,
     _ctc_sai_tam_threshold_get_attr,
     _ctc_sai_tam_threshold_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t snapshot_attr_fn_entries[] = {
    {SAI_TAM_SNAPSHOT_ATTR_TAM_ID,
     _ctc_sai_tam_snapshot_get_attr,
     _ctc_sai_tam_snapshot_set_attr},
    {SAI_TAM_SNAPSHOT_ATTR_STAT_TYPE,
     _ctc_sai_tam_snapshot_get_attr,
     _ctc_sai_tam_snapshot_set_attr},
    {SAI_TAM_SNAPSHOT_ATTR_TRANSPORTER,
     _ctc_sai_tam_snapshot_get_attr,
     _ctc_sai_tam_snapshot_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t transporter_attr_fn_entries[] = {
    {SAI_TAM_TRANSPORTER_ATTR_TYPE,
     _ctc_sai_tam_transporter_get_attr,
     _ctc_sai_tam_transporter_set_attr},
    {SAI_TAM_TRANSPORTER_ATTR_MAX_SNAPSHOT_SIZE,
     _ctc_sai_tam_transporter_get_attr,
     _ctc_sai_tam_transporter_set_attr},
    {SAI_TAM_TRANSPORTER_ATTR_MONITOR_ID,
     _ctc_sai_tam_transporter_get_attr,
     _ctc_sai_tam_transporter_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t microburst_attr_fn_entries[] = {
    {SAI_TAM_MICROBURST_ATTR_TAM_ID,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {SAI_TAM_MICROBURST_ATTR_STATISTIC,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {SAI_TAM_MICROBURST_ATTR_LEVEL_A,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {SAI_TAM_MICROBURST_ATTR_LEVEL_B,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {SAI_TAM_MICROBURST_ATTR_TRANSPORTER,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {SAI_TAM_MICROBURST_ATTR_STATS,
     _ctc_sai_uburst_microburst_get_attr,
     _ctc_sai_uburst_microburst_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
static  ctc_sai_attr_fn_entry_t histogram_attr_fn_entries[] = {
    {SAI_TAM_HISTOGRAM_ATTR_TAM_ID,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {SAI_TAM_HISTOGRAM_ATTR_STAT_TYPE,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {SAI_TAM_HISTOGRAM_ATTR_BIN_BOUNDARY,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {SAI_TAM_HISTOGRAM_ATTR_RESOLUTION,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {SAI_TAM_HISTOGRAM_ATTR_CLEAR_MODE,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {SAI_TAM_HISTOGRAM_ATTR_TRANSPORTER,
     _ctc_sai_uburst_histogram_get_attr,
     _ctc_sai_uburst_histogram_set_attr},
    {CTC_SAI_FUNC_ATTR_END_ID,NULL,NULL}
};
#define ________INTERNAL_API________


#define ________SAI_API________
static sai_status_t
ctc_sai_tam_create_tam(sai_object_id_t *tam_id, sai_object_id_t switch_id, uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t tam_oid;
    ctc_sai_tam_t* p_tam_info = NULL;
    void* p_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    tam_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM, tam_oid, (void**)(&p_tam_info)), status, error1);
    /*set default value*/
    p_tam_info->admin_state = 1;
    p_tam_info->reporting_mode = SAI_TAM_REPORTING_MODE_BYTES;
    p_tam_info->tracking_mode = SAI_TAM_TRACKING_MODE_CURRENT;
    p_tam_info->clear_all_thresholds = 0;

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_ATTR_BUFFER_TRACKING_ADMIN_STATE, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_tam_info->admin_state = attr_value->booldata;
    }
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_ATTR_BUFFER_REPORTING_MODE, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_tam_info->reporting_mode = attr_value->s32;
    }
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_ATTR_BUFFER_TRACKING_MODE, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_tam_info->reporting_mode = attr_value->s32;
    }
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_ATTR_CLEAR_ALL_THRESHOLDS, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_tam_info->clear_all_thresholds = attr_value->booldata;
    }
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_ATTR_TRACKING_OPTIONS, &attr_value, &index));
    if ((!CTC_SAI_ERROR(status)) && attr_value->objlist.count)
    {
        uint32 i = 0;
        for (i = 0; i < attr_value->objlist.count; i++)
        {
            p_info = ctc_sai_db_get_object_property(lchip, attr_value->objlist.list[i]);
            if (NULL == p_info)
            {
                status =  SAI_STATUS_ITEM_NOT_FOUND;
                goto error2;
            }
        }
        p_tam_info->stat_list.count = attr_value->objlist.count;
        p_tam_info->stat_list.list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*p_tam_info->stat_list.count);
        if (NULL == p_tam_info->stat_list.list)
        {
            status = SAI_STATUS_NO_MEMORY;
            goto error2;
        }
        sal_memcpy(p_tam_info->stat_list.list, attr_value->objlist.list, sizeof(sai_object_id_t)*p_tam_info->stat_list.count);
    }
    *tam_id = tam_oid;
    goto out;
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, tam_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_remove_tam(sai_object_id_t tam_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_tam_t* p_tam_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_id, &ctc_object_id);

    p_tam_info = ctc_sai_db_get_object_property(lchip, tam_id);
    if (NULL == p_tam_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }
    if (p_tam_info->stat_list.count)
    {
        mem_free(p_tam_info->stat_list.list);
    }
    _ctc_sai_tam_remove_db(lchip, tam_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_set_tam_attribute(sai_object_id_t tam_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM,  tam_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_attribute(sai_object_id_t tam_id, uint32_t attr_count, sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM, loop, tam_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_create_tam_stat(sai_object_id_t *tam_stat_id, sai_object_id_t switch_id,
                                                                                    uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t stat_oid;
    ctc_sai_stat_t* p_stat_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_stat_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    stat_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_STAT, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_STAT, stat_oid, (void**)(&p_stat_info)), status, error1);

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_STAT_ATTR_PARENT_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_stat_info->parent_id = attr_value->oid;
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_STAT_ATTR_COUNTER_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_stat_info->counter_id = attr_value->u32;
    *tam_stat_id = stat_oid;
    goto out;
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, stat_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_remove_tam_stat(sai_object_id_t tam_stat_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_stat_t* p_stat_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_stat_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_stat_id, &ctc_object_id);
    p_stat_info = ctc_sai_db_get_object_property(lchip, tam_stat_id);
    if (NULL == p_stat_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    _ctc_sai_tam_remove_db(lchip, tam_stat_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_set_tam_stat_attribute(sai_object_id_t tam_stat_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_stat_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_stat_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_STAT,  stat_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_stat_attribute(sai_object_id_t tam_stat_id, uint32_t attr_count,
                                                                                                       sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_stat_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_stat_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_STAT, loop, stat_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}


static sai_status_t
ctc_sai_tam_create_tam_threshold(sai_object_id_t *tam_threshold_id, sai_object_id_t switch_id,
                                                                                                     uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t threshold_oid;
    ctc_sai_threshold_t* p_threshold_info = NULL;
    ctc_sai_tam_t* p_tam_info = NULL;
    ctc_sai_stat_t* p_stat_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_threshold_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    threshold_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_THRESHOLD, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_THRESHOLD, threshold_oid, (void**)(&p_threshold_info)), status, error1);
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_THRESHOLD_ATTR_TAM_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_tam_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_tam_info)
    {
        status = SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_threshold_info->tam_id = attr_value->oid;
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_THRESHOLD_ATTR_STATISTIC, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_stat_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_stat_info)
    {
        status = SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_threshold_info->stat_id = attr_value->oid;

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_THRESHOLD_ATTR_LEVEL, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_threshold_info->level = attr_value->u64;
    }

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_THRESHOLD_ATTR_SNAPSHOT_ON_BREACH, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_threshold_info->snapshot_on_breach= attr_value->booldata;
    }


    *tam_threshold_id = threshold_oid;
    goto out;
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, threshold_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_remove_tam_threshold(sai_object_id_t tam_threshold_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_threshold_t* p_threshold_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_threshold_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_threshold_id, &ctc_object_id);
    p_threshold_info = ctc_sai_db_get_object_property(lchip, tam_threshold_id);
    if (NULL == p_threshold_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    _ctc_sai_tam_remove_db(lchip, tam_threshold_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_set_tam_threshold_attribute(sai_object_id_t tam_threshold_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_threshold_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_threshold_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_THRESHOLD,  threshold_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_threshold_attribute(sai_object_id_t tam_threshold_id,
                                                                                                                        uint32_t attr_count, sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_threshold_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_threshold_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_THRESHOLD, loop, threshold_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_create_tam_snapshot(sai_object_id_t *tam_snapshot_id, sai_object_id_t switch_id,
                                                                                                    uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t snapshot_oid;
    ctc_sai_snapshot_t* p_snapshot_info = NULL;
    ctc_sai_tam_t* p_tam_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_snapshot_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    snapshot_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_SNAPSHOT, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_SNAPSHOT, snapshot_oid, (void**)(&p_snapshot_info)), status, error1);
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_SNAPSHOT_ATTR_TAM_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_tam_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_tam_info)
    {
        status = SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_tam_info->latest_snapshot = attr_value->oid;
    p_snapshot_info->tam_id = attr_value->oid;

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_SNAPSHOT_ATTR_STAT_TYPE, &attr_value, &index));
    if ((!CTC_SAI_ERROR(status)) && attr_value->objlist.count)
    {
        p_snapshot_info->stat_list.count = attr_value->objlist.count;
        p_snapshot_info->stat_list.list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*p_snapshot_info->stat_list.count);
        if (NULL == p_snapshot_info->stat_list.list)
        {
            status = SAI_STATUS_NO_MEMORY;
            goto error2;
        }
        sal_memcpy(p_snapshot_info->stat_list.list, attr_value->objlist.list, sizeof(sai_object_id_t)*p_snapshot_info->stat_list.count);
    }

    *tam_snapshot_id = snapshot_oid;
    goto out;
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, snapshot_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_remove_tam_snapshot(sai_object_id_t tam_snapshot_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_snapshot_t* p_snapshot_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_snapshot_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_snapshot_id, &ctc_object_id);
    p_snapshot_info = ctc_sai_db_get_object_property(lchip, tam_snapshot_id);
    if (NULL == p_snapshot_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    _ctc_sai_tam_remove_db(lchip, tam_snapshot_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_set_tam_snapshot_attribute(sai_object_id_t tam_snapshot_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_snapshot_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_snapshot_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_SNAPSHOT,  snapshot_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_snapshot_attribute(sai_object_id_t tam_snapshot_id,
                                                                                                                       uint32_t attr_count, sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_snapshot_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_snapshot_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_SNAPSHOT, loop, snapshot_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_snapshot_stats(sai_object_id_t tam_snapshot_id,
                                                                                                            uint32_t *number_of_counters, sai_tam_statistic_t *statistics)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    return status;
}

static sai_status_t
ctc_sai_tam_create_tam_transporter(sai_object_id_t *tam_transporter_id, sai_object_id_t switch_id,
                                                                                                         uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t transporter_oid;
    ctc_sai_threshold_t* p_transporter_info = NULL;
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_transporter_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    transporter_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_TRANSPORTER, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_TRANSPORTER, transporter_oid, (void**)(&p_transporter_info)), status, error1);

    *tam_transporter_id = transporter_oid;
    goto out;
error1:
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_remove_tam_transporter(sai_object_id_t tam_transporter_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_transporter_t* p_transporter_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_transporter_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_transporter_id, &ctc_object_id);
    p_transporter_info = ctc_sai_db_get_object_property(lchip, tam_transporter_id);
    if (NULL == p_transporter_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    _ctc_sai_tam_remove_db(lchip, tam_transporter_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_set_tam_transporter_attribute(sai_object_id_t tam_transporter_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_transporter_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_transporter_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_TRANSPORTER,  transporter_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_tam_get_tam_transporter_attribute(sai_object_id_t tam_transporter_id,
                                                                                                                            uint32_t attr_count, sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_transporter_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    key.key.object_id = tam_transporter_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_TRANSPORTER, loop, transporter_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}


static sai_status_t
ctc_sai_uburst_create_tam_microburst(sai_object_id_t *tam_microburst_id, sai_object_id_t switch_id,
                                                                                                                uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t microburst_oid;
    ctc_sai_microburst_t* p_microburst_info = NULL;
    void* p_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_microburst_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    microburst_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_MICROBURST, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_MICROBURST, microburst_oid, (void**)(&p_microburst_info)), status, error1);
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_MICROBURST_ATTR_TAM_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_info)
    {
        status =  SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_microburst_info->tam_id = attr_value->oid;
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_MICROBURST_ATTR_STATISTIC, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_info)
    {
        status = SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_microburst_info->stat_id = attr_value->oid;
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_MICROBURST_ATTR_LEVEL_A, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_microburst_info->level_a = attr_value->u64;
    }
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_MICROBURST_ATTR_LEVEL_B, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        p_microburst_info->level_b = attr_value->u64;
    }
    *tam_microburst_id = microburst_oid;
    goto out;
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, microburst_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_remove_tam_microburst(sai_object_id_t tam_microburst_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_microburst_t* p_microburst_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_microburst_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_microburst_id, &ctc_object_id);
    p_microburst_info = ctc_sai_db_get_object_property(lchip, tam_microburst_id);
    if (NULL == p_microburst_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }

    _ctc_sai_tam_remove_db(lchip, tam_microburst_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_set_tam_microburst_attribute(sai_object_id_t tam_microburst_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_microburst_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_UBURST);
    key.key.object_id = tam_microburst_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_MICROBURST,  microburst_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_get_tam_microburst_attribute(sai_object_id_t tam_microburst_id, uint32_t attr_count,
                                                                                                                                    sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_microburst_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_UBURST);
    key.key.object_id = tam_microburst_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_MICROBURST, loop, microburst_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}


static sai_status_t
ctc_sai_uburst_create_tam_histogram(sai_object_id_t *tam_histogram_id, sai_object_id_t switch_id,
                                                                                                               uint32_t attr_count, const sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint32 id = 0;
    sai_object_id_t histogram_oid;
    ctc_sai_histogram_t* p_histogram_info = NULL;
    void* p_info = NULL;
    const sai_attribute_value_t *attr_value;
    uint32_t index = 0;

    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    CTC_SAI_PTR_VALID_CHECK(tam_histogram_id);
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(switch_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_MICROBURST_ATTR_STATS, &attr_value, &index));
    if (!CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_ATTR_NOT_SUPPORTED_0 + index;
        goto out;
    }

    CTC_SAI_ERROR_GOTO(ctc_sai_db_alloc_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, &id), status, out);
    histogram_oid = ctc_sai_create_object_id(SAI_OBJECT_TYPE_TAM_HISTOGRAM, lchip, 0, 0, id);
    CTC_SAI_ERROR_GOTO(_ctc_sai_tam_build_db(lchip, SAI_OBJECT_TYPE_TAM_HISTOGRAM, histogram_oid, (void**)(&p_histogram_info)), status, error1);
    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_HISTOGRAM_ATTR_TAM_ID, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    p_info = ctc_sai_db_get_object_property(lchip, attr_value->oid);
    if (NULL == p_info)
    {
        status =  SAI_STATUS_ITEM_NOT_FOUND;
        goto error2;
    }
    p_histogram_info->tam_id = attr_value->oid;

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_HISTOGRAM_ATTR_BIN_BOUNDARY, &attr_value, &index));
    if (CTC_SAI_ERROR(status))
    {
        status =  SAI_STATUS_MANDATORY_ATTRIBUTE_MISSING;
        goto error2;
    }
    if(attr_value->u32list.count)
    {
        p_histogram_info->boundary.count = attr_value->u32list.count;
        p_histogram_info->boundary.list = mem_malloc(MEM_MONITOR_MODULE, sizeof(uint32)*p_histogram_info->boundary.count);
        if (NULL == p_histogram_info->boundary.list)
        {
            status = SAI_STATUS_NO_MEMORY;
            goto error2;
        }
        sal_memcpy(p_histogram_info->boundary.list, attr_value->u32list.list, sizeof(uint32)*p_histogram_info->boundary.count);
    }

    status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_HISTOGRAM_ATTR_STAT_TYPE, &attr_value, &index));
    if ((!CTC_SAI_ERROR(status))&&attr_value->u32list.count)
    {
        uint32 i = 0;
        for (i = 0; i < attr_value->u32list.count; i++)
        {
            p_info = ctc_sai_db_get_object_property(lchip, attr_value->u32list.list[i]);
            if (NULL == p_info)
            {
                status =  SAI_STATUS_ITEM_NOT_FOUND;
                goto error3;
            }
        }

        p_histogram_info->microburst.count = attr_value->u32list.count;
        p_histogram_info->microburst.list = mem_malloc(MEM_MONITOR_MODULE, sizeof(sai_object_id_t)*p_histogram_info->microburst.count);
        if (NULL == p_histogram_info->microburst.list)
        {
            status = SAI_STATUS_NO_MEMORY;
            goto error3;
        }
        sal_memcpy(p_histogram_info->microburst.list, attr_value->u32list.list, sizeof(sai_object_id_t)*p_histogram_info->microburst.count);
    }

     status = (ctc_sai_find_attrib_in_list(attr_count, attr_list, SAI_TAM_HISTOGRAM_ATTR_CLEAR_MODE, &attr_value, &index));
     if (!CTC_SAI_ERROR(status))
     {
         p_histogram_info->clear_on_read = attr_value->booldata;
     }
    *tam_histogram_id = histogram_oid;
    goto out;
error3:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error3\n");
    if(p_histogram_info->boundary.count)
    {
        mem_free(p_histogram_info->boundary.list);
    }
error2:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error2\n");
    _ctc_sai_tam_remove_db(lchip, histogram_oid);
error1:
    CTC_SAI_LOG_ERROR(SAI_OBJECT_TYPE_TAM, "rollback to error1\n");
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, id);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_remove_tam_histogram(sai_object_id_t tam_histogram_id)
{
    uint8 lchip = 0;
    sai_status_t           status = SAI_STATUS_SUCCESS;
    ctc_object_id_t ctc_object_id;
    ctc_sai_histogram_t* p_histogram_info = NULL;
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_histogram_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_TAM);
    ctc_sai_get_ctc_object_id(SAI_OBJECT_TYPE_TAM, tam_histogram_id, &ctc_object_id);
    p_histogram_info = ctc_sai_db_get_object_property(lchip, tam_histogram_id);
    if (NULL == p_histogram_info)
    {
        return SAI_STATUS_ITEM_NOT_FOUND;
    }
    if (p_histogram_info->boundary.count)
    {
        mem_free(p_histogram_info->boundary.list);
    }
    if (p_histogram_info->microburst.count)
    {
        mem_free(p_histogram_info->microburst.list);
    }
    _ctc_sai_tam_remove_db(lchip, tam_histogram_id);
    ctc_sai_db_free_id(lchip, CTC_SAI_DB_ID_TYPE_COMMON, ctc_object_id.value);

    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_set_tam_histogram_attribute(sai_object_id_t tam_histogram_id, const sai_attribute_t *attr)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_histogram_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_UBURST);
    key.key.object_id = tam_histogram_id;
    CTC_SAI_ERROR_GOTO(ctc_sai_set_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_HISTOGRAM,  histogram_attr_fn_entries, attr), status, out);
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_get_tam_histogram_attribute(sai_object_id_t tam_histogram_id, uint32_t attr_count,
                                                                                                                                  sai_attribute_t *attr_list)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    uint8 lchip = 0;
    uint8          loop = 0;
    sai_object_key_t key;
    sal_memset(&key, 0, sizeof(key));
    CTC_SAI_ERROR_RETURN(ctc_sai_oid_get_lchip(tam_histogram_id, &lchip));
    CTC_SAI_DB_LOCK(lchip);
    CTC_SAI_LOG_ENTER(SAI_API_UBURST);
    key.key.object_id = tam_histogram_id;
    while(loop < attr_count)
    {
        CTC_SAI_ERROR_GOTO(ctc_sai_get_attribute(&key, NULL, SAI_OBJECT_TYPE_TAM_HISTOGRAM, loop, histogram_attr_fn_entries, &attr_list[loop]), status, out);
        loop++;
    }
out:
    CTC_SAI_DB_UNLOCK(lchip);
    return status;
}

static sai_status_t
ctc_sai_uburst_get_tam_histogram_stats(sai_object_id_t tam_histogram_id, uint32_t *number_of_counters,
                                                                                                                       uint64_t *counters)
{
    sai_status_t           status = SAI_STATUS_SUCCESS;
    return status;
}


const sai_tam_api_t ctc_sai_tam_api = {
    ctc_sai_tam_create_tam,
    ctc_sai_tam_remove_tam,
    ctc_sai_tam_set_tam_attribute,
    ctc_sai_tam_get_tam_attribute,
    ctc_sai_tam_create_tam_stat,
    ctc_sai_tam_remove_tam_stat,
    ctc_sai_tam_set_tam_stat_attribute,
    ctc_sai_tam_get_tam_stat_attribute,
    ctc_sai_tam_create_tam_threshold,
    ctc_sai_tam_remove_tam_threshold,
    ctc_sai_tam_set_tam_threshold_attribute,
    ctc_sai_tam_get_tam_threshold_attribute,
    ctc_sai_tam_create_tam_snapshot,
    ctc_sai_tam_remove_tam_snapshot,
    ctc_sai_tam_set_tam_snapshot_attribute,
    ctc_sai_tam_get_tam_snapshot_attribute,
    ctc_sai_tam_get_tam_snapshot_stats,
    ctc_sai_tam_create_tam_transporter,
    ctc_sai_tam_remove_tam_transporter,
    ctc_sai_tam_set_tam_transporter_attribute,
    ctc_sai_tam_get_tam_transporter_attribute
};

const sai_uburst_api_t ctc_sai_uburst_api = {
    ctc_sai_uburst_create_tam_microburst,
    ctc_sai_uburst_remove_tam_microburst,
    ctc_sai_uburst_set_tam_microburst_attribute,
    ctc_sai_uburst_get_tam_microburst_attribute,
    ctc_sai_uburst_create_tam_histogram,
    ctc_sai_uburst_remove_tam_histogram,
    ctc_sai_uburst_set_tam_histogram_attribute,
    ctc_sai_uburst_get_tam_histogram_attribute,
    ctc_sai_uburst_get_tam_histogram_stats,
};

sai_status_t
ctc_sai_tam_api_init()
{
    ctc_sai_register_module_api(SAI_API_TAM, (void*)&ctc_sai_tam_api);
    ctc_sai_register_module_api(SAI_API_UBURST, (void*)&ctc_sai_uburst_api);

    return SAI_STATUS_SUCCESS;
}

sai_status_t
ctc_sai_tam_db_init(uint8 lchip)
{
    ctc_sai_db_wb_t wb_info;
    sal_memset(&wb_info, 0, sizeof(wb_info));
    wb_info.version = SYS_WB_VERSION_TAM;
    wb_info.wb_sync_cb = NULL;
    wb_info.wb_reload_cb = NULL;
    wb_info.wb_reload_cb1 = NULL;
    wb_info.data_len = sizeof(ctc_sai_tam_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_stat_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_STAT, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_snapshot_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_SNAPSHOT, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_transporter_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_TRANSPORTER, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_threshold_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_THRESHOLD, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_histogram_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_HISTOGRAM, (void*)(&wb_info));
    wb_info.data_len = sizeof(ctc_sai_microburst_t);
    ctc_sai_warmboot_register_cb(lchip, CTC_SAI_WB_TYPE_OID, SAI_OBJECT_TYPE_TAM_MICROBURST, (void*)(&wb_info));
    return SAI_STATUS_SUCCESS;
}

