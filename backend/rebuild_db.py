from app import app, db
from models.user import User
from models.category import Category
from models.product import Product
from models.customer import Customer
from models.purchase_order import PurchaseOrder
from models.sales_order import SalesOrder
from models.invoice import Invoice
from datetime import datetime, timedelta

def to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

with app.app_context():
    # 删除所有现有数据
    print("正在删除现有数据...")
    
    # 删除所有表数据（先删除关联表）
    Invoice.query.delete()
    SalesOrder.query.delete()
    PurchaseOrder.query.delete()
    Product.query.delete()
    Category.query.delete()
    Customer.query.delete()
    User.query.delete()  # 添加用户表删除
    
    db.session.commit()
    print("现有数据已删除")
    
    # ==================== 用户数据 ====================
    # 创建默认管理员用户
    admin = User(username='admin')
    admin.set_password('123456')
    db.session.add(admin)
    
    # 创建其他用户
    zxy = User(username='zxy')
    zxy.set_password('zxy12345')
    db.session.add(zxy)
    
    test_users = ['manager', 'staff', 'guest', 'warehouse', 'accountant']
    for username in test_users:
        user = User(username=username)
        user.set_password(f'{username}123')
        db.session.add(user)
    
    db.session.commit()
    print("用户数据创建成功")
    
    # ==================== 商品类型数据（华为旗舰店模式）====================
    # 一级分类 - 先添加并提交以获取正确的ID
    cat_phone = Category(name='手机', parent_id=None)
    cat_tablet = Category(name='平板', parent_id=None)
    cat_computer = Category(name='电脑', parent_id=None)
    cat_accessories = Category(name='配件', parent_id=None)
    
    db.session.add_all([cat_phone, cat_tablet, cat_computer, cat_accessories])
    db.session.commit()
    
    # 二级分类 - 手机品牌
    cat_huawei_phone = Category(name='华为手机', parent_id=cat_phone.id)
    cat_apple_phone = Category(name='苹果手机', parent_id=cat_phone.id)
    cat_xiaomi_phone = Category(name='小米手机', parent_id=cat_phone.id)
    cat_samsung_phone = Category(name='三星手机', parent_id=cat_phone.id)
    
    # 二级分类 - 平板品牌
    cat_huawei_tablet = Category(name='华为平板', parent_id=cat_tablet.id)
    cat_apple_tablet = Category(name='苹果平板', parent_id=cat_tablet.id)
    
    # 二级分类 - 电脑类型
    cat_laptop = Category(name='笔记本电脑', parent_id=cat_computer.id)
    cat_desktop = Category(name='台式机', parent_id=cat_computer.id)
    
    # 二级分类 - 配件子分类
    cat_charger = Category(name='充电器', parent_id=cat_accessories.id)
    cat_powerbank = Category(name='充电宝', parent_id=cat_accessories.id)
    cat_adapter = Category(name='电源适配器', parent_id=cat_accessories.id)
    cat_headphone = Category(name='耳机', parent_id=cat_accessories.id)
    cat_cable = Category(name='数据线', parent_id=cat_accessories.id)
    
    db.session.add_all([
        cat_huawei_phone, cat_apple_phone, cat_xiaomi_phone, cat_samsung_phone,
        cat_huawei_tablet, cat_apple_tablet, cat_laptop, cat_desktop,
        cat_charger, cat_powerbank, cat_adapter, cat_headphone, cat_cable
    ])
    db.session.commit()
    
    # 三级分类 - 具体型号
    # 华为手机型号
    cat_mate60 = Category(name='Mate 60系列', parent_id=cat_huawei_phone.id)
    cat_mate50 = Category(name='Mate 50系列', parent_id=cat_huawei_phone.id)
    cat_pura80 = Category(name='Pura 80系列', parent_id=cat_huawei_phone.id)
    cat_pura70 = Category(name='Pura 70系列', parent_id=cat_huawei_phone.id)
    cat_nova13 = Category(name='Nova 13系列', parent_id=cat_huawei_phone.id)
    
    # 苹果手机型号
    cat_iphone15 = Category(name='iPhone 15系列', parent_id=cat_apple_phone.id)
    cat_iphone14 = Category(name='iPhone 14系列', parent_id=cat_apple_phone.id)
    
    # 小米手机型号
    cat_mi14 = Category(name='小米14系列', parent_id=cat_xiaomi_phone.id)
    cat_redmi_k80 = Category(name='红米K80系列', parent_id=cat_xiaomi_phone.id)
    
    # 三星手机型号
    cat_s24 = Category(name='Galaxy S24系列', parent_id=cat_samsung_phone.id)
    cat_note24 = Category(name='Galaxy Note24系列', parent_id=cat_samsung_phone.id)
    
    # 华为平板型号
    cat_matepad_pro = Category(name='MatePad Pro', parent_id=cat_huawei_tablet.id)
    cat_matepad_air = Category(name='MatePad Air', parent_id=cat_huawei_tablet.id)
    
    # 苹果平板型号
    cat_ipad_pro = Category(name='iPad Pro', parent_id=cat_apple_tablet.id)
    cat_ipad_air = Category(name='iPad Air', parent_id=cat_apple_tablet.id)
    cat_ipad_standard = Category(name='iPad', parent_id=cat_apple_tablet.id)
    
    # 笔记本电脑型号
    cat_matebook_x = Category(name='MateBook X系列', parent_id=cat_laptop.id)
    cat_matebook_d = Category(name='MateBook D系列', parent_id=cat_laptop.id)
    cat_macbook_pro = Category(name='MacBook Pro', parent_id=cat_laptop.id)
    cat_macbook_air = Category(name='MacBook Air', parent_id=cat_laptop.id)
    cat_thinkpad = Category(name='ThinkPad', parent_id=cat_laptop.id)
    
    # 充电器型号
    cat_huawei_66w = Category(name='华为66W充电器', parent_id=cat_charger.id)
    cat_huawei_40w = Category(name='华为40W充电器', parent_id=cat_charger.id)
    cat_huawei_22w = Category(name='华为22.5W充电器', parent_id=cat_charger.id)
    cat_apple_20w = Category(name='苹果20W充电器', parent_id=cat_charger.id)
    
    # 耳机型号
    cat_freebuds_pro = Category(name='FreeBuds Pro', parent_id=cat_headphone.id)
    cat_freebuds = Category(name='FreeBuds', parent_id=cat_headphone.id)
    cat_airpods = Category(name='AirPods', parent_id=cat_headphone.id)
    
    db.session.add_all([
        cat_mate60, cat_mate50, cat_pura80, cat_pura70, cat_nova13,
        cat_iphone15, cat_iphone14, cat_mi14, cat_redmi_k80, cat_s24, cat_note24,
        cat_matepad_pro, cat_matepad_air, cat_ipad_pro, cat_ipad_air, cat_ipad_standard,
        cat_matebook_x, cat_matebook_d, cat_macbook_pro, cat_macbook_air, cat_thinkpad,
        cat_huawei_66w, cat_huawei_40w, cat_huawei_22w, cat_apple_20w,
        cat_freebuds_pro, cat_freebuds, cat_airpods
    ])
    db.session.commit()
    print("商品类型数据创建成功（47个分类）")
    
    # ==================== 商品档案数据 ====================
    products = [
        # 华为手机 - Mate 60系列
        Product(name='华为 Mate 60 Pro 12GB+512GB', category_id=cat_mate60.id, unit='台', price=6999.00, stock=80),
        Product(name='华为 Mate 60 12GB+256GB', category_id=cat_mate60.id, unit='台', price=5499.00, stock=120),
        
        # 华为手机 - Mate 50系列
        Product(name='华为 Mate 50 Pro 8GB+256GB', category_id=cat_mate50.id, unit='台', price=4999.00, stock=60),
        Product(name='华为 Mate 50 8GB+128GB', category_id=cat_mate50.id, unit='台', price=3999.00, stock=90),
        
        # 华为手机 - Pura 80系列
        Product(name='华为 Pura 80 Ultra 12GB+512GB', category_id=cat_pura80.id, unit='台', price=8499.00, stock=35),
        Product(name='华为 Pura 80 Pro 12GB+256GB', category_id=cat_pura80.id, unit='台', price=5999.00, stock=70),
        Product(name='华为 Pura 80 12GB+256GB', category_id=cat_pura80.id, unit='台', price=4499.00, stock=100),
        
        # 华为手机 - Pura 70系列
        Product(name='华为 Pura 70 Ultra 12GB+512GB', category_id=cat_pura70.id, unit='台', price=7999.00, stock=50),
        Product(name='华为 Pura 70 Pro 12GB+256GB', category_id=cat_pura70.id, unit='台', price=5499.00, stock=85),
        
        # 华为手机 - Nova 13系列
        Product(name='华为 Nova 13 Pro 8GB+256GB', category_id=cat_nova13.id, unit='台', price=3999.00, stock=150),
        Product(name='华为 Nova 13 8GB+256GB', category_id=cat_nova13.id, unit='台', price=3299.00, stock=180),
        
        # 苹果手机 - iPhone 15系列
        Product(name='iPhone 15 Pro Max 256GB', category_id=cat_iphone15.id, unit='台', price=11999.00, stock=30),
        Product(name='iPhone 15 Pro 256GB', category_id=cat_iphone15.id, unit='台', price=9999.00, stock=50),
        Product(name='iPhone 15 256GB', category_id=cat_iphone15.id, unit='台', price=6999.00, stock=80),
        
        # 苹果手机 - iPhone 14系列
        Product(name='iPhone 14 Pro Max 256GB', category_id=cat_iphone14.id, unit='台', price=8999.00, stock=45),
        Product(name='iPhone 14 256GB', category_id=cat_iphone14.id, unit='台', price=5999.00, stock=90),
        
        # 小米手机
        Product(name='小米14 Ultra 16GB+512GB', category_id=cat_mi14.id, unit='台', price=6499.00, stock=40),
        Product(name='小米14 12GB+256GB', category_id=cat_mi14.id, unit='台', price=3999.00, stock=100),
        Product(name='红米K80 Pro 12GB+256GB', category_id=cat_redmi_k80.id, unit='台', price=3599.00, stock=120),
        
        # 三星手机
        Product(name='三星 Galaxy S24 Ultra 256GB', category_id=cat_s24.id, unit='台', price=11999.00, stock=25),
        Product(name='三星 Galaxy S24 256GB', category_id=cat_s24.id, unit='台', price=6499.00, stock=55),
        Product(name='三星 Galaxy Note24 Ultra 256GB', category_id=cat_note24.id, unit='台', price=12999.00, stock=20),
        
        # 华为平板
        Product(name='华为 MatePad Pro 12.2英寸 8GB+256GB', category_id=cat_matepad_pro.id, unit='台', price=4999.00, stock=60),
        Product(name='华为 MatePad Pro 11英寸 8GB+128GB', category_id=cat_matepad_pro.id, unit='台', price=3499.00, stock=80),
        Product(name='华为 MatePad Air 11.5英寸 8GB+256GB', category_id=cat_matepad_air.id, unit='台', price=3999.00, stock=70),
        
        # 苹果平板
        Product(name='iPad Pro 12.9英寸 256GB', category_id=cat_ipad_pro.id, unit='台', price=9299.00, stock=30),
        Product(name='iPad Pro 11英寸 256GB', category_id=cat_ipad_pro.id, unit='台', price=7299.00, stock=45),
        Product(name='iPad Air 11英寸 256GB', category_id=cat_ipad_air.id, unit='台', price=5499.00, stock=65),
        Product(name='iPad 10.9英寸 256GB', category_id=cat_ipad_standard.id, unit='台', price=4499.00, stock=90),
        
        # 笔记本电脑
        Product(name='华为 MateBook X Pro 2024 14.2英寸', category_id=cat_matebook_x.id, unit='台', price=11999.00, stock=25),
        Product(name='华为 MateBook D16 16英寸', category_id=cat_matebook_d.id, unit='台', price=5999.00, stock=50),
        Product(name='华为 MateBook D14 14英寸', category_id=cat_matebook_d.id, unit='台', price=4999.00, stock=60),
        Product(name='MacBook Pro 16英寸 M3 Pro', category_id=cat_macbook_pro.id, unit='台', price=19999.00, stock=20),
        Product(name='MacBook Pro 14英寸 M3', category_id=cat_macbook_pro.id, unit='台', price=12999.00, stock=35),
        Product(name='MacBook Air 15英寸 M3', category_id=cat_macbook_air.id, unit='台', price=9499.00, stock=45),
        Product(name='ThinkPad X1 Carbon Gen 12', category_id=cat_thinkpad.id, unit='台', price=12999.00, stock=25),
        
        # 充电器
        Product(name='华为 66W超级快充充电器', category_id=cat_huawei_66w.id, unit='个', price=199.00, stock=200),
        Product(name='华为 40W快充充电器', category_id=cat_huawei_40w.id, unit='个', price=149.00, stock=150),
        Product(name='华为 22.5W充电器', category_id=cat_huawei_22w.id, unit='个', price=99.00, stock=300),
        Product(name='Apple 20W USB-C充电器', category_id=cat_apple_20w.id, unit='个', price=149.00, stock=250),
        Product(name='Apple 35W双USB-C充电器', category_id=cat_apple_20w.id, unit='个', price=329.00, stock=100),
        
        # 充电宝
        Product(name='华为 12000mAh 66W超级快充移动电源', category_id=cat_powerbank.id, unit='个', price=399.00, stock=120),
        Product(name='华为 20000mAh 40W快充移动电源', category_id=cat_powerbank.id, unit='个', price=299.00, stock=150),
        Product(name='Anker 10000mAh 65W氮化镓移动电源', category_id=cat_powerbank.id, unit='个', price=279.00, stock=100),
        
        # 电源适配器
        Product(name='华为 MateBook 65W电源适配器', category_id=cat_adapter.id, unit='个', price=299.00, stock=80),
        Product(name='苹果 MacBook 67W USB-C电源适配器', category_id=cat_adapter.id, unit='个', price=399.00, stock=60),
        
        # 耳机
        Product(name='华为 FreeBuds Pro 3', category_id=cat_freebuds_pro.id, unit='副', price=1299.00, stock=60),
        Product(name='华为 FreeBuds 5', category_id=cat_freebuds.id, unit='副', price=899.00, stock=80),
        Product(name='华为 FreeBuds SE 3', category_id=cat_freebuds.id, unit='副', price=299.00, stock=200),
        Product(name='AirPods Pro 2', category_id=cat_airpods.id, unit='副', price=1899.00, stock=40),
        Product(name='AirPods 3', category_id=cat_airpods.id, unit='副', price=1399.00, stock=70),
        
        # 数据线
        Product(name='华为 6A快充数据线 1m', category_id=cat_cable.id, unit='条', price=69.00, stock=500),
        Product(name='华为 6A快充数据线 1.5m', category_id=cat_cable.id, unit='条', price=89.00, stock=300),
        Product(name='Apple Lightning数据线 1m', category_id=cat_cable.id, unit='条', price=149.00, stock=200),
        Product(name='USB-C转USB-C数据线 1m', category_id=cat_cable.id, unit='条', price=39.00, stock=400),
    ]
    
    db.session.add_all(products)
    db.session.commit()
    print("商品档案数据创建成功（60+种商品）")
    
    # ==================== 客户数据 ====================
    customers = [
        Customer(name='北京华为旗舰店', contact='张伟', phone='13800138001', address='北京市朝阳区建国路88号'),
        Customer(name='上海华为体验店', contact='李明', phone='13800138002', address='上海市浦东新区陆家嘴环路1000号'),
        Customer(name='广州华为授权店', contact='王强', phone='13800138003', address='广州市天河区天河路385号'),
        Customer(name='深圳华为旗舰店', contact='刘洋', phone='13800138004', address='深圳市南山区深南大道9999号'),
        Customer(name='杭州华为体验店', contact='陈静', phone='13800138005', address='杭州市西湖区延安路500号'),
        Customer(name='成都华为授权店', contact='赵丽', phone='13800138006', address='成都市高新区天府大道中段1号'),
        Customer(name='武汉华为旗舰店', contact='孙伟', phone='13800138007', address='武汉市江汉区解放大道688号'),
        Customer(name='南京华为体验店', contact='周芳', phone='13800138008', address='南京市鼓楼区中山北路201号'),
        Customer(name='苏州华为授权店', contact='吴涛', phone='13800138009', address='苏州市工业园区金鸡湖大道100号'),
        Customer(name='重庆华为旗舰店', contact='郑欣', phone='13800138010', address='重庆市渝中区解放碑步行街1号'),
    ]
    
    db.session.add_all(customers)
    db.session.commit()
    print("客户数据创建成功（10个客户）")
    
    # 获取商品数据用于创建订单
    products = Product.query.all()
    customers = Customer.query.all()
    
    # ==================== 采购订单数据 ====================
    purchase_orders = []
    
    # 2026年1月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=50, unit_price=6500.00, total_amount=325000.00, status='completed', purchase_date=to_date('2026-01-10')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[0].id, product_id=products[1].id, quantity=80, unit_price=5100.00, total_amount=408000.00, status='completed', purchase_date=to_date('2026-01-15')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[1].id, product_id=products[5].id, quantity=40, unit_price=5600.00, total_amount=224000.00, status='completed', purchase_date=to_date('2026-01-20')))
    
    # 2026年2月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[2].id, product_id=products[11].id, quantity=30, unit_price=11500.00, total_amount=345000.00, status='completed', purchase_date=to_date('2026-02-08')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[2].id, product_id=products[12].id, quantity=50, unit_price=9500.00, total_amount=475000.00, status='completed', purchase_date=to_date('2026-02-12')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[3].id, product_id=products[39].id, quantity=100, unit_price=180.00, total_amount=18000.00, status='completed', purchase_date=to_date('2026-02-20')))
    
    # 2026年3月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=40, unit_price=4700.00, total_amount=188000.00, status='completed', purchase_date=to_date('2026-03-05')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[4].id, product_id=products[23].id, quantity=60, unit_price=6900.00, total_amount=414000.00, status='completed', purchase_date=to_date('2026-03-15')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[5].id, product_id=products[36].id, quantity=25, unit_price=11500.00, total_amount=287500.00, status='completed', purchase_date=to_date('2026-03-25')))
    
    # 2026年4月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[6].id, product_id=products[0].id, quantity=60, unit_price=6500.00, total_amount=390000.00, status='completed', purchase_date=to_date('2026-04-10')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=80, unit_price=1150.00, total_amount=92000.00, status='completed', purchase_date=to_date('2026-04-18')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[7].id, product_id=products[45].id, quantity=100, unit_price=780.00, total_amount=78000.00, status='pending', purchase_date=to_date('2026-04-25')))
    
    # 2026年5月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[8].id, product_id=products[28].id, quantity=35, unit_price=6000.00, total_amount=210000.00, status='completed', purchase_date=to_date('2026-05-08')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[8].id, product_id=products[30].id, quantity=50, unit_price=4500.00, total_amount=225000.00, status='completed', purchase_date=to_date('2026-05-15')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=25, unit_price=11500.00, total_amount=287500.00, status='pending', purchase_date=to_date('2026-05-28')))
    
    # 2026年6月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=40, unit_price=6500.00, total_amount=260000.00, status='completed', purchase_date=to_date('2026-06-05')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[1].id, product_id=products[44].id, quantity=60, unit_price=1150.00, total_amount=69000.00, status='completed', purchase_date=to_date('2026-06-12')))
    
    # 2026年7月采购
    purchase_orders.append(PurchaseOrder(customer_id=customers[2].id, product_id=products[11].id, quantity=20, unit_price=11500.00, total_amount=230000.00, status='completed', purchase_date=to_date('2026-07-05')))
    purchase_orders.append(PurchaseOrder(customer_id=customers[3].id, product_id=products[39].id, quantity=150, unit_price=180.00, total_amount=27000.00, status='pending', purchase_date=to_date('2026-07-15')))
    
    db.session.add_all(purchase_orders)
    db.session.commit()
    print("采购订单数据创建成功（20条订单）")
    
    # ==================== 销售订单数据（2026年1月-7月）====================
    sales_orders = []
    
    # 2026年1月销售 - 约180万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=15, unit_price=6999.00, total_amount=104985.00, status='completed', sale_date=to_date('2026-01-05')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[1].id, quantity=25, unit_price=5499.00, total_amount=137475.00, status='completed', sale_date=to_date('2026-01-08')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[11].id, quantity=8, unit_price=11999.00, total_amount=95992.00, status='completed', sale_date=to_date('2026-01-10')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=12, unit_price=9999.00, total_amount=119988.00, status='completed', sale_date=to_date('2026-01-12')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[29].id, quantity=20, unit_price=4999.00, total_amount=99980.00, status='completed', sale_date=to_date('2026-01-15')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[34].id, quantity=5, unit_price=11999.00, total_amount=59995.00, status='completed', sale_date=to_date('2026-01-18')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[44].id, quantity=35, unit_price=899.00, total_amount=31465.00, status='completed', sale_date=to_date('2026-01-20')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[39].id, quantity=80, unit_price=199.00, total_amount=15920.00, status='completed', sale_date=to_date('2026-01-22')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[0].id, quantity=12, unit_price=6999.00, total_amount=83988.00, status='completed', sale_date=to_date('2026-01-25')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[23].id, quantity=15, unit_price=7299.00, total_amount=109485.00, status='completed', sale_date=to_date('2026-01-28')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[11].id, quantity=6, unit_price=11999.00, total_amount=71994.00, status='completed', sale_date=to_date('2026-01-30')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[45].id, quantity=45, unit_price=899.00, total_amount=40455.00, status='completed', sale_date=to_date('2026-01-31')))
    
    # 2026年2月销售 - 约220万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=18, unit_price=6999.00, total_amount=125982.00, status='completed', sale_date=to_date('2026-02-03')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[5].id, quantity=20, unit_price=5999.00, total_amount=119980.00, status='completed', sale_date=to_date('2026-02-06')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[11].id, quantity=10, unit_price=11999.00, total_amount=119990.00, status='completed', sale_date=to_date('2026-02-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[1].id, quantity=30, unit_price=5499.00, total_amount=164970.00, status='completed', sale_date=to_date('2026-02-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=15, unit_price=19999.00, total_amount=299985.00, status='completed', sale_date=to_date('2026-02-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=25, unit_price=4999.00, total_amount=124975.00, status='completed', sale_date=to_date('2026-02-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[44].id, quantity=40, unit_price=899.00, total_amount=35960.00, status='completed', sale_date=to_date('2026-02-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[34].id, quantity=8, unit_price=11999.00, total_amount=95992.00, status='completed', sale_date=to_date('2026-02-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=16, unit_price=6999.00, total_amount=111984.00, status='completed', sale_date=to_date('2026-02-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=22, unit_price=4999.00, total_amount=109978.00, status='completed', sale_date=to_date('2026-02-25')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=8, unit_price=11999.00, total_amount=95992.00, status='completed', sale_date=to_date('2026-02-28')))
    
    # 2026年3月销售 - 约280万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=22, unit_price=6999.00, total_amount=153978.00, status='completed', sale_date=to_date('2026-03-02')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[11].id, quantity=12, unit_price=11999.00, total_amount=143988.00, status='completed', sale_date=to_date('2026-03-05')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=20, unit_price=9999.00, total_amount=199980.00, status='completed', sale_date=to_date('2026-03-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[5].id, quantity=25, unit_price=5999.00, total_amount=149975.00, status='completed', sale_date=to_date('2026-03-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=20, unit_price=19999.00, total_amount=399980.00, status='completed', sale_date=to_date('2026-03-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=30, unit_price=4999.00, total_amount=149970.00, status='completed', sale_date=to_date('2026-03-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[34].id, quantity=10, unit_price=11999.00, total_amount=119990.00, status='completed', sale_date=to_date('2026-03-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=50, unit_price=899.00, total_amount=44950.00, status='completed', sale_date=to_date('2026-03-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=20, unit_price=6999.00, total_amount=139980.00, status='completed', sale_date=to_date('2026-03-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=28, unit_price=4999.00, total_amount=139972.00, status='completed', sale_date=to_date('2026-03-25')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=10, unit_price=11999.00, total_amount=119990.00, status='completed', sale_date=to_date('2026-03-28')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[39].id, quantity=100, unit_price=199.00, total_amount=19900.00, status='completed', sale_date=to_date('2026-03-30')))
    
    # 2026年4月销售 - 约320万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=25, unit_price=6999.00, total_amount=174975.00, status='completed', sale_date=to_date('2026-04-03')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[11].id, quantity=15, unit_price=11999.00, total_amount=179985.00, status='completed', sale_date=to_date('2026-04-06')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=25, unit_price=9999.00, total_amount=249975.00, status='completed', sale_date=to_date('2026-04-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[5].id, quantity=30, unit_price=5999.00, total_amount=179970.00, status='completed', sale_date=to_date('2026-04-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=25, unit_price=19999.00, total_amount=499975.00, status='completed', sale_date=to_date('2026-04-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=35, unit_price=4999.00, total_amount=174965.00, status='completed', sale_date=to_date('2026-04-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[34].id, quantity=12, unit_price=11999.00, total_amount=143988.00, status='completed', sale_date=to_date('2026-04-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=60, unit_price=899.00, total_amount=53940.00, status='completed', sale_date=to_date('2026-04-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=22, unit_price=6999.00, total_amount=153978.00, status='completed', sale_date=to_date('2026-04-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=32, unit_price=4999.00, total_amount=159968.00, status='completed', sale_date=to_date('2026-04-25')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=12, unit_price=11999.00, total_amount=143988.00, status='completed', sale_date=to_date('2026-04-28')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[45].id, quantity=80, unit_price=899.00, total_amount=71920.00, status='completed', sale_date=to_date('2026-04-30')))
    
    # 2026年5月销售 - 约380万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=28, unit_price=6999.00, total_amount=195972.00, status='completed', sale_date=to_date('2026-05-02')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[11].id, quantity=18, unit_price=11999.00, total_amount=215982.00, status='completed', sale_date=to_date('2026-05-05')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=30, unit_price=9999.00, total_amount=299970.00, status='completed', sale_date=to_date('2026-05-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[5].id, quantity=35, unit_price=5999.00, total_amount=209965.00, status='completed', sale_date=to_date('2026-05-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=30, unit_price=19999.00, total_amount=599970.00, status='completed', sale_date=to_date('2026-05-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=40, unit_price=4999.00, total_amount=199960.00, status='completed', sale_date=to_date('2026-05-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[34].id, quantity=15, unit_price=11999.00, total_amount=179985.00, status='completed', sale_date=to_date('2026-05-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=70, unit_price=899.00, total_amount=62930.00, status='completed', sale_date=to_date('2026-05-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=25, unit_price=6999.00, total_amount=174975.00, status='completed', sale_date=to_date('2026-05-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=38, unit_price=4999.00, total_amount=179962.00, status='completed', sale_date=to_date('2026-05-25')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=15, unit_price=11999.00, total_amount=179985.00, status='completed', sale_date=to_date('2026-05-28')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[45].id, quantity=90, unit_price=899.00, total_amount=80910.00, status='completed', sale_date=to_date('2026-05-31')))
    
    # 2026年6月销售 - 约420万
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=30, unit_price=6999.00, total_amount=209970.00, status='completed', sale_date=to_date('2026-06-02')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[11].id, quantity=20, unit_price=11999.00, total_amount=239980.00, status='completed', sale_date=to_date('2026-06-05')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=35, unit_price=9999.00, total_amount=349965.00, status='completed', sale_date=to_date('2026-06-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[5].id, quantity=40, unit_price=5999.00, total_amount=239960.00, status='completed', sale_date=to_date('2026-06-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=35, unit_price=19999.00, total_amount=699965.00, status='completed', sale_date=to_date('2026-06-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=45, unit_price=4999.00, total_amount=224955.00, status='completed', sale_date=to_date('2026-06-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[34].id, quantity=18, unit_price=11999.00, total_amount=215982.00, status='completed', sale_date=to_date('2026-06-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=80, unit_price=899.00, total_amount=71920.00, status='completed', sale_date=to_date('2026-06-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=28, unit_price=6999.00, total_amount=195972.00, status='completed', sale_date=to_date('2026-06-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=42, unit_price=4999.00, total_amount=209958.00, status='completed', sale_date=to_date('2026-06-25')))
    sales_orders.append(SalesOrder(customer_id=customers[9].id, product_id=products[11].id, quantity=18, unit_price=11999.00, total_amount=215982.00, status='completed', sale_date=to_date('2026-06-28')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[45].id, quantity=100, unit_price=899.00, total_amount=89900.00, status='completed', sale_date=to_date('2026-06-30')))
    
    # 2026年7月销售 - 约280万（截至中旬）
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[0].id, quantity=20, unit_price=6999.00, total_amount=139980.00, status='completed', sale_date=to_date('2026-07-02')))
    sales_orders.append(SalesOrder(customer_id=customers[0].id, product_id=products[11].id, quantity=12, unit_price=11999.00, total_amount=143988.00, status='completed', sale_date=to_date('2026-07-05')))
    sales_orders.append(SalesOrder(customer_id=customers[1].id, product_id=products[12].id, quantity=20, unit_price=9999.00, total_amount=199980.00, status='completed', sale_date=to_date('2026-07-08')))
    sales_orders.append(SalesOrder(customer_id=customers[2].id, product_id=products[5].id, quantity=25, unit_price=5999.00, total_amount=149975.00, status='completed', sale_date=to_date('2026-07-10')))
    sales_orders.append(SalesOrder(customer_id=customers[3].id, product_id=products[36].id, quantity=20, unit_price=19999.00, total_amount=399980.00, status='completed', sale_date=to_date('2026-07-12')))
    sales_orders.append(SalesOrder(customer_id=customers[4].id, product_id=products[22].id, quantity=30, unit_price=4999.00, total_amount=149970.00, status='completed', sale_date=to_date('2026-07-15')))
    sales_orders.append(SalesOrder(customer_id=customers[5].id, product_id=products[34].id, quantity=10, unit_price=11999.00, total_amount=119990.00, status='completed', sale_date=to_date('2026-07-18')))
    sales_orders.append(SalesOrder(customer_id=customers[6].id, product_id=products[44].id, quantity=50, unit_price=899.00, total_amount=44950.00, status='completed', sale_date=to_date('2026-07-20')))
    sales_orders.append(SalesOrder(customer_id=customers[7].id, product_id=products[0].id, quantity=18, unit_price=6999.00, total_amount=125982.00, status='pending', sale_date=to_date('2026-07-22')))
    sales_orders.append(SalesOrder(customer_id=customers[8].id, product_id=products[29].id, quantity=25, unit_price=4999.00, total_amount=124975.00, status='pending', sale_date=to_date('2026-07-25')))
    
    db.session.add_all(sales_orders)
    db.session.commit()
    print("销售订单数据创建成功（80条订单，2026年1-7月）")
    
    # ==================== 发票数据 ====================
    invoices = [
        Invoice(customer_id=customers[0].id, invoice_no='FP202601001', content='华为 Mate 60 Pro 15台', amount=104985.00, status='paid', issue_date='2026-01-10'),
        Invoice(customer_id=customers[1].id, invoice_no='FP202601002', content='iPhone 15 Pro Max 8台', amount=95992.00, status='paid', issue_date='2026-01-15'),
        Invoice(customer_id=customers[2].id, invoice_no='FP202602003', content='华为 Pura 80 Pro 20台', amount=119980.00, status='paid', issue_date='2026-02-10'),
        Invoice(customer_id=customers[3].id, invoice_no='FP202602004', content='MacBook Pro 15台', amount=299985.00, status='paid', issue_date='2026-02-20'),
        Invoice(customer_id=customers[4].id, invoice_no='FP202603005', content='华为 Mate 60 Pro 22台', amount=153978.00, status='paid', issue_date='2026-03-15'),
        Invoice(customer_id=customers[5].id, invoice_no='FP202603006', content='华为 MateBook X Pro 10台', amount=119990.00, status='unpaid', issue_date='2026-03-28'),
        Invoice(customer_id=customers[6].id, invoice_no='FP202604007', content='华为 Mate 60 Pro 25台', amount=174975.00, status='paid', issue_date='2026-04-15'),
        Invoice(customer_id=customers[7].id, invoice_no='FP202604008', content='小米14 Ultra 10台', amount=64990.00, status='unpaid', issue_date='2026-04-28'),
        Invoice(customer_id=customers[8].id, invoice_no='FP202605009', content='华为 Mate 60 Pro 28台', amount=195972.00, status='pending', issue_date='2026-05-15'),
        Invoice(customer_id=customers[9].id, invoice_no='FP202606010', content='iPhone 15 Pro Max 20台', amount=239980.00, status='pending', issue_date='2026-06-15'),
    ]
    
    db.session.add_all(invoices)
    db.session.commit()
    print("发票数据创建成功（10张发票）")
    
    print("\n数据库重构完成！")
    print("========================================")
    print("新数据概览：")
    print(f"• 用户: {User.query.count()} 个")
    print(f"• 商品类型: {Category.query.count()} 个")
    print(f"• 商品档案: {Product.query.count()} 种")
    print(f"• 客户: {Customer.query.count()} 个")
    print(f"• 采购订单: {PurchaseOrder.query.count()} 条")
    print(f"• 销售订单: {SalesOrder.query.count()} 条")
    print(f"• 发票: {Invoice.query.count()} 张")
    print("========================================")
