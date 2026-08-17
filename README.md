# 智能进销存系统（project_zxy）

基于 **Flask + Vue3** 的全栈进销存管理系统，内置一个**基于意图识别 + 大模型（LLM）的自然语言智能助手**，可查询库存、分析销售、生成经营报表。

> 项目定位：求职作品集（二本 / 27 届计算机科学与技术）。演示重点 = 全栈工程能力 + AI 协同落地能力。

## 技术栈
- 后端：Flask（Blueprint 模块化）、Flask-SQLAlchemy、SQLite（可切换 Postgres）
- 前端：Vue3（CDN 引入，无需构建步骤）、Chart.js、原生 HTML/CSS/JS
- AI：DeepSeek（OpenAI 兼容协议）大模型问答，意图路由 + 真实数据抓取 + LLM 合成，无 Key 时自动降级为本地规则答复

## 目录结构
```
project_zxy/
├── backend/
│   ├── app.py            # Flask 入口（配置 / 注册蓝图 / 错误处理）
│   ├── config.py         # 环境变量配置（密钥 / 数据库 / 大模型）
│   ├── llm.py            # 大模型调用封装（失效自动降级）
│   ├── extensions.py     # SQLAlchemy 实例
│   ├── models/           # 数据模型（商品/客户/订单/库存/发票…）
│   ├── routes/           # 业务路由（含 agent.py 智能体）
│   ├── utils/            # 工具（auth 等）
│   ├── requirements.txt
│   └── test_agent.py     # pytest 测试
├── frontend/             # Vue3 页面（由 Flask 直接托管）
├── .env.example          # 环境变量模板
└── README.md
```

## 本地运行
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env 并填入 Key）
cp ../.env.example ../.env
# 编辑 .env：LLM_API_KEY=你的DeepSeek Key；SECRET_KEY=随机串

# 初始化数据库（如 inventory.db 不存在）
python init_db.py        # 或 rebuild_db.py 重置

python app.py            # 访问 http://127.0.0.1:5000
```

## 运行测试
```bash
cd backend
pip install pytest
pytest test_agent.py -v   # 离线兜底路径，无需网络 / API Key
```

## 智能体说明（面试可讲）
1. 用户提问 → `analyze_intent` 做**意图路由**（库存 / 销售 / 报表 / 通用）。
2. 按意图调用对应的 `gather_*` 函数，**真实查询数据库**得到结构化数据。
3. 将数据 + 用户问题组装成提示词，交给 **LLM 合成自然语言答复**。
4. 若未配置 Key 或调用失败，自动降级为本地规则摘要，**演示绝不崩**。

> 诚实注记：智能体调用的是真实大模型 API（非写死模板）。如未配置 `LLM_API_KEY`，则以本地规则兜底，但简历 / 面试中应如实说明"已接入大模型、并保留离线降级"。

## 部署（Render，免费层 ¥0/月）
整个 Flask 应用（API + 前端）作为一个 Web Service 部署：
1. 推送到 GitHub 仓库。
2. Render → New Web Service → 连接仓库，Root Directory 设为 `backend`。
3. Build Command：`pip install -r requirements.txt`
4. Start Command：`gunicorn app:app --bind 0.0.0.0:$PORT`
5. 在 Render 后台设置环境变量：`LLM_API_KEY`、`SECRET_KEY`（**不要提交到仓库**）。
6. 免费层文件系统为临时盘，演示数据建议用 Render Postgres 免费层（设 `DATABASE_URL`）。

详细说明见陪跑文档《求职陪跑_阶段2.5_职位规划与项目部署.md》。
