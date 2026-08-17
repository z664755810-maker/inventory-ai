from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'jinxiaoying-secret-key-2026'

app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app_dir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FRONTEND_DIR'] = os.path.join(app_dir, '..', 'frontend')

CORS(app, supports_credentials=True)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {'id': self.id, 'username': self.username}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful', 'user': user.to_dict()})
    
    return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict())
    return jsonify({'error': 'User not logged in'}), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    user = User(username=data.get('username'))
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': '密码重置成功'})

@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}

@app.route('/')
def index():
    return send_from_directory(app.config['FRONTEND_DIR'], 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(app.config['FRONTEND_DIR'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    app.run(debug=True, host='0.0.0.0', port=5000)
