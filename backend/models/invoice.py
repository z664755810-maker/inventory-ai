from extensions import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_no = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    amount = db.Column(db.DECIMAL(12, 2))
    invoice_date = db.Column(db.DateTime, default=datetime.now)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    status = db.Column(db.String(20), default='pending')
    issue_date = db.Column(db.String(20))
    
    customer = db.relationship('Customer', backref=db.backref('invoices', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_no': self.invoice_no,
            'content': self.content,
            'amount': float(self.amount) if self.amount else None,
            'invoice_date': self.invoice_date.isoformat(),
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'status': self.status,
            'issue_date': self.issue_date
        }
