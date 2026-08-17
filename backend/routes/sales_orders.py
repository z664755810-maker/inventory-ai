from flask import Blueprint, request, jsonify
from extensions import db
from models.sales_order import SalesOrder
from models.product import Product
from utils.auth import login_required
from datetime import datetime, timedelta

bp = Blueprint('sales_orders', __name__, url_prefix='/api')

@bp.route('/sales-orders', methods=['GET'])
@login_required
def get_sales_orders():
    days = request.args.get('days', type=int)
    
    query = SalesOrder.query
    
    if days:
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        query = query.filter(SalesOrder.sale_date >= date_threshold)
    
    orders = query.all()
    return jsonify([o.to_dict() for o in orders])

@bp.route('/sales-orders/<int:id>', methods=['GET'])
@login_required
def get_sales_order(id):
    order = SalesOrder.query.get(id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({'error': 'Sales order not found'}), 404

@bp.route('/sales-orders', methods=['POST'])
@login_required
def create_sales_order():
    data = request.get_json()
    
    product = Product.query.get(data.get('product_id'))
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.stock < data.get('quantity', 0):
        return jsonify({'error': 'Insufficient stock'}), 400
    
    unit_price = data.get('unit_price')
    quantity = data.get('quantity')
    total_amount = unit_price * quantity if unit_price and quantity else None
    
    order = SalesOrder(
        customer_id=data.get('customer_id'),
        product_id=data.get('product_id'),
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount
    )
    db.session.add(order)
    
    product.stock -= quantity
    db.session.commit()
    
    return jsonify(order.to_dict()), 201

@bp.route('/sales-orders/<int:id>', methods=['PUT'])
@login_required
def update_sales_order(id):
    order = SalesOrder.query.get(id)
    if not order:
        return jsonify({'error': 'Sales order not found'}), 404
    
    old_quantity = order.quantity
    data = request.get_json()
    
    if 'quantity' in data:
        product = Product.query.get(order.product_id)
        if product:
            product.stock += old_quantity
            if product.stock < data['quantity']:
                return jsonify({'error': 'Insufficient stock'}), 400
            product.stock -= data['quantity']
    
    if 'customer_id' in data:
        order.customer_id = data['customer_id']
    if 'product_id' in data:
        order.product_id = data['product_id']
    if 'quantity' in data:
        order.quantity = data['quantity']
    if 'unit_price' in data:
        order.unit_price = data['unit_price']
    if 'status' in data:
        order.status = data['status']
    if 'unit_price' in data or 'quantity' in data:
        order.total_amount = (order.unit_price or 0) * (order.quantity or 0)
    
    db.session.commit()
    return jsonify(order.to_dict())

@bp.route('/sales-orders/<int:id>', methods=['DELETE'])
@login_required
def delete_sales_order(id):
    order = SalesOrder.query.get(id)
    if not order:
        return jsonify({'error': 'Sales order not found'}), 404
    
    product = Product.query.get(order.product_id)
    if product:
        product.stock += order.quantity
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Sales order deleted successfully'})
