# 数据库视图设计文档

> 文档生成时间: 2026-04-21
> 项目路径: `d:\learning_materials\AAmyPrograms\SeniRoad\yilu_an_backend`

## 目录

- [1. 视图设计概述](#1-视图设计概述)
- [2. 视图详细设计](#2-视图详细设计)
  - [2.1 老人家属绑定关系视图 (v_elderly_family_binding)](#21-老人家属绑定关系视图-v_elderly_family_binding)
  - [2.2 老人位置信息视图 (v_elderly_location)](#22-老人位置信息视图-v_elderly_location)
  - [2.3 老人常用地点视图 (v_elderly_favorite_places)](#23-老人常用地点视图-v_elderly_favorite_places)
  - [2.4 导航记录统计视图 (v_navigation_stats)](#24-导航记录统计视图-v_navigation_stats)
  - [2.5 语音交互日志视图 (v_voice_interaction_logs)](#25-语音交互日志视图-v_voice_interaction_logs)
- [3. 视图使用建议](#3-视图使用建议)
- [4. 性能优化考虑](#4-性能优化考虑)

## 1. 视图设计概述

根据数据库架构文件，我们设计了5个核心视图，涵盖了系统的主要业务场景：

| 视图名称 | 功能描述 | 主要表 | 业务价值 |
|---------|---------|--------|----------|
| v_elderly_family_binding | 老人与家属的绑定关系 | users, bindings | 快速查询老人与家属的关联关系 |
| v_elderly_location | 老人最新位置信息 | users, locations | 实时获取老人位置信息 |
| v_elderly_favorite_places | 老人常用地点 | users, favorite_places | 管理老人的常用地点 |
| v_navigation_stats | 导航记录统计 | users, navigation_records | 分析导航使用情况 |
| v_voice_interaction_logs | 语音交互日志 | users, voice_logs | 查看用户与系统的语音交互 |

## 2. 视图详细设计

### 2.1 老人家属绑定关系视图 (v_elderly_family_binding)

**设计说明**：
- 显示老人与家属之间的绑定关系
- 包含双方用户信息和绑定状态
- 便于家属管理和老人监护

**SQL 语句**：

```sql
CREATE VIEW v_elderly_family_binding AS
SELECT 
    b.binding_id,
    e.user_id AS elderly_id,
    e.nickname AS elderly_name,
    e.phone AS elderly_phone,
    f.user_id AS family_id,
    f.nickname AS family_name,
    f.phone AS family_phone,
    b.status,
    b.created_at,
    b.approved_at
FROM 
    bindings b
JOIN 
    users e ON b.elderly_id = e.user_id
JOIN 
    users f ON b.family_id = f.user_id
WHERE 
    e.role = 'elderly'
    AND f.role = 'family';
```

**字段说明**：
| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| binding_id | Integer | 绑定ID |
| elderly_id | Integer | 老人ID |
| elderly_name | String | 老人昵称 |
| elderly_phone | String | 老人手机号 |
| family_id | Integer | 家属ID |
| family_name | String | 家属昵称 |
| family_phone | String | 家属手机号 |
| status | Enum | 绑定状态 |
| created_at | DateTime | 创建时间 |
| approved_at | DateTime | 审批时间 |

### 2.2 老人位置信息视图 (v_elderly_location)

**设计说明**：
- 显示老人的最新位置信息
- 包含位置坐标、地址和精度
- 便于家属实时查看老人位置

**SQL 语句**：

```sql
CREATE VIEW v_elderly_location AS
SELECT 
    u.user_id,
    u.nickname,
    u.phone,
    l.location_id,
    l.latitude,
    l.longitude,
    l.address,
    l.accuracy,
    l.created_at AS location_time
FROM 
    users u
JOIN 
    locations l ON u.user_id = l.user_id
JOIN (
    SELECT 
        user_id,
        MAX(created_at) AS max_time
    FROM 
        locations
    GROUP BY 
        user_id
) latest ON l.user_id = latest.user_id AND l.created_at = latest.max_time
WHERE 
    u.role = 'elderly';
```

**字段说明**：
| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| user_id | Integer | 老人ID |
| nickname | String | 老人昵称 |
| phone | String | 老人手机号 |
| location_id | Integer | 位置记录ID |
| latitude | Float | 纬度 |
| longitude | Float | 经度 |
| address | String | 地址 |
| accuracy | Float | 精度(米) |
| location_time | DateTime | 位置时间 |

### 2.3 老人常用地点视图 (v_elderly_favorite_places)

**设计说明**：
- 显示老人的常用地点
- 包含地点名称、坐标和地址
- 区分地点来源（家属预设/自动识别）

**SQL 语句**：

```sql
CREATE VIEW v_elderly_favorite_places AS
SELECT 
    u.user_id,
    u.nickname,
    fp.place_id,
    fp.place_name,
    fp.latitude,
    fp.longitude,
    fp.address,
    CASE 
        WHEN fp.source_type = 1 THEN '家属预设'
        WHEN fp.source_type = 2 THEN '自动识别'
        ELSE '未知'
    END AS source_type_desc,
    CASE 
        WHEN fp.is_active = 1 THEN '激活'
        ELSE '未激活'
    END AS status
FROM 
    users u
JOIN 
    favorite_places fp ON u.user_id = fp.user_id
WHERE 
    u.role = 'elderly'
    AND fp.is_active = 1
ORDER BY 
    fp.source_type, fp.place_name;
```

**字段说明**：
| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| user_id | Integer | 老人ID |
| nickname | String | 老人昵称 |
| place_id | BigInteger | 地点ID |
| place_name | String | 地点名称 |
| latitude | Numeric | 纬度 |
| longitude | Numeric | 经度 |
| address | String | 详细地址 |
| source_type_desc | String | 来源类型描述 |
| status | String | 状态 |

### 2.4 导航记录统计视图 (v_navigation_stats)

**设计说明**：
- 统计老人的导航记录
- 包含导航次数、成功率等统计信息
- 按月份和目的地分组

**SQL 语句**：

```sql
CREATE VIEW v_navigation_stats AS
SELECT 
    u.user_id,
    u.nickname,
    strftime('%Y-%m', nr.start_time) AS month,
    nr.dest_name,
    COUNT(*) AS total_navigations,
    SUM(CASE WHEN nr.status = 2 THEN 1 ELSE 0 END) AS completed_navigations,
    ROUND(SUM(CASE WHEN nr.status = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate,
    AVG(julianday(nr.end_time) - julianday(nr.start_time)) * 24 * 60 AS avg_duration_minutes
FROM 
    users u
JOIN 
    navigation_records nr ON u.user_id = nr.user_id
WHERE 
    u.role = 'elderly'
GROUP BY 
    u.user_id, u.nickname, strftime('%Y-%m', nr.start_time), nr.dest_name
ORDER BY 
    u.user_id, month DESC, total_navigations DESC;
```

**字段说明**：
| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| user_id | Integer | 老人ID |
| nickname | String | 老人昵称 |
| month | String | 月份(YYYY-MM) |
| dest_name | String | 目的地名称 |
| total_navigations | Integer | 总导航次数 |
| completed_navigations | Integer | 完成导航次数 |
| success_rate | Numeric | 成功率(%) |
| avg_duration_minutes | Numeric | 平均导航时长(分钟) |

### 2.5 语音交互日志视图 (v_voice_interaction_logs)

**设计说明**：
- 显示用户与系统的语音交互记录
- 包含语音识别文本和系统回复
- 便于分析用户需求和系统响应

**SQL 语句**：

```sql
CREATE VIEW v_voice_interaction_logs AS
SELECT 
    u.user_id,
    u.nickname,
    u.role,
    vl.log_id,
    vl.audio_url,
    vl.asr_text,
    vl.intent_json,
    vl.response_text,
    vl.log_time,
    vl.created_at
FROM 
    users u
JOIN 
    voice_logs vl ON u.user_id = vl.user_id
ORDER BY 
    vl.log_time DESC;
```

**字段说明**：
| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| user_id | Integer | 用户ID |
| nickname | String | 用户昵称 |
| role | Enum | 用户角色 |
| log_id | BigInteger | 日志ID |
| audio_url | String | 语音文件路径 |
| asr_text | Text | 语音识别文本 |
| intent_json | Text | 意图结构化数据 |
| response_text | Text | 系统回复文本 |
| log_time | DateTime | 日志时间 |
| created_at | DateTime | 创建时间 |

## 3. 视图使用建议

1. **老人家属绑定关系视图**
   - 用于家属管理页面，显示所有绑定关系
   - 可按状态筛选，如只查看待审批的绑定请求

2. **老人位置信息视图**
   - 用于老人定位页面，实时显示老人位置
   - 可结合地图API显示位置标记

3. **老人常用地点视图**
   - 用于老人常用地点管理页面
   - 可用于快速导航功能，显示推荐地点

4. **导航记录统计视图**
   - 用于数据分析页面，显示导航使用情况
   - 可用于优化导航路线和目的地推荐

5. **语音交互日志视图**
   - 用于系统分析和用户行为分析
   - 可用于优化语音识别和系统响应

## 4. 性能优化考虑

1. **索引优化**
   - 确保关联字段（如user_id）有适当的索引
   - 对于频繁查询的字段，考虑添加复合索引

2. **视图刷新策略**
   - 对于实时性要求高的视图（如位置信息），考虑使用物化视图
   - 对于统计类视图，可考虑定期刷新

3. **查询优化**
   - 避免在视图上进行复杂的聚合操作
   - 使用适当的WHERE条件限制结果集大小

4. **数据量控制**
   - 对于历史数据，考虑分区或归档策略
   - 对于日志类数据，设置合理的保留期限

5. **缓存策略**
   - 对于频繁访问的视图，考虑使用缓存机制
   - 合理设置缓存过期时间

## 总结

本视图设计基于现有的数据库架构，涵盖了系统的主要业务场景，提供了便捷的数据查询和分析能力。通过这些视图，开发人员可以更高效地实现业务逻辑，同时为用户提供更好的功能体验。

视图设计遵循了以下原则：
- 命名规范清晰，便于理解和使用
- 字段选择合理，满足业务需求
- 表连接方式优化，确保查询效率
- 必要的过滤条件，提高数据质量

这些视图可以根据实际业务需求进行调整和扩展，以适应系统的发展和变化。