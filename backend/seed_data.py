"""一键初始化演示数据：默认管理员 / 分类 / 商品 / 客户 / 销售订单。

设计要点：
- 幂等：仅在 products 表为空时才会写入，重复运行不会重复插入。
- 与 Railway 自动部署配合：app.py 启动时调用 seed_if_empty()，
  解决临时容器里 SQLite 是空库、导致 LLM 拿不到数据的问题。
- 默认管理员：演示账号 admin / admin（密码 bcrypt 哈希存储）。
  Railway 容器重启会清空 SQLite，必须靠 seed 重建管理员账号。
"""
from datetime import datetime, timedelta

from extensions import db
from models.category import Category
from models.product import Product
from models.customer import Customer
from models.sales_order import SalesOrder
from models.user import User


DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'


def _ensure_default_admin():
    """确保存在默认管理员账号（演示用）。

    Railway 容器重启 SQLite 重置后，管理员账号会丢失。这里在 seed
    阶段自动创建一个 admin/admin 账号，业务演示不必手动注册。
    密码经 bcrypt 哈希后存储。
    """
    if User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first():
        return False
    admin = User(username=DEFAULT_ADMIN_USERNAME)
    admin.set_password(DEFAULT_ADMIN_PASSWORD)
    db.session.add(admin)
    return True


def _build_categories():
    """返回 (分类名 -> 实例) 映射，方便后续商品关联。"""
    catalog = {
        '办公文具': None,
        '数码电子': None,
        '家用电器': None,
        '仓储耗材': None,
    }
    for name in catalog:
        cat = Category(name=name)
        db.session.add(cat)
        db.session.flush()  # 拿到 id 供商品外键使用
        catalog[name] = cat
    return catalog


def _build_products(catalog):
    """15 个商品，覆盖 4 个分类，含 5 个低于库存阈值(50)的预警品。"""
    specs = [
        # (名称, 分类key, 单位, 单价, 库存)
        ('A4 打印纸 70g 500张/包', '办公文具', '包', 25.00, 120),
        ('中性笔 0.5mm 黑色', '办公文具', '支', 2.50, 35),      # 预警
        ('文件夹 双夹 A4', '办公文具', '个', 8.00, 60),
        ('笔记本 软皮 80页', '办公文具', '本', 6.50, 45),       # 预警
        ('无线机械键盘', '数码电子', '个', 199.00, 80),
        ('人体工学鼠标', '数码电子', '个', 89.00, 30),          # 预警
        ('USB-C 扩展坞 7合1', '数码电子', '个', 159.00, 55),
        ('4K 高清网络摄像头', '数码电子', '个', 249.00, 40),
        ('蓝牙耳机 入耳式', '数码电子', '副', 129.00, 90),
        ('电热水壶 1.7L', '家用电器', '台', 79.00, 25),         # 预警
        ('桌面加湿器', '家用电器', '台', 99.00, 70),
        ('LED 护眼台灯', '家用电器', '台', 69.00, 50),
        ('瓦楞纸箱 中号 40*30*30', '仓储耗材', '个', 3.20, 200),
        ('气泡膜 50cm 宽/卷', '仓储耗材', '卷', 15.00, 150),
        ('封箱胶带 透明 60mm', '仓储耗材', '卷', 4.50, 300),
    ]
    products = []
    for name, cat_key, unit, price, stock in specs:
        p = Product(
            name=name,
            category_id=catalog[cat_key].id,
            unit=unit,
            price=price,
            stock=stock,
        )
        db.session.add(p)
        products.append(p)
    db.session.flush()
    return products


def _build_customers():
    customers = [
        Customer(name='北京启航科技', contact='王经理', phone='13800001111', address='北京市海淀区中关村南大街 5 号'),
        Customer(name='上海云图贸易', contact='李女士', phone='13900002222', address='上海市浦东新区世纪大道 100 号'),
        Customer(name='广州恒达办公', contact='陈先生', phone='13700003333', address='广州市天河区珠江新城 88 号'),
        Customer(name='深圳锐捷电子', contact='赵工', phone='13600004444', address='深圳市南山区科技园 12 栋'),
        Customer(name='成都锦城文具', contact='周店长', phone='13500005555', address='成都市武侯区人民南路 66 号'),
    ]
    for c in customers:
        db.session.add(c)
    db.session.flush()
    return customers


def _build_sales_orders(products, customers):
    """12 条订单，日期分布在本月，便于「今日/报表」类问题有数据。"""
    today = datetime.now()
    order_specs = [
        # (商品索引, 客户索引, 数量, 天数前)
        (0, 0, 20, 0),
        (4, 3, 5, 0),
        (5, 1, 8, 1),
        (12, 2, 50, 2),
        (10, 4, 3, 3),
        (6, 0, 4, 5),
        (8, 3, 10, 7),
        (1, 1, 60, 9),
        (14, 2, 40, 12),
        (3, 4, 15, 15),
        (11, 0, 2, 20),
        (7, 3, 6, 25),
    ]
    for p_idx, c_idx, qty, days_ago in order_specs:
        product = products[p_idx]
        customer = customers[c_idx]
        unit_price = float(product.price)
        order = SalesOrder(
            customer_id=customer.id,
            product_id=product.id,
            quantity=qty,
            unit_price=unit_price,
            total_amount=round(unit_price * qty, 2),
            sale_date=today - timedelta(days=days_ago),
            status='completed' if days_ago > 0 else 'pending',
        )
        db.session.add(order)


def seed_if_empty():
    """若 products 表为空则初始化演示数据；否则只确保默认管理员存在。

    - 第一次启动：products 空 → seed 全部演示数据 + 默认管理员
    - 后续启动：products 有数据 → 跳过演示数据但仍保证管理员存在
      （Railway 容器重启后 SQLite 被清，products 也是空的，会重新 seed）
    """
    admin_created = _ensure_default_admin()

    if Product.query.count() > 0:
        if admin_created:
            db.session.commit()
            print('[seed] 检测到已有业务数据，已补建默认管理员账号 admin/admin')
        else:
            print('[seed] 检测到已有数据，跳过初始化')
        return admin_created

    catalog = _build_categories()
    products = _build_products(catalog)
    customers = _build_customers()
    _build_sales_orders(products, customers)

    db.session.commit()
    print('[seed] 初始化完成：4 分类 / 15 商品 / 5 客户 / 12 订单 / 默认管理员 admin/admin')
    return True


if __name__ == '__main__':
    # 本地手动运行：python seed_data.py
    from app import app
    with app.app_context():
        seed_if_empty()
