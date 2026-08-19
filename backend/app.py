from flask import Flask, session, send_from_directory, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# 使用绝对路径配置前端目录，防止权限问题
app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['FRONTEND_DIR'] = os.path.join(app_dir, '..', 'frontend')

CORS(app, supports_credentials=True)

from extensions import db
db.init_app(app)

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

@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}

@app.errorhandler(404)
def not_found(_e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(_e):
    return jsonify({'error': 'Internal server error'}), 500

# 前端页面路由
@app.route('/')
def index():
    return send_from_directory(app.config['FRONTEND_DIR'], 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(app.config['FRONTEND_DIR'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
