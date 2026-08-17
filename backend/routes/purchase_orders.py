from flask import Blueprint, request, jsonify
from extensions import db
from models.purchase_order import PurchaseOrder
from models.product import Product
from utils.auth import login_required
from datetime import datetime, timedelta

bp = Blueprint('purchase_orders', __name__, url_prefix='/api')

@bp.route('/purchase-orders', methods=['GET'])
@login_required
def get_purchase_orders():
    days = request.args.get('days', type=int)
    
    query = PurchaseOrder.query
    
    if days:
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        query = query.filter(PurchaseOrder.purchase_date >= date_threshold)
    
    orders = query.all()
    return jsonify([o.to_dict() for o in orders])

@bp.route('/purchase-orders/<int:id>', methods=['GET'])
@login_required
def get_purchase_order(id):
    order = PurchaseOrder.query.get(id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({'error': 'Purchase order not found'}), 404

@bp.route('/purchase-orders', methods=['POST'])
@login_required
def create_purchase_order():
    data = request.get_json()
    
    product = Product.query.get(data.get('product_id'))
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    unit_price = data.get('unit_price')
    quantity = data.get('quantity')
    total_amount = unit_price * quantity if unit_price and quantity else None
    
    order = PurchaseOrder(
        customer_id=data.get('customer_id'),
        product_id=data.get('product_id'),
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    
    return jsonify(order.to_dict()), 201

@bp.route('/purchase-orders/<int:id>', methods=['PUT'])
@login_required
def update_purchase_order(id):
    order = PurchaseOrder.query.get(id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    
    old_quantity = order.quantity
    old_status = order.status
    data = request.get_json()
    
    if 'quantity' in data and old_status == 'completed':
        product = Product.query.get(order.product_id)
        if product:
            product.stock -= old_quantity
            product.stock += data['quantity']
    
    if 'status' in data and data['status'] == 'completed' and old_status == 'pending':
        product = Product.query.get(order.product_id)
        if product:
            product.stock += order.quantity
    
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

@bp.route('/purchase-orders/<int:id>', methods=['DELETE'])
@login_required
def delete_purchase_order(id):
    order = PurchaseOrder.query.get(id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    
    if order.status == 'completed':
        product = Product.query.get(order.product_id)
        if product:
            product.stock -= order.quantity
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Purchase order deleted successfully'})
