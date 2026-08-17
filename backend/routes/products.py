from flask import Blueprint, request, jsonify
from extensions import db
from models.product import Product
from utils.auth import login_required

bp = Blueprint('products', __name__, url_prefix='/api')

@bp.route('/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@bp.route('/products/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    product = Product.query.get(id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({'error': 'Product not found'}), 404

@bp.route('/products', methods=['POST'])
@login_required
def create_product():
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'error': '商品名称不能为空'}), 400
            
        product = Product(
            name=data.get('name'),
            category_id=data.get('category_id'),
            unit=data.get('unit'),
            price=data.get('price'),
            stock=data.get('stock', 0)
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建商品失败: {str(e)}'}), 500

@bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        data = request.get_json()
        if 'name' in data:
            product.name = data['name']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'unit' in data:
            product.unit = data['unit']
        if 'price' in data:
            product.price = data['price']
        if 'stock' in data:
            product.stock = data['stock']
        
        db.session.commit()
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新商品失败: {str(e)}'}), 500

@bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
