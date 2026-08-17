import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 密钥 / 大模型凭据一律走环境变量，禁止硬编码
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    # 数据库：默认本地 SQLite；生产可设 DATABASE_URL 指向 Postgres
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'inventory.db')
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 大模型（DeepSeek 兼容 OpenAI 协议）
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.deepseek.com/v1')
    LLM_MODEL = os.getenv('LLM_MODEL', 'deepseek-chat')

    # 智能体默认库存预警阈值
    AGENT_INVENTORY_THRESHOLD = int(os.getenv('AGENT_INVENTORY_THRESHOLD', '10'))
