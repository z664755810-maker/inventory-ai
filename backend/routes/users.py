from flask import Blueprint, request, jsonify, session
from extensions import db
from models.user import User
from utils.auth import login_required

bp = Blueprint('users', __name__, url_prefix='/api')

# 登录接口：每个 IP 限制 10 次/分钟，防止暴力破解
# 从 app.py 拿 limiter 实例（避免循环导入）
from app import limiter


@bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': '用户名或密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful', 'user': user.to_dict()})

    # 故意不区分"用户不存在"和"密码错误"，避免用户名枚举攻击
    return jsonify({'error': '用户名或密码错误'}), 401


@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})


# 注册：每个 IP 5 次/小时，防止恶意注册
@bp.route('/users', methods=['POST'])
@limiter.limit('5 per hour')
def create_user():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    # 入参校验
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 3 or len(username) > 50:
        return jsonify({'error': '用户名长度需 3-50 字符'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少 6 位'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


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


@bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'username' in data:
        new_username = (data['username'] or '').strip()
        if not new_username or len(new_username) < 3:
            return jsonify({'error': '用户名长度需 3-50 字符'}), 400
        # 检查是否与他人冲突
        if new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                return jsonify({'error': '用户名已被占用'}), 400
            user.username = new_username
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': '密码至少 6 位'}), 400
        user.set_password(data['password'])

    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    # 不允许删除默认管理员账号（防止自我删除锁死系统）
    if id == 1:
        return jsonify({'error': '默认管理员账号不可删除'}), 400

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
