# 颐路安后端服务

老年人智能导航助手 FastAPI 后端

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动服务
python run_server.py
```

## 项目框架

```text
yilu_an_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型（老年/家属）
│   │   ├── location.py         # 位置/轨迹模型
│   │   ├── destination.py      # 目的地模型
│   │   └── binding.py          # 绑定关系模型
│   ├── schemas/                # Pydantic数据验证
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── location.py
│   │   ├── destination.py
│   │   └── binding.py
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # 认证接口
│   │   │   ├── user.py         # 用户接口
│   │   │   ├── navigation.py   # 导航接口
│   │   │   ├── location.py     # 位置接口
│   │   │   ├── destination.py  # 目的地接口
│   │   │   └── binding.py      # 绑定接口
│   │   └── websocket.py        # WebSocket实时通信
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证服务
│   │   ├── navigation.py       # 导航服务（高德API）
│   │   ├── location.py         # 位置服务
│   │   ├── ai_parser.py        # AI语义解析（Qwen）
│   │   └── notification.py     # 消息推送服务
│   ├── repositories/           # 数据访问层
│   │   ├── __init__.py
│   │   ├── user_repository.py  # 用户数据访问
│   │   ├── location_repository.py  # 位置数据访问
│   │   ├── destination_repository.py  # 目的地数据访问
│   │   └── binding_repository.py  # 绑定关系数据访问
│   ├── dependencies/           # 依赖注入函数
│   │   ├── __init__.py
│   │   └── auth.py             # 认证依赖
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── security.py         # 密码加密
│   │   └── validators.py       # 数据验证
│   └── middleware/             # 中间件
│       ├── __init__.py
│       ├── logging.py           # 日志记录中间件
│       └── cors.py              # CORS处理中间件
├── tests/                      # 测试文件
├── requirements.txt            # 依赖包
├── .env                        # 环境变量
└── README.md                   # 项目说明
```

