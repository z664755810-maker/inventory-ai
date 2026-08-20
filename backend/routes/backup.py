"""演示数据导入导出路由（解决 Railway 临时容器导致的数据丢失问题）。

提供：
- GET  /api/admin/backup-export  下载完整数据备份 JSON（不含密码哈希）
- POST /api/admin/backup-import  上传之前的备份 JSON，恢复用户/业务数据
- GET  /api/admin/backup-stats   仅查看当前数据量统计

设计要点：
- 备份里不含 passwords 字段（出于安全），但导出时通过特殊机制可以恢复哈希；
  实际上导出包含 password_hash，导入时保留原哈希。导入会**先清空**所有表再插入。
- 备份文件由前端下载到浏览器本地（FileSaver），下次部署后上传恢复。
- 加了简单 IP 限流，防止恶意导入。
"""
import io
import json
from datetime import datetime

from flask import Blueprint, request, jsonify, send_file, Response

from extensions import db
from models import (
    User, Category, Product, Customer,
    SalesOrder, PurchaseOrder, Invoice
)
from utils.auth import login_required
from app import limiter


bp = Blueprint('admin_backup', __name__, url_prefix='/api/admin')


@bp.route('/backup-export', methods=['GET'])
@login_required
def export_backup():
    """导出完整业务数据为 JSON 下载文件。"""
    try:
        users = []
        for u in User.query.all():
            d = u.to_dict()
            # 包含 password_hash 用于恢复；前端下载后用户自行保管
            d['password_hash'] = u.password
            users.append(d)

        categories = [{
            'id': c.id, 'name': c.name, 'parent_id': c.parent_id
        } for c in Category.query.all()]

        products = [{
            'id': p.id, 'name': p.name, 'category_id': p.category_id,
            'unit': p.unit, 'price': float(p.price) if p.price else None,
            'stock': p.stock
        } for p in Product.query.all()]

        customers = [{
            'id': c.id, 'name': c.name, 'contact': c.contact,
            'phone': c.phone, 'address': c.address
        } for c in Customer.query.all()]

        sales_orders = [{
            'id': o.id, 'customer_id': o.customer_id, 'product_id': o.product_id,
            'quantity': o.quantity, 'unit_price': float(o.unit_price) if o.unit_price else None,
            'total_amount': float(o.total_amount) if o.total_amount else None,
            'sale_date': o.sale_date.isoformat() if o.sale_date else None,
            'status': o.status
        } for o in SalesOrder.query.all()]

        purchase_orders = [{
            'id': o.id, 'customer_id': o.customer_id, 'product_id': o.product_id,
            'quantity': o.quantity, 'unit_price': float(o.unit_price) if o.unit_price else None,
            'total_amount': float(o.total_amount) if o.total_amount else None,
            'purchase_date': o.purchase_date.isoformat() if o.purchase_date else None,
            'status': o.status
        } for o in PurchaseOrder.query.all()]

        backup = {
            '_meta': {
                'exported_at': datetime.now().isoformat(),
                'version': 1,
                'source': '义乌商品物流系统',
                'tables': {
                    'users': len(users),
                    'categories': len(categories),
                    'products': len(products),
                    'customers': len(customers),
                    'sales_orders': len(sales_orders),
                    'purchase_orders': len(purchase_orders),
                }
            },
            'users': users,
            'categories': categories,
            'products': products,
            'customers': customers,
            'sales_orders': sales_orders,
            'purchase_orders': purchase_orders,
        }

        data = json.dumps(backup, ensure_ascii=False, indent=2)
        filename = f'inventory-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        return Response(
            data,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/json; charset=utf-8'
            }
        )
    except Exception as e:
        return jsonify({'error': f'导出失败：{str(e)}'}), 500


@bp.route('/backup-stats', methods=['GET'])
@login_required
def backup_stats():
    """查看当前各表数据量。"""
    try:
        return jsonify({
            'users': User.query.count(),
            'categories': Category.query.count(),
            'products': Product.query.count(),
            'customers': Customer.query.count(),
            'sales_orders': SalesOrder.query.count(),
            'purchase_orders': PurchaseOrder.query.count(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/backup-import', methods=['POST'])
@limiter.limit('5 per hour')
@login_required
def import_backup():
    """导入备份 JSON，恢复业务数据。**危险操作**，会清空当前表。"""
    try:
        payload = request.get_json(force=True, silent=False)
        if not isinstance(payload, dict):
            return jsonify({'error': '备份文件格式错误（不是 JSON 对象）'}), 400

        if '_meta' not in payload:
            return jsonify({'error': '备份文件格式错误（缺少 _meta 字段）'}), 400

        # 二次确认保护：必须传 confirm: true
        if not payload.get('confirm'):
            return jsonify({
                'error': '必须显式确认（confirm=true）才能执行导入，会清空当前所有业务数据',
                'preview': payload.get('_meta', {}).get('tables', {})
            }), 400

        # 清空表（按外键反序）
        try:
            Invoice.query.delete()
            SalesOrder.query.delete()
            PurchaseOrder.query.delete()
            Customer.query.delete()
            Product.query.delete()
            Category.query.delete()
            User.query.delete()
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'清表失败：{str(e)}'}), 500

        inserted = {'users': 0, 'categories': 0, 'products': 0,
                    'customers': 0, 'sales_orders': 0, 'purchase_orders': 0}

        try:
            # 用户
            for u in payload.get('users', []):
                user = User(id=u['id'], username=u['username'])
                user.password = u.get('password_hash') or ''
                # 如密码哈希缺失或 bcrypt 不识别，强制重置密码为 admin123
                if not user.password or not user.password.startswith('$2'):
                    user.set_password('admin123')
                db.session.add(user)
                inserted['users'] += 1

            # 分类
            for c in payload.get('categories', []):
                cat = Category(id=c['id'], name=c['name'], parent_id=c.get('parent_id'))
                db.session.add(cat)
                inserted['categories'] += 1

            # 商品
            for p in payload.get('products', []):
                prod = Product(id=p['id'], name=p['name'],
                               category_id=p.get('category_id'),
                               unit=p.get('unit'),
                               price=p.get('price'),
                               stock=p.get('stock', 0))
                db.session.add(prod)
                inserted['products'] += 1

            # 客户
            for c in payload.get('customers', []):
                cust = Customer(id=c['id'], name=c['name'],
                                contact=c.get('contact'), phone=c.get('phone'),
                                address=c.get('address'))
                db.session.add(cust)
                inserted['customers'] += 1

            # 销售单
            for o in payload.get('sales_orders', []):
                order = SalesOrder(id=o['id'],
                                   customer_id=o.get('customer_id'),
                                   product_id=o.get('product_id'),
                                   quantity=o.get('quantity'),
                                   unit_price=o.get('unit_price'),
                                   total_amount=o.get('total_amount'),
                                   sale_date=datetime.fromisoformat(o['sale_date']) if o.get('sale_date') else None,
                                   status=o.get('status'))
                db.session.add(order)
                inserted['sales_orders'] += 1

            # 采购单
            for o in payload.get('purchase_orders', []):
                order = PurchaseOrder(id=o['id'],
                                      customer_id=o.get('customer_id'),
                                      product_id=o.get('product_id'),
                                      quantity=o.get('quantity'),
                                      unit_price=o.get('unit_price'),
                                      total_amount=o.get('total_amount'),
                                      purchase_date=datetime.fromisoformat(o['purchase_date']) if o.get('purchase_date') else None,
                                      status=o.get('status'))
                db.session.add(order)
                inserted['purchase_orders'] += 1

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'导入失败，已回滚：{str(e)}'}), 500

        return jsonify({'message': '导入成功', 'inserted': inserted})
    except Exception as e:
        return jsonify({'error': f'请求处理失败：{str(e)}'}), 500
