# 物流进销存系统 - 概要设计文档

## 1. 需求分析

### 1.1 项目背景
本系统是一个面向物流行业的进销存管理系统，旨在实现商品采购、销售、库存管理的信息化管理。

### 1.2 功能需求

| 模块 | 功能描述 | 说明 |
|------|----------|------|
| 用户管理 | 系统用户表管理 | 支持用户的增删改查 |
| 商品类型 | 树形结构分类管理 | 商品类别支持层级结构 |
| 商品档案 | 商品基本信息管理 | 商品的基础档案维护 |
| 客户档案 | 客户信息管理 | 支持采购入库单和销售出库单关联 |
| 采购入库单 | 采购入库业务处理 | 记录商品采购入库信息 |
| 库存查询 | 库存信息查询 | 查询当前库存状态 |
| 销售出库单 | 销售出库业务处理 | 记录商品销售出库信息 |
| 发票单 | 发票信息管理 | 独立表，仅含文本字段，无需外键 |

### 1.3 非功能需求
- 字段设计简洁，具备基础功能即可
- 发票单为独立表，不依赖其他表外键
- 采用前后端分离架构
- 前后端通过REST API进行数据交换
- 采用简单的权限和登录验证方式

---

## 2. 技术选型

### 2.1 后端技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 语言 | Python | 3.8 | 后端开发语言 |
| 框架 | Flask | 2.x | Web应用框架 |
| ORM | SQLAlchemy | 2.x | 数据库ORM框架 |
| 数据库 | SQLite | 3.x | 轻量级数据库（开发/测试环境） |
| API规范 | RESTful | - | REST API设计标准 |

### 2.2 前端技术栈

| 分类 | 技术 | 说明 |
|------|------|------|
| HTML | HTML5 | 页面结构 |
| CSS | CSS3 | 页面样式 |
| JavaScript | ES6+ | 前端逻辑 |
| AJAX | Fetch API | 异步数据请求 |
| UI控件 | 轻量级控件库 | 体积较小的UI组件 |

### 2.3 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                      │
│  HTML + CSS + JavaScript + Fetch API                       │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端层 (Backend)                       │
│  Flask + SQLAlchemy + REST API                             │
└─────────────────────────────────────────────────────────────┘
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Database)                      │
│                      SQLite                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 数据库模型设计

### 3.1 实体关系图 (ERD)

```
用户表 (users)
    │
    ├─ id (主键)
    ├─ username
    ├─ password
    └─ ...

商品类型表 (categories)  ──┐ 树形结构
    │                      │ parent_id → id
    ├─ id (主键)           │
    ├─ name                │
    └─ parent_id (外键) ───┘

商品档案表 (products)
    │
    ├─ id (主键)
    ├─ name
    ├─ category_id (外键 → categories)
    └─ ...

客户档案表 (customers)
    │
    ├─ id (主键)
    ├─ name
    └─ ...

采购入库单表 (purchase_orders)
    │
    ├─ id (主键)
    ├─ customer_id (外键 → customers)
    ├─ product_id (外键 → products)
    └─ ...

销售出库单表 (sales_orders)
    │
    ├─ id (主键)
    ├─ customer_id (外键 → customers)
    ├─ product_id (外键 → products)
    └─ ...

发票单表 (invoices)
    │
    ├─ id (主键)
    └─ 文本字段... (无外键)
```

### 3.2 数据表详细设计

#### 3.2.1 用户表 (users)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 用户唯一标识 |
| username | VARCHAR(50) | NOT NULL UNIQUE | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码（加密存储） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 3.2.2 商品类型表 (categories)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 类型唯一标识 |
| name | VARCHAR(100) | NOT NULL | 类型名称 |
| parent_id | INTEGER | FOREIGN KEY → categories(id) | 父类型ID（支持树形结构） |

#### 3.2.3 商品档案表 (products)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 商品唯一标识 |
| name | VARCHAR(200) | NOT NULL | 商品名称 |
| category_id | INTEGER | FOREIGN KEY → categories(id) | 所属类型 |
| unit | VARCHAR(20) | - | 计量单位 |
| price | DECIMAL(10,2) | - | 参考价格 |
| stock | INTEGER | DEFAULT 0 | 当前库存 |

#### 3.2.4 客户档案表 (customers)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 客户唯一标识 |
| name | VARCHAR(100) | NOT NULL | 客户名称 |
| contact | VARCHAR(50) | - | 联系人 |
| phone | VARCHAR(20) | - | 联系电话 |

#### 3.2.5 采购入库单表 (purchase_orders)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 单据唯一标识 |
| customer_id | INTEGER | FOREIGN KEY → customers(id) | 供应商ID |
| product_id | INTEGER | FOREIGN KEY → products(id) | 商品ID |
| quantity | INTEGER | NOT NULL | 入库数量 |
| unit_price | DECIMAL(10,2) | - | 单价 |
| total_amount | DECIMAL(12,2) | - | 总金额 |
| purchase_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | 入库日期 |

#### 3.2.6 销售出库单表 (sales_orders)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 单据唯一标识 |
| customer_id | INTEGER | FOREIGN KEY → customers(id) | 客户ID |
| product_id | INTEGER | FOREIGN KEY → products(id) | 商品ID |
| quantity | INTEGER | NOT NULL | 出库数量 |
| unit_price | DECIMAL(10,2) | - | 单价 |
| total_amount | DECIMAL(12,2) | - | 总金额 |
| sale_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | 出库日期 |

#### 3.2.7 发票单表 (invoices)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 发票唯一标识 |
| invoice_no | VARCHAR(50) | NOT NULL | 发票编号 |
| content | TEXT | - | 发票内容 |
| amount | DECIMAL(12,2) | - | 金额 |
| invoice_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | 开票日期 |

---

## 4. REST API 接口设计

### 4.1 用户管理接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/users` | GET | 获取用户列表 |
| `/api/users/<id>` | GET | 获取单个用户 |
| `/api/users` | POST | 创建新用户 |
| `/api/users/<id>` | PUT | 更新用户信息 |
| `/api/users/<id>` | DELETE | 删除用户 |
| `/api/login` | POST | 用户登录 |

### 4.2 商品类型接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/categories` | GET | 获取商品类型树 |
| `/api/categories` | POST | 创建商品类型 |
| `/api/categories/<id>` | PUT | 更新商品类型 |
| `/api/categories/<id>` | DELETE | 删除商品类型 |

### 4.3 商品档案接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/products` | GET | 获取商品列表 |
| `/api/products/<id>` | GET | 获取单个商品 |
| `/api/products` | POST | 创建商品 |
| `/api/products/<id>` | PUT | 更新商品信息 |
| `/api/products/<id>` | DELETE | 删除商品 |

### 4.4 客户档案接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/customers` | GET | 获取客户列表 |
| `/api/customers/<id>` | GET | 获取单个客户 |
| `/api/customers` | POST | 创建客户 |
| `/api/customers/<id>` | PUT | 更新客户信息 |
| `/api/customers/<id>` | DELETE | 删除客户 |

### 4.5 采购入库单接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/purchase-orders` | GET | 获取采购入库单列表 |
| `/api/purchase-orders/<id>` | GET | 获取单个采购入库单 |
| `/api/purchase-orders` | POST | 创建采购入库单 |
| `/api/purchase-orders/<id>` | PUT | 更新采购入库单 |
| `/api/purchase-orders/<id>` | DELETE | 删除采购入库单 |

### 4.6 销售出库单接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/sales-orders` | GET | 获取销售出库单列表 |
| `/api/sales-orders/<id>` | GET | 获取单个销售出库单 |
| `/api/sales-orders` | POST | 创建销售出库单 |
| `/api/sales-orders/<id>` | PUT | 更新销售出库单 |
| `/api/sales-orders/<id>` | DELETE | 删除销售出库单 |

### 4.7 库存查询接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/stock` | GET | 查询库存列表 |
| `/api/stock/<product_id>` | GET | 查询单个商品库存 |

### 4.8 发票单接口

| API路径 | HTTP方法 | 功能描述 |
|---------|----------|----------|
| `/api/invoices` | GET | 获取发票列表 |
| `/api/invoices/<id>` | GET | 获取单个发票 |
| `/api/invoices` | POST | 创建发票 |
| `/api/invoices/<id>` | PUT | 更新发票 |
| `/api/invoices/<id>` | DELETE | 删除发票 |

---

## 5. 前端页面设计规划

### 5.1 页面结构

| 页面名称 | 功能描述 | 路径 |
|----------|----------|------|
| 登录页 | 用户登录 | `/login` |
| 首页/仪表盘 | 系统概览 | `/` |
| 用户管理 | 用户列表与操作 | `/users` |
| 商品类型管理 | 树形结构管理 | `/categories` |
| 商品档案管理 | 商品信息管理 | `/products` |
| 客户档案管理 | 客户信息管理 | `/customers` |
| 采购入库 | 采购入库单管理 | `/purchase-orders` |
| 销售出库 | 销售出库单管理 | `/sales-orders` |
| 库存查询 | 库存信息查看 | `/stock` |
| 发票管理 | 发票信息管理 | `/invoices` |

### 5.2 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  Header (顶部导航栏)                                    │
│  ┌─────────────────┬─────────────────────────────────┐ │
│  │ Logo/系统名称    │ 导航菜单 | 用户信息/退出        │ │
│  └─────────────────┴─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Sidebar (左侧菜单)        │  Main Content (主内容区)   │
│  ┌───────────────────────┐ │                           │
│  │ 用户管理              │ │                           │
│  │ 商品类型              │ │                           │
│  │ 商品档案              │ │   表格/表单/详情           │
│  │ 客户档案              │ │                           │
│  │ 采购入库              │ │                           │
│  │ 销售出库              │ │                           │
│  │ 库存查询              │ │                           │
│  │ 发票管理              │ │                           │
│  └───────────────────────┘ │                           │
└─────────────────────────────┴───────────────────────────┘
```

---

## 6. 权限与登录验证方案

### 6.1 认证机制

- **登录方式**: 用户名 + 密码
- **Session管理**: 使用Flask Session
- **密码加密**: 使用BCrypt进行密码哈希存储

### 6.2 权限控制

| 用户角色 | 权限说明 |
|----------|----------|
| 管理员 | 所有功能权限 |
| 普通用户 | 基础业务操作权限 |

### 6.3 登录流程

```
用户访问登录页面 → 输入用户名密码 → 发送POST请求到/api/login → 
验证用户名密码 → 生成Session → 返回登录成功 → 跳转首页
```

### 6.4 接口访问控制

- 登录接口 `/api/login`: 公开访问
- 其他业务接口: 需要登录验证
- 使用Flask装饰器进行登录状态检查

---

## 7. 项目目录结构

```
project/
├── backend/                    # 后端代码
│   ├── app.py                  # Flask应用入口
│   ├── models/                 # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── purchase_order.py
│   │   ├── sales_order.py
│   │   └── invoice.py
│   ├── routes/                 # API路由
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   ├── customers.py
│   │   ├── purchase_orders.py
│   │   ├── sales_orders.py
│   │   ├── stock.py
│   │   └── invoices.py
│   ├── utils/                  # 工具函数
│   │   └── __init__.py
│   └── requirements.txt        # 依赖列表
└── frontend/                   # 前端代码
    ├── index.html
    ├── login.html
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── app.js
    │   └── api.js
    └── pages/
        ├── users.html
        ├── categories.html
        ├── products.html
        ├── customers.html
        ├── purchase-orders.html
        ├── sales-orders.html
        ├── stock.html
        └── invoices.html
```

---

## 8. 部署与运行

### 8.1 环境要求

- Python 3.8+
- Flask 2.x
- SQLAlchemy 2.x
- SQLite 3.x

### 8.2 安装与运行

```bash
# 后端部署
cd backend
pip install -r requirements.txt
python app.py

# 前端运行
cd frontend
# 使用静态服务器或直接打开HTML文件
```

---

**文档版本**: v1.0  
**创建日期**: 2026-06-23  
**适用项目**: 物流进销存系统