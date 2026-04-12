# 颐路安导航系统 API 文档

## 1. 认证相关接口

### 1.1 用户注册
- **接口路径**: `/api/v1/auth/register`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | phone | string | 是 | 手机号（11-20位） |
  | password | string | 是 | 密码（至少6位） |
  | nickname | string | 否 | 昵称 |
  | role | string | 否 | 角色（elderly或family，默认elderly） |
  | avatar_url | string | 否 | 头像URL |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 用户ID |
  | phone | string | 手机号 |
  | nickname | string | 昵称 |
  | role | string | 角色 |
  | avatar_url | string | 头像URL |
  | is_active | boolean | 是否激活 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 400: 请求参数错误
- **示例请求**:
  ```json
  POST /api/v1/auth/register
  {
    "phone": "13800138000",
    "password": "123456",
    "nickname": "测试用户",
    "role": "elderly"
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "phone": "13800138000",
    "nickname": "测试用户",
    "role": "elderly",
    "avatar_url": null,
    "is_active": true,
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 1.2 用户登录
- **接口路径**: `/api/v1/auth/login`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | username | string | 是 | 手机号 |
  | password | string | 是 | 密码 |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | access_token | string | 访问令牌 |
  | token_type | string | 令牌类型（bearer） |
- **错误码说明**:
  - 401: 手机号或密码错误
- **示例请求**:
  ```json
  POST /api/v1/auth/login
  {
    "username": "13800138000",
    "password": "123456"
  }
  ```
- **示例响应**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

## 2. 用户相关接口

### 2.1 获取当前用户信息
- **接口路径**: `/api/v1/users/profile`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 用户ID |
  | phone | string | 手机号 |
  | nickname | string | 昵称 |
  | role | string | 角色 |
  | avatar_url | string | 头像URL |
  | is_active | boolean | 是否激活 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/users/profile
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "phone": "13800138000",
    "nickname": "测试用户",
    "role": "elderly",
    "avatar_url": null,
    "is_active": true,
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 2.2 更新用户信息
- **接口路径**: `/api/v1/users/profile`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | nickname | string | 否 | 昵称 |
  | avatar_url | string | 否 | 头像URL |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 用户ID |
  | phone | string | 手机号 |
  | nickname | string | 昵称 |
  | role | string | 角色 |
  | avatar_url | string | 头像URL |
  | is_active | boolean | 是否激活 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```json
  PUT /api/v1/users/profile
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "nickname": "更新后的昵称",
    "avatar_url": "https://example.com/avatar.jpg"
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "phone": "13800138000",
    "nickname": "更新后的昵称",
    "role": "elderly",
    "avatar_url": "https://example.com/avatar.jpg",
    "is_active": true,
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 2.3 获取用户的绑定关系
- **接口路径**: `/api/v1/users/bindings`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | elderly_bindings | array | 作为老人的绑定关系 |
  | family_bindings | array | 作为家属的绑定关系 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/users/bindings
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "elderly_bindings": [
      {
        "id": 2,
        "phone": "13900139000",
        "nickname": "家属用户"
      }
    ],
    "family_bindings": []
  }
  ```

## 3. 绑定相关接口

### 3.1 创建绑定关系
- **接口路径**: `/api/v1/bindings/`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | elderly_id | integer | 是 | 老人用户ID |
  | family_id | integer | 是 | 家属用户ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 绑定ID |
  | elderly_id | integer | 老人用户ID |
  | family_id | integer | 家属用户ID |
  | status | string | 绑定状态 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 400: 绑定关系已存在
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/bindings/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "elderly_id": 1,
    "family_id": 2
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "elderly_id": 1,
    "family_id": 2,
    "status": "pending",
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 3.2 获取绑定关系列表
- **接口路径**: `/api/v1/bindings/`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**: 绑定关系列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/bindings/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "elderly_id": 1,
      "family_id": 2,
      "status": "pending",
      "created_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 3.3 解除绑定关系
- **接口路径**: `/api/v1/bindings/unbind`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | elderly_id | integer | 是 | 老人用户ID |
  | family_id | integer | 是 | 家属用户ID |
- **响应数据结构**: 无（204 No Content）
- **错误码说明**:
  - 404: 绑定关系不存在
  - 403: 无权解除此绑定关系
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/bindings/unbind
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "elderly_id": 1,
    "family_id": 2
  }
  ```

### 3.4 批准绑定请求
- **接口路径**: `/api/v1/bindings/{binding_id}/approve`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | binding_id | integer | 是 | 绑定ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 绑定ID |
  | elderly_id | integer | 老人用户ID |
  | family_id | integer | 家属用户ID |
  | status | string | 绑定状态（accepted） |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 404: 绑定关系不存在
  - 403: 只有老人可以批准绑定请求
  - 401: 未授权
- **示例请求**:
  ```
  PUT /api/v1/bindings/1/approve
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "elderly_id": 1,
    "family_id": 2,
    "status": "accepted",
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 3.5 拒绝绑定请求
- **接口路径**: `/api/v1/bindings/{binding_id}/reject`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | binding_id | integer | 是 | 绑定ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 绑定ID |
  | elderly_id | integer | 老人用户ID |
  | family_id | integer | 家属用户ID |
  | status | string | 绑定状态（rejected） |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 404: 绑定关系不存在
  - 403: 只有老人可以拒绝绑定请求
  - 401: 未授权
- **示例请求**:
  ```
  PUT /api/v1/bindings/1/reject
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "elderly_id": 1,
    "family_id": 2,
    "status": "rejected",
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

## 4. 位置相关接口

### 4.1 更新实时位置
- **接口路径**: `/api/v1/locations/update`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | latitude | float | 是 | 纬度（-90到90之间） |
  | longitude | float | 是 | 经度（-180到180之间） |
  | address | string | 否 | 地址 |
  | accuracy | float | 否 | 精度 |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 位置记录ID |
  | user_id | integer | 用户ID |
  | latitude | float | 纬度 |
  | longitude | float | 经度 |
  | address | string | 地址 |
  | accuracy | float | 精度 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/locations/update
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "latitude": 39.90923,
    "longitude": 116.397428,
    "address": "北京市东城区",
    "accuracy": 10.0
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "latitude": 39.90923,
    "longitude": 116.397428,
    "address": "北京市东城区",
    "accuracy": 10.0,
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 4.2 查询历史轨迹
- **接口路径**: `/api/v1/locations/history`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | start_time | datetime | 否 | 开始时间 |
  | end_time | datetime | 否 | 结束时间 |
  | limit | integer | 否 | 返回记录数量限制（默认100） |
- **响应数据结构**: 位置记录列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/locations/history?start_time=2026-04-01T00:00:00&end_time=2026-04-12T23:59:59&limit=50
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "latitude": 39.90923,
      "longitude": 116.397428,
      "address": "北京市东城区",
      "accuracy": 10.0,
      "created_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 4.3 获取最新位置
- **接口路径**: `/api/v1/locations/latest`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 位置记录ID |
  | user_id | integer | 用户ID |
  | latitude | float | 纬度 |
  | longitude | float | 经度 |
  | address | string | 地址 |
  | accuracy | float | 精度 |
  | created_at | datetime | 创建时间 |
- **错误码说明**:
  - 404: 位置记录不存在
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/locations/latest
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "latitude": 39.90923,
    "longitude": 116.397428,
    "address": "北京市东城区",
    "accuracy": 10.0,
    "created_at": "2026-04-12T14:25:50.518828"
  }
  ```

## 5. 目的地相关接口

### 5.1 获取目的地列表
- **接口路径**: `/api/v1/destinations/`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**: 目的地列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/destinations/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 5.2 创建目的地
- **接口路径**: `/api/v1/destinations/`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | name | string | 是 | 目的地名称 |
  | address | string | 是 | 地址 |
  | latitude | float | 否 | 纬度 |
  | longitude | float | 否 | 经度 |
  | is_common | boolean | 否 | 是否常用 |
- **响应数据结构**: 目的地信息
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/destinations/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "name": "家",
    "address": "北京市东城区",
    "latitude": 39.90923,
    "longitude": 116.397428,
    "is_common": true
  }
  ```

## 6. 导航相关接口

### 6.1 规划导航路线
- **接口路径**: `/api/v1/navigation/plan`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | origin | string | 是 | 起点坐标，格式为"经度,纬度" |
  | destination | string | 是 | 终点坐标，格式为"经度,纬度"或目的地名称 |
  | priority | string | 否 | 优先级，可选值为"elderly_friendly"（默认）、"time"、"distance" |
- **响应数据结构**: 导航路线数据
- **错误码说明**:
  - 400: 起点和终点不能为空
  - 500: 规划路线失败
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/navigation/plan
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "origin": "116.397428,39.90923",
    "destination": "116.407428,39.91923",
    "priority": "elderly_friendly"
  }
  ```

### 6.2 获取常用地点列表
- **接口路径**: `/api/v1/navigation/common-destinations`
- **请求方法**: GET
- **请求参数**: 无（需要Authorization头）
- **响应数据结构**: 目的地列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/navigation/common-destinations
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "name": "家",
      "address": "北京市东城区",
      "latitude": 39.90923,
      "longitude": 116.397428,
      "is_common": true,
      "created_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

## 7. 设备相关接口

### 7.1 创建设备
- **接口路径**: `/api/v1/devices/`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | device_token | string | 是 | 设备唯一标识 |
  | device_model | string | 否 | 设备型号 |
  | status | integer | 否 | 设备状态（0-离线，1-在线） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | device_id | integer | 设备ID |
  | user_id | integer | 用户ID |
  | device_token | string | 设备唯一标识 |
  | device_model | string | 设备型号 |
  | status | integer | 设备状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 400: 请求参数错误
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/devices/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "test_model",
    "status": 1
  }
  ```
- **示例响应**:
  ```json
  {
    "device_id": 1,
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "test_model",
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 7.2 获取设备列表
- **接口路径**: `/api/v1/devices/`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 否 | 用户ID |
- **响应数据结构**: 设备列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/devices/?user_id=1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "device_id": 1,
      "user_id": 1,
      "device_token": "test_token_123",
      "device_model": "test_model",
      "status": 1,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 7.3 根据ID获取设备
- **接口路径**: `/api/v1/devices/{device_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_id | integer | 是 | 设备ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | device_id | integer | 设备ID |
  | user_id | integer | 用户ID |
  | device_token | string | 设备唯一标识 |
  | device_model | string | 设备型号 |
  | status | integer | 设备状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 设备不存在
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/devices/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "device_id": 1,
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "test_model",
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 7.4 根据设备token获取设备
- **接口路径**: `/api/v1/devices/token/{device_token}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_token | string | 是 | 设备唯一标识 |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | device_id | integer | 设备ID |
  | user_id | integer | 用户ID |
  | device_token | string | 设备唯一标识 |
  | device_model | string | 设备型号 |
  | status | integer | 设备状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 设备不存在
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/devices/token/test_token_123
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "device_id": 1,
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "test_model",
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 7.5 更新设备
- **接口路径**: `/api/v1/devices/{device_id}`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_id | integer | 是 | 设备ID |
  | device_model | string | 否 | 设备型号 |
  | status | integer | 否 | 设备状态（0-离线，1-在线） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | device_id | integer | 设备ID |
  | user_id | integer | 用户ID |
  | device_token | string | 设备唯一标识 |
  | device_model | string | 设备型号 |
  | status | integer | 设备状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 设备不存在
  - 401: 未授权
- **示例请求**:
  ```json
  PUT /api/v1/devices/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "device_model": "updated_model",
    "status": 0
  }
  ```
- **示例响应**:
  ```json
  {
    "device_id": 1,
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "updated_model",
    "status": 0,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 7.6 删除设备
- **接口路径**: `/api/v1/devices/{device_id}`
- **请求方法**: DELETE
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_id | integer | 是 | 设备ID |
- **响应数据结构**: 无（204 No Content）
- **错误码说明**:
  - 404: 设备不存在
  - 401: 未授权
- **示例请求**:
  ```
  DELETE /api/v1/devices/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 7.7 更新设备状态
- **接口路径**: `/api/v1/devices/{device_id}/status/{status}`
- **请求方法**: PATCH
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_id | integer | 是 | 设备ID |
  | status | integer | 是 | 设备状态（0-离线，1-在线） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | device_id | integer | 设备ID |
  | user_id | integer | 用户ID |
  | device_token | string | 设备唯一标识 |
  | device_model | string | 设备型号 |
  | status | integer | 设备状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 400: 状态值必须为0（离线）或1（在线）
  - 404: 设备不存在
  - 401: 未授权
- **示例请求**:
  ```
  PATCH /api/v1/devices/1/status/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "device_id": 1,
    "user_id": 1,
    "device_token": "test_token_123",
    "device_model": "test_model",
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

## 8. 导航记录相关接口

### 8.1 创建导航记录
- **接口路径**: `/api/v1/navigation-records/`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | device_id | integer | 是 | 设备ID |
  | start_location | string | 是 | 起始位置 |
  | end_location | string | 是 | 终点位置 |
  | start_time | datetime | 是 | 开始时间 |
  | status | integer | 是 | 状态（1-进行中, 2-完成, 3-取消） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 导航记录ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | start_location | string | 起始位置 |
  | end_location | string | 终点位置 |
  | start_time | datetime | 开始时间 |
  | end_time | datetime | 结束时间 |
  | status | integer | 状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/navigation-records/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "status": 1
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "end_time": null,
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 8.2 获取导航记录列表
- **接口路径**: `/api/v1/navigation-records/`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | status | integer | 否 | 状态（1-进行中, 2-完成, 3-取消） |
- **响应数据结构**: 导航记录列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/navigation-records/?user_id=1&status=2
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "start_location": "116.397428,39.90923",
      "end_location": "116.407428,39.91923",
      "start_time": "2026-04-12T14:25:50.518828",
      "end_time": "2026-04-12T14:35:50.518828",
      "status": 2,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:35:50.518828"
    }
  ]
  ```

### 8.3 获取用户的进行中导航记录
- **接口路径**: `/api/v1/navigation-records/user/{user_id}/active`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
- **响应数据结构**: 导航记录列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/navigation-records/user/1/active
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "start_location": "116.397428,39.90923",
      "end_location": "116.407428,39.91923",
      "start_time": "2026-04-12T14:25:50.518828",
      "end_time": null,
      "status": 1,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 8.4 获取用户的已完成导航记录
- **接口路径**: `/api/v1/navigation-records/user/{user_id}/completed`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | start_date | datetime | 否 | 开始日期 |
  | end_date | datetime | 否 | 结束日期 |
- **响应数据结构**: 导航记录列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/navigation-records/user/1/completed?start_date=2026-04-01T00:00:00&end_date=2026-04-12T23:59:59
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "start_location": "116.397428,39.90923",
      "end_location": "116.407428,39.91923",
      "start_time": "2026-04-12T14:25:50.518828",
      "end_time": "2026-04-12T14:35:50.518828",
      "status": 2,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:35:50.518828"
    }
  ]
  ```

### 8.5 根据ID获取导航记录
- **接口路径**: `/api/v1/navigation-records/{record_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | record_id | integer | 是 | 导航记录ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 导航记录ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | start_location | string | 起始位置 |
  | end_location | string | 终点位置 |
  | start_time | datetime | 开始时间 |
  | end_time | datetime | 结束时间 |
  | status | integer | 状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 导航记录不存在
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/navigation-records/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "end_time": null,
    "status": 1,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 8.6 更新导航记录
- **接口路径**: `/api/v1/navigation-records/{record_id}`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | record_id | integer | 是 | 导航记录ID |
  | end_time | datetime | 否 | 结束时间 |
  | status | integer | 否 | 状态（1-进行中, 2-完成, 3-取消） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 导航记录ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | start_location | string | 起始位置 |
  | end_location | string | 终点位置 |
  | start_time | datetime | 开始时间 |
  | end_time | datetime | 结束时间 |
  | status | integer | 状态 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 导航记录不存在
  - 401: 未授权
- **示例请求**:
  ```json
  PUT /api/v1/navigation-records/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "end_time": "2026-04-12T14:35:50.518828",
    "status": 2
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "end_time": "2026-04-12T14:35:50.518828",
    "status": 2,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:35:50.518828"
  }
  ```

### 8.7 删除导航记录
- **接口路径**: `/api/v1/navigation-records/{record_id}`
- **请求方法**: DELETE
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | record_id | integer | 是 | 导航记录ID |
- **响应数据结构**: 无（204 No Content）
- **错误码说明**:
  - 404: 导航记录不存在
  - 401: 未授权
- **示例请求**:
  ```
  DELETE /api/v1/navigation-records/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 8.8 完成导航记录
- **接口路径**: `/api/v1/navigation-records/{record_id}/complete`
- **请求方法**: PATCH
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | record_id | integer | 是 | 导航记录ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 导航记录ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | start_location | string | 起始位置 |
  | end_location | string | 终点位置 |
  | start_time | datetime | 开始时间 |
  | end_time | datetime | 结束时间 |
  | status | integer | 状态（2-完成） |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 导航记录不存在
  - 401: 未授权
- **示例请求**:
  ```
  PATCH /api/v1/navigation-records/1/complete
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "end_time": "2026-04-12T14:35:50.518828",
    "status": 2,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:35:50.518828"
  }
  ```

### 8.9 取消导航记录
- **接口路径**: `/api/v1/navigation-records/{record_id}/cancel`
- **请求方法**: PATCH
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | record_id | integer | 是 | 导航记录ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 导航记录ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | start_location | string | 起始位置 |
  | end_location | string | 终点位置 |
  | start_time | datetime | 开始时间 |
  | end_time | datetime | 结束时间 |
  | status | integer | 状态（3-取消） |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 导航记录不存在
  - 401: 未授权
- **示例请求**:
  ```
  PATCH /api/v1/navigation-records/1/cancel
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "start_location": "116.397428,39.90923",
    "end_location": "116.407428,39.91923",
    "start_time": "2026-04-12T14:25:50.518828",
    "end_time": "2026-04-12T14:30:50.518828",
    "status": 3,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:30:50.518828"
  }
  ```

## 9. 语音日志相关接口

### 9.1 创建语音日志
- **接口路径**: `/api/v1/voice-logs/`
- **请求方法**: POST
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | device_id | integer | 是 | 设备ID |
  | voice_text | string | 是 | 语音文本 |
  | audio_url | string | 否 | 音频URL |
  | duration | float | 否 | 音频时长 |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 语音日志ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | voice_text | string | 语音文本 |
  | audio_url | string | 音频URL |
  | duration | float | 音频时长 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```json
  POST /api/v1/voice-logs/
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "user_id": 1,
    "device_id": 1,
    "voice_text": "导航到天安门",
    "audio_url": "https://example.com/audio.mp3",
    "duration": 3.5
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "voice_text": "导航到天安门",
    "audio_url": "https://example.com/audio.mp3",
    "duration": 3.5,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 9.2 获取用户的语音日志列表
- **接口路径**: `/api/v1/voice-logs/`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | limit | integer | 否 | 返回日志数量限制（默认100） |
- **响应数据结构**: 语音日志列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/voice-logs/?user_id=1&limit=50
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "voice_text": "导航到天安门",
      "audio_url": "https://example.com/audio.mp3",
      "duration": 3.5,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 9.3 根据设备ID获取语音日志列表
- **接口路径**: `/api/v1/voice-logs/device/{device_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | device_id | integer | 是 | 设备ID |
  | limit | integer | 否 | 返回日志数量限制（默认100） |
- **响应数据结构**: 语音日志列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/voice-logs/device/1?limit=50
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "voice_text": "导航到天安门",
      "audio_url": "https://example.com/audio.mp3",
      "duration": 3.5,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 9.4 根据时间范围获取语音日志
- **接口路径**: `/api/v1/voice-logs/time-range/{user_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | start_time | datetime | 是 | 开始时间 |
  | end_time | datetime | 是 | 结束时间 |
- **响应数据结构**: 语音日志列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/voice-logs/time-range/1?start_time=2026-04-01T00:00:00&end_time=2026-04-12T23:59:59
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "voice_text": "导航到天安门",
      "audio_url": "https://example.com/audio.mp3",
      "duration": 3.5,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 9.5 获取最近几小时的语音日志
- **接口路径**: `/api/v1/voice-logs/recent/{user_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | hours | integer | 否 | 最近几小时（默认24） |
- **响应数据结构**: 语音日志列表
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/voice-logs/recent/1?hours=12
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "device_id": 1,
      "voice_text": "导航到天安门",
      "audio_url": "https://example.com/audio.mp3",
      "duration": 3.5,
      "created_at": "2026-04-12T14:25:50.518828",
      "updated_at": "2026-04-12T14:25:50.518828"
    }
  ]
  ```

### 9.6 根据ID获取语音日志
- **接口路径**: `/api/v1/voice-logs/{log_id}`
- **请求方法**: GET
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | log_id | integer | 是 | 语音日志ID |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 语音日志ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | voice_text | string | 语音文本 |
  | audio_url | string | 音频URL |
  | duration | float | 音频时长 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 语音日志不存在
  - 401: 未授权
- **示例请求**:
  ```
  GET /api/v1/voice-logs/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "voice_text": "导航到天安门",
    "audio_url": "https://example.com/audio.mp3",
    "duration": 3.5,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:25:50.518828"
  }
  ```

### 9.7 更新语音日志
- **接口路径**: `/api/v1/voice-logs/{log_id}`
- **请求方法**: PUT
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | log_id | integer | 是 | 语音日志ID |
  | voice_text | string | 否 | 语音文本 |
  | audio_url | string | 否 | 音频URL |
  | duration | float | 否 | 音频时长 |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | id | integer | 语音日志ID |
  | user_id | integer | 用户ID |
  | device_id | integer | 设备ID |
  | voice_text | string | 语音文本 |
  | audio_url | string | 音频URL |
  | duration | float | 音频时长 |
  | created_at | datetime | 创建时间 |
  | updated_at | datetime | 更新时间 |
- **错误码说明**:
  - 404: 语音日志不存在
  - 401: 未授权
- **示例请求**:
  ```json
  PUT /api/v1/voice-logs/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  {
    "voice_text": "导航到天安门广场",
    "audio_url": "https://example.com/audio_updated.mp3"
  }
  ```
- **示例响应**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "device_id": 1,
    "voice_text": "导航到天安门广场",
    "audio_url": "https://example.com/audio_updated.mp3",
    "duration": 3.5,
    "created_at": "2026-04-12T14:25:50.518828",
    "updated_at": "2026-04-12T14:35:50.518828"
  }
  ```

### 9.8 删除语音日志
- **接口路径**: `/api/v1/voice-logs/{log_id}`
- **请求方法**: DELETE
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | log_id | integer | 是 | 语音日志ID |
- **响应数据结构**: 无（204 No Content）
- **错误码说明**:
  - 404: 语音日志不存在
  - 401: 未授权
- **示例请求**:
  ```
  DELETE /api/v1/voice-logs/1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 9.9 删除指定天数之前的语音日志
- **接口路径**: `/api/v1/voice-logs/user/{user_id}/old`
- **请求方法**: DELETE
- **请求参数**:
  | 参数名 | 类型 | 是否必填 | 描述 |
  |-------|------|---------|------|
  | user_id | integer | 是 | 用户ID |
  | days | integer | 否 | 天数（默认30） |
- **响应数据结构**:
  | 字段名 | 类型 | 描述 |
  |-------|------|------|
  | deleted_count | integer | 删除的日志数量 |
- **错误码说明**:
  - 401: 未授权
- **示例请求**:
  ```
  DELETE /api/v1/voice-logs/user/1/old?days=30
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- **示例响应**:
  ```json
  {
    "deleted_count": 10
  }
  ```