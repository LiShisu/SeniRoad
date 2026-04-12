# MySQL数据库的ER模型（实体关系图）和关系模式（建表语句）。

### 1. ER模型设计 (实体与关系)

为了直观展示，我将核心实体和它们的关系梳理如下：

- **User (用户)**: 区分老年用户和家属用户。
- **Device (设备)**: 关联老年用户，用于实时位置上报。
- **Location (位置)**: 存储实时位置和历史轨迹。
- **FavoritePlace (常用地点)**: 包括家属预设和老人自动识别的地点。
- **NavigationRecord (导航记录)**: 存储历史出行记录。
- **Binding (绑定关系)**: 维护老人与家属的多对多关系。

**实体关系图（文本描述）：**

- **User** 1 --- \* **Device** (一个用户可有多台设备，但通常是一对一)
- **User** 1 --- \* **Location** (一个用户产生多个位置点)
- **User** 1 --- \* **NavigationRecord** (一个用户有多次导航记录)
- **User** 1 --- \* **FavoritePlace** (用户拥有常用地点)
- **User** (Elder) --- **Binding** --- **User** (Family) (多对多绑定关系)

***

### 2. 关系模式与MySQL建表语句

以下是具体的建表SQL语句，包含了注释说明，符合MySQL 5.7+规范。

```sql
-- 1. 用户表 (Users)
-- 存储老年用户和家属用户的基础信息
CREATE TABLE `users` (
  `user_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名/手机号',
  `nickname` VARCHAR(100) COMMENT '昵称',
  `avatar_url` VARCHAR(255) COMMENT '头像URL',
  `user_type` TINYINT NOT NULL DEFAULT 1 COMMENT '用户类型: 1-老年人, 2-家属',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (`username`),
  INDEX idx_type (`user_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 设备表 (Devices)
-- 关联老年用户，用于接收实时位置
CREATE TABLE `devices` (
  `device_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '设备ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '关联的用户ID(老人)',
  `device_token` VARCHAR(255) NOT NULL COMMENT '设备唯一标识/Token',
  `device_model` VARCHAR(100) COMMENT '设备型号',
  `last_login_time` DATETIME COMMENT '最后登录时间',
  `status` TINYINT DEFAULT 1 COMMENT '状态: 1-在线, 0-离线',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_token` (`device_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 3. 位置轨迹表 (Locations)
-- 存储实时位置和历史轨迹
CREATE TABLE `locations` (
  `location_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '定位对象(老人ID)',
  `latitude` DECIMAL(10, 8) NOT NULL COMMENT '纬度',
  `longitude` DECIMAL(11, 8) NOT NULL COMMENT '经度',
  `accuracy` FLOAT COMMENT '精度(米)',
  `address` VARCHAR(500) COMMENT '详细地址',
  `location_type` TINYINT DEFAULT 1 COMMENT '类型: 1-实时, 2-轨迹点',
  `upload_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上报时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  INDEX idx_user_time (`user_id`, `upload_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='位置信息表';

-- 4. 常用地点表 (Favorite_Places)
-- 存储家属预设和老人自动识别的常用地点
CREATE TABLE `favorite_places` (
  `place_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属老人ID',
  `place_name` VARCHAR(100) NOT NULL COMMENT '地点名称(如: 儿子家)',
  `latitude` DECIMAL(10, 8) NOT NULL,
  `longitude` DECIMAL(11, 8) NOT NULL,
  `address` VARCHAR(500) NOT NULL,
  `source_type` TINYINT DEFAULT 1 COMMENT '来源: 1-家属预设, 2-自动识别',
  `is_active` TINYINT DEFAULT 1,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  INDEX idx_user_source (`user_id`, `source_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='常用地点表';

-- 5. 绑定关系表 (Bindings)
-- 实现老人与家属的多对多关系
CREATE TABLE `bindings` (
  `binding_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `elder_id` BIGINT UNSIGNED NOT NULL COMMENT '老人用户ID',
  `family_id` BIGINT UNSIGNED NOT NULL COMMENT '家属用户ID',
  `relation` VARCHAR(20) COMMENT '关系(如: 儿子, 女儿)',
  `status` TINYINT DEFAULT 1 COMMENT '绑定状态',
  `bind_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`elder_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`family_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_elder_family` (`elder_id`, `family_id`) -- 防止重复绑定
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户绑定关系表';

-- 6. 导航记录表 (Navigation_Records)
-- 存储历史出行记录，用于家属查看
CREATE TABLE `navigation_records` (
  `record_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `start_time` DATETIME NOT NULL COMMENT '导航开始时间',
  `end_time` DATETIME COMMENT '结束时间',
  `origin_lat` DECIMAL(10, 8) COMMENT '起点纬度',
  `origin_lng` DECIMAL(11, 8) COMMENT '起点经度',
  `dest_lat` DECIMAL(10, 8) NOT NULL COMMENT '终点纬度',
  `dest_lng` DECIMAL(11, 8) NOT NULL COMMENT '终点经度',
  `dest_name` VARCHAR(100) COMMENT '目的地名称',
  `status` TINYINT DEFAULT 1 COMMENT '状态: 1-进行中, 2-完成, 3-取消',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  INDEX idx_user_start (`user_id`, `start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='导航历史记录表';

-- 7. 语音交互日志表 (Voice_Logs)
-- 记录语音输入和AI解析结果，用于异常分析
CREATE TABLE `voice_logs` (
  `log_id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `device_id` BIGINT UNSIGNED,
  `audio_url` VARCHAR(255) COMMENT '语音文件存储路径',
  `asr_text` TEXT COMMENT '语音识别转文本',
  `intent_json` TEXT COMMENT 'AI解析的意图结构化数据',
  `response_text` TEXT COMMENT '系统回复文本',
  `log_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='语音交互日志表';
```

### 3. 设计思路解析

根据《需求分析说明书》，我的设计重点考虑了以下几点：

1. **核心分离：** 将**User**表作为核心，通过 `user_type` 字段区分老人和家属。这样设计便于统一管理登录和权限，也方便通过**Binding**表建立关联。
2. **实时位置处理：** 需求中提到“实时位置推送”和“历史轨迹”。因此，**Location**表设计了 `location_type` 字段。家属查询时，可以只查最新的（实时），也可以查时间段内的（轨迹）。
3. **常用地点同步：** 需求中提到“家属预设”和“自动识别”。在**Favorite\_Places**表中，我增加了 `source_type` 字段，以便在老年端展示时，可以区分哪些是子女设置的，哪些是自己常去的。
4. **语音交互支持：** 针对“语音交互发起导航”和“AI语义解析”需求，设计了**Voice\_Logs**表。这不仅记录了原始语音，还预留了 `intent_json` 字段来存储大模型（Qwen/豆包）解析出的结构化意图（如：目的地、意图类型），这对后续分析老人意图非常关键。
5. **导航记录：** **Navigation\_Records** 表记录了完整的出行过程，满足家属端“查看历史出行记录”的需求。

### 4. 建议的索引策略

为了保证查询效率，特别是针对老年人端的低延迟要求，建议在以下字段建立索引：

- `locations` 表的 `(user_id, upload_time)`：快速查询某老人的历史轨迹。
- `bindings` 表的 `(elder_id, family_id)`：快速验证家属与老人的绑定关系。
- `favorite_places` 表的 `user_id`：快速加载老人的常用地点列表。

