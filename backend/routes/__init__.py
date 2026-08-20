from .users import bp as users_bp
from .categories import bp as categories_bp
from .products import bp as products_bp
from .customers import bp as customers_bp
from .purchase_orders import bp as purchase_orders_bp
from .sales_orders import bp as sales_orders_bp
from .stock import bp as stock_bp
from .invoices import bp as invoices_bp
from .agent import agent as agent_bp
from .backup import bp as backup_bp

# 导出蓝图供主应用使用
users = users_bp
categories = categories_bp
products = products_bp
customers = customers_bp
purchase_orders = purchase_orders_bp
sales_orders = sales_orders_bp
stock = stock_bp
invoices = invoices_bp
agent = agent_bp
backup = backup_bp
