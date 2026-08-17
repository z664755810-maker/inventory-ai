from flask import Blueprint, request, jsonify
from extensions import db
from models.category import Category
from utils.auth import login_required

bp = Blueprint('categories', __name__, url_prefix='/api')

@bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories])

@bp.route('/categories/tree', methods=['GET'])
@login_required
def get_category_tree():
    root_categories = Category.query.filter_by(parent_id=None).all()
    return jsonify([cat.to_tree_dict() for cat in root_categories])

@bp.route('/categories/<int:id>', methods=['GET'])
@login_required
def get_category(id):
    category = Category.query.get(id)
    if category:
        return jsonify(category.to_dict())
    return jsonify({'error': 'Category not found'}), 404

@bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'error': '分类名称不能为空'}), 400
            
        category = Category(
            name=data.get('name'),
            parent_id=data.get('parent_id')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建分类失败: {str(e)}'}), 500

@bp.route('/categories/<int:id>', methods=['PUT'])
@login_required
def update_category(id):
    try:
        category = Category.query.get(id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
        
        data = request.get_json()
        if 'name' in data:
            category.name = data['name']
        if 'parent_id' in data:
            category.parent_id = data['parent_id']
        
        db.session.commit()
        return jsonify(category.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新分类失败: {str(e)}'}), 500

@bp.route('/categories/<int:id>', methods=['DELETE'])
@login_required
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})
