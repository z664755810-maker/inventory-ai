"""AI 智能体路由（统一多面手版）。

原版有 4 个 agent_type（general/inventory/sales/report），前端切换 tab 体验冗余。
v2 简化：
- 只有一个智能体"业务智能助手"，覆盖库存/销售/报表
- 后端意图路由仍在（让模型拿到正确的数据），但不再有"角色概念"
- 前端不再接受 agent_type 入参（向后兼容：忽略）
"""
import re
from datetime import datetime

from flask import Blueprint, request, jsonify

from models.product import Product
from models.category import Category
from models.customer import Customer
from models.sales_order import SalesOrder
from models.purchase_order import PurchaseOrder
from models.invoice import Invoice
from routes.stock import get_stock_data
from llm import ask_llm
from config import Config

agent = Blueprint('agent', __name__)


# ---------- 1. 意图识别（路由到正确的数据工具）----------
def analyze_intent(message):
    """根据用户问题关键字路由到对应的数据抓取函数。"""
    message_lower = message.lower()
    if any(k in message_lower for k in ['库存', '存货', 'stock', '预警', '盘点', '仓库', '种类', '多少件', '种类数']):
        return 'inventory'
    if any(k in message_lower for k in ['销售', 'sales', '订单', '客户', '购买', '排行', '热门', 'top']):
        return 'sales'
    if any(k in message_lower for k in ['报表', '分析', '统计', '趋势', '数据', '日报', '月报', '利润', '今日']):
        return 'report'
    return 'general'


# ---------- 2. 数据抓取（真实查询数据库，喂给大模型）----------
def gather_inventory_data():
    stock = get_stock_data()
    threshold = Config.AGENT_INVENTORY_THRESHOLD
    low = [i for i in stock if i['stock'] < threshold]
    return {
        'threshold': threshold,
        'total': len(stock),
        'total_stock': sum(i['stock'] for i in stock),
        'low_stock_count': len(low),
        'low_stock': low[:10],
    }


def gather_sales_data():
    orders = SalesOrder.query.all()
    stock = get_stock_data()
    product_sales = {}
    for o in orders:
        name = next((i['product_name'] for i in stock if i['product_id'] == o.product_id),
                    f'商品{o.product_id}')
        product_sales[name] = product_sales.get(name, 0) + (o.quantity or 0)
    top = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        'order_count': len(orders),
        'total_amount': float(sum(o.total_amount or 0 for o in orders)),
        'top_products': [{'name': n, 'qty': q} for n, q in top],
    }


def gather_report_data():
    today = datetime.now().strftime('%Y-%m-%d')
    sales = SalesOrder.query.filter(SalesOrder.sale_date.like(f'{today}%')).all()
    purchases = PurchaseOrder.query.filter(PurchaseOrder.purchase_date.like(f'{today}%')).all()
    invoices = Invoice.query.filter(Invoice.invoice_date.like(f'{today}%')).all()
    total_sales = sum(o.total_amount or 0 for o in sales)
    total_purchase = sum(o.total_amount or 0 for o in purchases)
    return {
        'date': today,
        'sales_count': len(sales),
        'sales_amount': float(total_sales),
        'purchase_count': len(purchases),
        'purchase_amount': float(total_purchase),
        'invoice_count': len(invoices),
        'profit': float(total_sales - total_purchase),
    }


def gather_overview_data():
    """聚合三类数据，一次性提供给 LLM，避免用户问综合问题时漏数据。"""
    return {
        'inventory': gather_inventory_data(),
        'sales': gather_sales_data(),
        'today_report': gather_report_data(),
    }


# ---------- 3. 离线兜底（无 Key / 调用失败时使用）----------
def fallback_response(intent, message, data):
    """根据意图和数据返回规则答案，用于 LLM 不可用时。"""
    if intent == 'inventory':
        d = data if isinstance(data, dict) and 'total' in data else {}
        if d.get('low_stock_count', 0) > 0:
            lines = '\n'.join(f"• {i['product_name']}: {i['stock']} {i['unit']}"
                              for i in d['low_stock'])
            return (f"⚠️ 库存低于{d['threshold']}件的商品共{d['low_stock_count']}种：\n{lines}"
                    f"\n（离线模式：未配置大模型，已用本地规则生成答复）")
        return f"✅ 当前无库存低于{d['threshold']}件的商品，共{d['total']}种。"

    if intent == 'sales':
        d = data if isinstance(data, dict) and 'order_count' in data else {}
        top = '\n'.join(f"{i + 1}. {p['name']}: {p['qty']}件"
                        for i, p in enumerate(d.get('top_products', [])[:5])) or '暂无销售数据'
        return (f"📈 销售订单{d.get('order_count', 0)}单，销售额¥{d.get('total_amount', 0):.2f}。\n"
                f"热销 TOP：\n{top}\n（离线模式）")

    if intent == 'report':
        d = data if isinstance(data, dict) and 'date' in data else {}
        return (f"📊 {d.get('date', '')} 经营日报：销售{d.get('sales_count', 0)}单/¥{d.get('sales_amount', 0):.2f}，"
                f"采购{d.get('purchase_count', 0)}单/¥{d.get('purchase_amount', 0):.2f}，"
                f"毛利¥{d.get('profit', 0):.2f}。（离线模式）")

    return f"（离线模式）已收到您的问题：{message}。系统将基于业务数据作答，当前大模型未配置，已返回本地摘要。"


# ---------- 4. 提示词构造 ----------
FIELD_LABELS = {
    'total': '商品种类数（即"多少种商品"）',
    'total_stock': '所有商品的总库存件数（即"总共多少件"）',
    'threshold': '库存预警阈值',
    'low_stock_count': '低于阈值的商品种类数',
    'low_stock': '低于阈值的商品清单',
    'order_count': '销售订单总单数',
    'total_amount': '销售总额',
    'top_products': '热销商品排行',
    'date': '统计日期',
    'sales_count': '当日销售单数',
    'sales_amount': '当日销售额',
    'purchase_count': '当日采购单数',
    'purchase_amount': '当日采购额',
    'invoice_count': '当日发票数',
    'profit': '当日毛利（销售额-采购额）',
    'inventory': '库存概览',
    'sales': '销售概览',
    'today_report': '今日经营日报',
}


def _format_data_for_prompt(data):
    """把 dict 渲染成 bullet 列表，便于小模型直接读取字段。"""
    lines = []
    for key, value in data.items():
        label = FIELD_LABELS.get(key, key)
        if isinstance(value, list):
            if not value:
                lines.append(f"- {label}：（空）")
            else:
                lines.append(f"- {label}：")
                for item in value[:5]:
                    if isinstance(item, dict):
                        sub = '，'.join(
                            f"{ik}={iv}" for ik, iv in item.items()
                            if not str(ik).endswith('_id')
                        )
                        lines.append(f"  · {sub}")
        elif isinstance(value, dict):
            lines.append(f"- {label}：")
            for sub_k, sub_v in value.items():
                sub_label = FIELD_LABELS.get(sub_k, sub_k)
                if isinstance(sub_v, (int, float, str)):
                    lines.append(f"  · {sub_label}：{sub_v}")
                elif isinstance(sub_v, list):
                    lines.append(f"  · {sub_label}：{len(sub_v)} 项")
                else:
                    lines.append(f"  · {sub_label}：{type(sub_v).__name__}")
        else:
            lines.append(f"- {label}：{value}")
    return '\n'.join(lines)


def build_system_prompt():
    """统一多面手 system prompt：覆盖库存/销售/报表三类问题。"""
    return ("你是「京东电子商品物流系统」的智能助手，负责回答用户关于库存、销售、报表的问题。\n"
            "你的任务：根据下方【业务数据】回答【用户问题】。\n"
            "严格要求：\n"
            "1. 必须从【业务数据】里提取具体数字或名称放进回答，禁止编造。\n"
            "2. 区分语义：问『多少商品/多少种』→ 用商品种类数（total）；"
            "问『多少件/总量/总库存』→ 用总库存件数（total_stock）；"
            "问『今天/今日/日报』→ 看 today_report 子表。\n"
            "3. 禁止回答『暂无相关数据』『问题为空』『未提供』等套话——"
            "只要【业务数据】有任何字段，就用它来回答。\n"
            "4. 回答用简洁中文，可使用 emoji 与条目排版。")


def build_user_prompt(message, data):
    formatted = _format_data_for_prompt(data)
    return (f"【用户问题】\n{message}\n\n"
            f"【业务数据】（下面每一行都是可以直接引用的真实业务数据）\n{formatted}\n\n"
            f"请根据上面【业务数据】直接回答【用户问题】，必须包含其中的具体数字。")


# ---------- 5. 鲁棒性：防呆（检测 LLM 幻觉）----------
LLM_HALLUCINATION_KEYWORDS = (
    '问题内容为空', '问题为空', '未提供具体内容', '未提供具体问题',
    '未提供具体', '没有提供具体', '未输入', '未给出具体',
)


def _looks_like_hallucination(text):
    if not text:
        return True
    return any(kw in text for kw in LLM_HALLUCINATION_KEYWORDS)


# ---------- 6. 路由 ----------
@agent.route('/api/agent/query', methods=['POST'])
def query_agent():
    """统一智能体入口（向后兼容 agent_type 入参但忽略）。"""
    try:
        data = request.get_json(silent=True) or {}
        # 向后兼容：忽略前端可能仍传来的 agent_type
        # _ = data.get('agent_type')
        message = data.get('message', '')
        if not message:
            return jsonify({'success': False, 'error': '请输入问题'}), 400

        intent = analyze_intent(message)
        if intent == 'inventory':
            payload = gather_inventory_data()
        elif intent == 'sales':
            payload = gather_sales_data()
        elif intent == 'report':
            payload = gather_report_data()
        else:
            payload = gather_overview_data()

        llm_text = ask_llm(
            build_system_prompt(),
            build_user_prompt(message, payload),
        )

        if llm_text is None:
            llm_text = fallback_response(intent, message, payload)
            source = 'rule'
        elif _looks_like_hallucination(llm_text):
            llm_text = fallback_response(intent, message, payload)
            source = 'rule-fallback'
        else:
            source = 'llm'

        return jsonify({
            'success': True,
            'response': llm_text,
            'intent': intent,
            'source': source,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as exc:  # noqa: BLE001
        return jsonify({'success': False, 'error': str(exc)}), 500