# SeniRoad - 老年人智能导航软件

## 📋 项目概述

**版本号**: V5.0  
**日期**: 2026年6月2日

随着我国老龄化进程的加快，老年群体的日常出行需求日益增长。本项目旨在打造一款极简操作、贴合老年习惯的适老化智能导航软件，解决老年群体出行痛点，提升其生活自主性，并缓解家属的照护压力。

**核心目标**：实现"老年人独立安全出行、家属远程可守护"

---

## 👥 用户角色分析

| 用户角色 | 特征 | 主要需求 |
|----------|------|----------|
| **老年用户** | 年龄较大，对智能手机操作不熟练，视力、听力下降 | 简单、语音化的导航体验 |
| **家属用户** | 老年人的子女或照护者 | 远程监护、预设常用地点、降低照护焦虑 |

---

## ✨ 核心功能

### 📱 老年端功能

#### 智能适老化导航
- **语音交互发起导航**：支持语音输入目的地
- **AI语义解析**：解析模糊、口语化表达（如"去老二家"）
- **目的地确认**：信息不足时联系家属确认
- **全语音导航引导**：如"前方路口请左转，注意红绿灯"
- **常用地点管理**：一键发起前往常用地点的导航，同步家属预设地点

#### 通信功能
- **一键通话**：快速联系紧急联系人

### 👨‍👩‍👧 家属端功能

#### 安全状态监控
- **实时位置推送**：查看老年人当前位置
- **历史轨迹查询**：查看出行记录和位置历史

#### 联动管理
- **绑定管理**：双向绑定老年端与家属端
- **地点预设**：预设常用地点（医院、子女家、超市等）并同步至老年端
- **历史记录查询**：查看出行记录，协助更新常用地点

---

## 🛠️ 技术架构

### 技术栈

| 层次 | 技术 | 用途 |
|------|------|------|
| **前端** | 微信小程序 | 跨平台可视化交互 |
| **后端** | FastAPI | 高效数据接口服务 |
| **数据层** | PostgreSQL | 结构化存储 |
| **大模型** | qwen3.6-plus (DashScope) | 语义解析、出行建议 |
| **导航服务** | 高德地图API | 地图数据、路线规划 |
| **语音识别** | qwen3-asr-flash | 支持多种中文口音与方言 |
| **语音合成** | cosyvoice-v2 (DashScope) | 生成自然语音导航 |
| **流式输出** | SSE技术 | 实时导航响应 |

### 系统架构图

```mermaid
flowchart TB
    subgraph 前端层
        A1[老年端小程序]
        A2[家属端小程序]
    end
    
    subgraph API网关层
        B1[FastAPI]
        B2[WebSocket（待实现）]
    end
    
    subgraph 业务逻辑层
        C1[认证服务]
        C2[导航服务]
        C3[位置服务]
        C4[绑定服务]
        C5[语音服务]
        C6[用户服务]
        C7[通知服务]
    end
    
    subgraph AI智能体层
        D1[目的地解析节点]
        D2[路线规划节点]
        D3[语音转文字]
        D4[文字转语音]
        D5[导航工作流]
    end
    
    subgraph 数据访问层
        E1[用户仓储]
        E2[位置仓储]
        E3[导航记录仓储]
        E4[绑定关系仓储]
    end
    
    subgraph 外部服务
        F1[高德地图API]
        F2[Qwen大模型\nDashScope]
        F3[DeepSeek\nModelScope]
        F4[微信小程序API]
    end
    
    subgraph 数据存储层
        G1[(PostgreSQL)]
        G2[(Redis（待实现）)]
    end
    
    A1 --> B1
    A2 --> B1
    
    B1 --> C1
    B1 --> C2
    B1 --> C3
    B1 --> C4
    B1 --> C5
    B1 --> C6
    B1 --> C7
    
    C2 --> D5
    C5 --> D3
    C5 --> D4
    
    D5 --> D1
    D5 --> D2
    D1 --> F2
    D2 --> F1
    D3 --> F2
    D4 --> F2
    
    C1 --> E1
    C2 --> E3
    C3 --> E2
    C4 --> E4
    C6 --> E1
    
    E1 --> G1
    E2 --> G1
    E3 --> G1
    E4 --> G1
    
    C1 --> F4
```

---

## 🚀 快速开始

### 环境要求

- Python >= 3.14
- Node.js >= 18.x
- PostgreSQL >= 15.x
- Redis >= 7.x

### 后端部署

```bash
# 进入后端目录
cd yilu_an_backend

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键项：
- 数据库连接信息
- 高德地图API Key
- DashScope API Key（Qwen大模型）
- 微信小程序AppID和AppSecret

```bash
# 启动服务
uv run python run_server.py
```

服务启动后访问：http://localhost:8000

### 前端开发

```bash
# 进入前端目录
cd yilu_an_frontend

# 安装依赖
npm install

# 配置API地址
cp miniprogram/utils/config_example.ts miniprogram/utils/config.ts
```
在 `project.json` 中配置小程序AppID。
使用微信开发者工具打开 `miniprogram` 目录进行开发调试。

---

## 🔧 环境变量配置

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/yilu_an
REDIS_URL=redis://localhost:6379

# 地图服务
AMAP_API_KEY=your_amap_key
TENCENT_MAP_API_KEY=your_tencent_map_key

# JWT配置
JWT_SECRET_KEY=your_jwt_secret

# AI服务 (Qwen)
DASHSCOPE_API_KEY=your_dashscope_key
DASHSCOPE_TEXT_MODEL=qwen3.6-plus
DASHSCOPE_ASR_MODEL=Qwen3-ASR-Flash
DASHSCOPE_TTS_MODEL=cosyvoice-v2

# 微信小程序
WECHAT_APPID=your_wechat_appid
WECHAT_APPSECRET=your_wechat_appsecret
```

---

## 📁 项目结构

```
SeniRoad/
├── yilu_an_backend/          # 后端服务
│   ├── app/                  # 应用核心代码
│   │   ├── api/              # API路由
│   │   ├── services/         # 业务逻辑层
│   │   ├── agent/            # AI智能体
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic验证模型
│   │   ├── repositories/     # 数据访问层
│   │   ├── dependencies/     # 依赖注入
│   │   ├── middleware/       # 中间件
│   │   ├── utils/            # 工具函数
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   └── main.py           # FastAPI入口
│   ├── .env.example          # 环境变量模板
│   ├── pyproject.toml        # Python依赖配置
│   └── run_server.py         # 启动脚本
├── yilu_an_frontend/         # 前端小程序
│   ├── miniprogram/          # 小程序代码
│   │   ├── elderly/          # 老年端页面
│   │   ├── family/           # 家属端页面
│   │   ├── api/              # API封装
│   │   ├── utils/            # 工具函数
│   │   └── assets/           # 静态资源
│   └── typings/              # TypeScript类型定义
└── tips/                     # 展望未来功能与优化
```

---

## 🔍 API接口

### 认证接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 账号密码登录 |
| `/api/v1/auth/wechat/login` | POST | 微信小程序登录 |

### 用户接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/user/profile` | GET | 获取用户信息 |
| `/api/v1/user/profile` | PUT | 更新用户信息 |

### 导航接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/navigation/route` | POST | 规划导航路线 |
| `/api/v1/navigation/navigate` | POST | 开始实时导航 |

### 位置接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/location/report` | POST | 上报位置 |
| `/api/v1/location/track` | GET | 获取轨迹 |

### 绑定接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/binding/create` | POST | 创建绑定关系 |
| `/api/v1/binding/list` | GET | 获取绑定列表 |

### WebSocket
| 接口 | 描述 |
|------|------|
| `/ws/location` | 实时位置推送 |

---

## 🎯 非功能性需求

### 适老化体验
- **界面极简**：剔除冗余功能入口，放大核心操作按钮
- **视觉优化**：支持大字体、高对比度模式
- **听觉优化**：优化语音播报的音量、语速和音色

### 性能与可靠性
- **响应时间**：语音识别与路线规划响应迅速
- **稳定性**：持续导航和通信过程保持稳定

### 可扩展性
- 支持接入更多第三方服务（紧急呼叫、医疗资源等）
- 方言识别和老人异常状态判定
- 语音陪伴助手
- 老年人友好路线优先筛选

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。
