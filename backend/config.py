import os

from dotenv import load_dotenv

load_dotenv()  # 本地开发读取 .env；部署平台直接注入环境变量时不冲突

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

    # SQLite 引擎参数：
    # - check_same_thread=False：允许多线程访问 Flask app context
    # - timeout=15：写入冲突时等待 15 秒，避免「database is locked」瞬时失败
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False, 'timeout': 15},
        'pool_pre_ping': True,  # 每次连接前 ping，断线自动重连
    }

    # Session Cookie 安全加固
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 小时过期

    # 大模型（OpenAI 兼容协议；默认智谱 GLM-4-Flash 免费版）
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
    LLM_MODEL = os.getenv('LLM_MODEL', 'glm-4-flash')

    # 智能体默认库存预警阈值（默认 50，电商惯例：库存低于 50 即视为预警商品）
    AGENT_INVENTORY_THRESHOLD = int(os.getenv('AGENT_INVENTORY_THRESHOLD', '50'))
