from flask import Blueprint, jsonify
from models.product import Product
from utils.auth import login_required

bp = Blueprint('stock', __name__, url_prefix='/api')

def get_stock_data():
    """获取库存数据，供其他模块使用（非Flask路由）"""
    products = Product.query.all()
    return [{
        'product_id': p.id,
        'product_name': p.name,
        'category_id': p.category_id,
        'category_name': p.category.name if p.category else None,
        'unit': p.unit,
        'reference_price': float(p.price) if p.price else None,
        'price': float(p.price) if p.price else None,
        'stock': p.stock
    } for p in products]

@bp.route('/stock', methods=['GET'])
@login_required
def get_stock():
    products = Product.query.all()
    stock_data = [{
        'product_id': p.id,
        'product_name': p.name,
        'category_id': p.category_id,
        'category_name': p.category.name if p.category else None,
        'unit': p.unit,
        'price': float(p.price) if p.price else None,
        'stock': p.stock
    } for p in products]
    return jsonify(stock_data)

@bp.route('/stock/<int:product_id>', methods=['GET'])
@login_required
def get_stock_by_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'product_id': product.id,
            'product_name': product.name,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else None,
            'unit': product.unit,
            'price': float(product.price) if product.price else None,
            'stock': product.stock
        })
    return jsonify({'error': 'Product not found'}), 404
