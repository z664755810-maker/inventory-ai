from flask import Flask, session, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import event
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# 使用绝对路径配置前端目录，防止权限问题
app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['FRONTEND_DIR'] = os.path.join(app_dir, 'static')

CORS(app, supports_credentials=True)

# ---------- 安全：限流（防暴力破解 / API 滥用）----------
# 默认：所有接口每 IP 每小时 600 次 / 每分钟 100 次
# 登录接口在 routes/users.py 里单独设置更严
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=['600 per hour', '100 per minute'],
    storage_uri='memory://',
    headers_enabled=True,  # 响应里加 X-RateLimit-* 头
)
limiter.init_app(app)


# ---------- 安全：每个响应都带 CSP / 防 XSS / 防点击劫持等头 ----------
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # 允许同源 + 智谱 API（CORS 已通过 Flask-CORS 处理，浏览器 CSP 适度放开）
    # 注意：script-src 必须包含 cdn.jsdelivr.net，否则 index.html 的 Chart.js 会被拦截、图表全空
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'self';"
    )
    return response


from extensions import db
db.init_app(app)

# ---------- 安全：SQLite 启用 WAL 模式 + 5s busy_timeout ----------
# WAL 让读写并发，busy_timeout 让偶发锁等待不报错
# 必须注册到具体 engine 上，全局 Engine 监听不会命中 ORM 用的连接
with app.app_context():
    @event.listens_for(db.engine, 'connect')
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        # SQLite 连接（pysqlite）才需要设置
        if 'sqlite' not in str(type(dbapi_connection).__module__).lower():
            return
        cursor = dbapi_connection.cursor()
        # PRAGMA 必须消费结果并 commit，否则设置不生效
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.fetchall()
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.fetchall()
        cursor.execute('PRAGMA busy_timeout=5000')
        cursor.fetchall()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.fetchall()
        dbapi_connection.commit()
        cursor.close()

with app.app_context():
    from routes import users, categories, products, customers, purchase_orders, sales_orders, stock, invoices, agent

    # 注册蓝图
    app.register_blueprint(users)
    app.register_blueprint(categories)
    app.register_blueprint(products)
    app.register_blueprint(customers)
    app.register_blueprint(purchase_orders)
    app.register_blueprint(sales_orders)
    app.register_blueprint(stock)
    app.register_blueprint(invoices)
    app.register_blueprint(agent)

    db.create_all()
    print("Database tables created successfully")

    # 临时容器（如 Railway）SQLite 为空库，启动时自动填充演示数据（幂等）
    from seed_data import seed_if_empty
    seed_if_empty()

# ---------- 公开接口 ----------
@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}


# ---------- 错误处理：所有未捕获异常都返回友好 JSON ----------
@app.errorhandler(404)
def not_found(_e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return send_from_directory(app.config['FRONTEND_DIR'], 'login.html'), 200


@app.errorhandler(500)
def server_error(_e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_unhandled(exc):
    """兜底：捕获所有未处理异常，避免 502 / 进程崩溃。"""
    # 记录到日志便于排查
    app.logger.error('Unhandled exception: %s\n%s', exc, traceback.format_exc())
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': f'服务器错误：{type(exc).__name__}'}), 500
    return jsonify({'success': False, 'error': '服务器异常'}), 500


@app.errorhandler(429)
def ratelimit_handler(_e):
    """限流命中时返回 429 而非默认 500。"""
    return jsonify({'success': False, 'error': '请求过于频繁，请稍后再试'}), 429


# ---------- 前端页面路由 ----------
@app.route('/')
def index():
    return send_from_directory(app.config['FRONTEND_DIR'], 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(app.config['FRONTEND_DIR'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
