from extensions import db
from datetime import datetime

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.DECIMAL(10, 2))
    total_amount = db.Column(db.DECIMAL(12, 2))
    purchase_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')
    
    customer = db.relationship('Customer', backref=db.backref('purchase_orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('purchase_orders', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'purchase_date': self.purchase_date.isoformat(),
            'status': self.status
        }
