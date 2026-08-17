from app import app, db

with app.app_context():
    # 添加address列到customers表
    from sqlalchemy import text
    try:
        db.session.execute(text('ALTER TABLE customers ADD COLUMN address VARCHAR(200)'))
        db.session.commit()
        print("Successfully added address column to customers table")
    except Exception as e:
        print(f"Error adding address column: {e}")
    
    # 添加status列到purchase_orders表
    try:
        db.session.execute(text("ALTER TABLE purchase_orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
        db.session.commit()
        print("Successfully added status column to purchase_orders table")
    except Exception as e:
        print(f"Error adding status column to purchase_orders: {e}")
    
    # 添加status列到sales_orders表
    try:
        db.session.execute(text("ALTER TABLE sales_orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
        db.session.commit()
        print("Successfully added status column to sales_orders table")
    except Exception as e:
        print(f"Error adding status column to sales_orders: {e}")
    
    # 添加customer_id列到invoices表
    try:
        db.session.execute(text('ALTER TABLE invoices ADD COLUMN customer_id INTEGER'))
        db.session.commit()
        print("Successfully added customer_id column to invoices table")
    except Exception as e:
        print(f"Error adding customer_id column to invoices: {e}")
    
    # 添加status列到invoices表
    try:
        db.session.execute(text("ALTER TABLE invoices ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
        db.session.commit()
        print("Successfully added status column to invoices table")
    except Exception as e:
        print(f"Error adding status column to invoices: {e}")
    
    # 添加issue_date列到invoices表
    try:
        db.session.execute(text('ALTER TABLE invoices ADD COLUMN issue_date VARCHAR(20)'))
        db.session.commit()
        print("Successfully added issue_date column to invoices table")
    except Exception as e:
        print(f"Error adding issue_date column to invoices: {e}")
