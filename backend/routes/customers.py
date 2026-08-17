from flask import Blueprint, request, jsonify
from extensions import db
from models.customer import Customer
from utils.auth import login_required

bp = Blueprint('customers', __name__, url_prefix='/api')

@bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@bp.route('/customers/<int:id>', methods=['GET'])
@login_required
def get_customer(id):
    customer = Customer.query.get(id)
    if customer:
        return jsonify(customer.to_dict())
    return jsonify({'error': 'Customer not found'}), 404

@bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    data = request.get_json()
    customer = Customer(
        name=data.get('name'),
        contact=data.get('contact'),
        phone=data.get('phone')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201

@bp.route('/customers/<int:id>', methods=['PUT'])
@login_required
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    if 'name' in data:
        customer.name = data['name']
    if 'contact' in data:
        customer.contact = data['contact']
    if 'phone' in data:
        customer.phone = data['phone']
    
    db.session.commit()
    return jsonify(customer.to_dict())

@bp.route('/customers/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})
