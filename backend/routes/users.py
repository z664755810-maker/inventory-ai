from flask import Blueprint, request, jsonify, session
from extensions import db
from models.user import User
from utils.auth import login_required

bp = Blueprint('users', __name__, url_prefix='/api')

@bp.route('/login', methods=['POST'])
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

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

@bp.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    user = User(username=data.get('username'))
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict())
    return jsonify({'error': 'User not logged in'}), 401

@bp.route('/forgot-password', methods=['POST'])
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
