from flask import Blueprint, request, jsonify
from extensions import db
from models.invoice import Invoice
from utils.auth import login_required

bp = Blueprint('invoices', __name__, url_prefix='/api')

@bp.route('/invoices', methods=['GET'])
@login_required
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify([i.to_dict() for i in invoices])

@bp.route('/invoices/<int:id>', methods=['GET'])
@login_required
def get_invoice(id):
    invoice = Invoice.query.get(id)
    if invoice:
        return jsonify(invoice.to_dict())
    return jsonify({'error': 'Invoice not found'}), 404

@bp.route('/invoices', methods=['POST'])
@login_required
def create_invoice():
    data = request.get_json()
    invoice = Invoice(
        invoice_no=data.get('invoice_no'),
        content=data.get('content'),
        amount=data.get('amount')
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify(invoice.to_dict()), 201

@bp.route('/invoices/<int:id>', methods=['PUT'])
@login_required
def update_invoice(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    data = request.get_json()
    if 'invoice_no' in data:
        invoice.invoice_no = data['invoice_no']
    if 'content' in data:
        invoice.content = data['content']
    if 'amount' in data:
        invoice.amount = data['amount']
    
    db.session.commit()
    return jsonify(invoice.to_dict())

@bp.route('/invoices/<int:id>', methods=['DELETE'])
@login_required
def delete_invoice(id):
    invoice = Invoice.query.get(id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({'message': 'Invoice deleted successfully'})
