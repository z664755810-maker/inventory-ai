from extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    unit = db.Column(db.String(20))
    price = db.Column(db.DECIMAL(10, 2))
    stock = db.Column(db.Integer, default=0)
    
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'unit': self.unit,
            'price': float(self.price) if self.price else None,
            'stock': self.stock
        }
