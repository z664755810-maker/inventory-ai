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

AGENT_CONFIGS = {
    'general': {
        'name': '通用助手',
        'icon': '🎯',
        'description': '综合智能助手，提供全面的业务支持',
    },
    'inventory': {
        'name': '库存专家',
        'icon': '📦',
        'description': '专业库存管理咨询',
    },
    'sales': {
        'name': '销售顾问',
        'icon': '📈',
        'description': '销售数据分析与建议',
    },
    'report': {
        'name': '报表分析',
        'icon': '📊',
        'description': '深度业务报表分析',
    },
}

AGENT_CONTEXT = {
    'inventory_threshold': Config.AGENT_INVENTORY_THRESHOLD,
    'last_query_time': None,
    'last_agent_type': 'general',
}


# ---------- 1. 意图识别（路由到正确的数据工具）----------
def analyze_intent(message):
    message_lower = message.lower()
    if any(k in message_lower for k in ['库存', '存货', 'stock', '预警', '盘点', '仓库']):
        return 'inventory'
    if any(k in message_lower for k in ['销售', 'sales', '订单', '客户', '购买', '排行', '热门']):
        return 'sales'
    if any(k in message_lower for k in ['报表', '分析', '统计', '趋势', '数据', '日报', '月报', '利润']):
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


# ---------- 3. 离线兜底（无 Key / 调用失败时使用）----------
def fallback_response(agent_type, message, data):
    if agent_type == 'inventory' or '库存' in message or '预警' in message:
        d = data
        if d['low_stock_count'] > 0:
            lines = '\n'.join(f"• {i['product_name']}: {i['stock']} {i['unit']}"
                              for i in d['low_stock'])
            return (f"⚠️ 库存低于{d['threshold']}件的商品共{d['low_stock_count']}种：\n{lines}"
                    f"\n（离线模式：未配置大模型，已用本地规则生成答复）")
        return f"✅ 当前无库存低于{d['threshold']}件的商品，共{d['total']}种。"
    if agent_type == 'sales' or '销售' in message:
        d = data
        top = '\n'.join(f"{i + 1}. {p['name']}: {p['qty']}件"
                        for i, p in enumerate(d['top_products'][:5])) or '暂无销售数据'
        return (f"📈 销售订单{d['order_count']}单，销售额¥{d['total_amount']:.2f}。\n"
                f"热销 TOP：\n{top}\n（离线模式）")
    if agent_type == 'report' or '报表' in message or '利润' in message:
        d = data
        return (f"📊 {d['date']} 经营日报：销售{d['sales_count']}单/¥{d['sales_amount']:.2f}，"
                f"采购{d['purchase_count']}单/¥{d['purchase_amount']:.2f}，毛利¥{d['profit']:.2f}。"
                f"（离线模式）")
    return f"（离线模式）已收到您的问题：{message}。系统将基于业务数据作答，当前大模型未配置，已返回本地摘要。"


# ---------- 4. 提示词构造 ----------
def _format_data_for_prompt(data):
    """把 dict 渲染成 bullet 列表，便于小模型直接读取字段。

    小模型对 JSON 嵌套结构解析能力弱，把它平铺成「字段：值」更可靠。
    """
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"- {key}：（空）")
            else:
                lines.append(f"- {key}：")
                for item in value[:5]:
                    if isinstance(item, dict):
                        sub = '，'.join(
                            f"{ik}={iv}" for ik, iv in item.items()
                            if not str(ik).endswith('_id')
                        )
                        lines.append(f"  · {sub}")
        else:
            lines.append(f"- {key}：{value}")
    return '\n'.join(lines)


def build_system_prompt(agent_type):
    role = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS['general'])['description']
    return (f"你是京东电子商品物流系统的智能助手（{role}）。\n"
            f"你的任务：根据下方【业务数据】回答【用户问题】。\n"
            f"严格要求：\n"
            f"1. 必须从【业务数据】里提取具体数字或名称放进回答。\n"
            f"2. 禁止回答『暂无相关数据』『问题为空』『未提供』等套话——只要【业务数据】有任何字段，就用它来回答。\n"
            f"3. 回答用简洁中文，可使用 emoji 与条目排版。")


def build_user_prompt(agent_type, message, data):
    formatted = _format_data_for_prompt(data)
    return (f"【用户问题】\n{message}\n\n"
            f"【业务数据】（下面每一行都是可以直接引用的真实业务数据）\n{formatted}\n\n"
            f"请根据上面【业务数据】直接回答【用户问题】，必须包含其中的具体数字。")


# ---------- 5.5. 防呆：小模型幻觉检测 ----------
LLM_HALLUCINATION_KEYWORDS = (
    '问题内容为空', '问题为空', '未提供具体内容', '未提供具体问题',
    '未提供具体', '没有提供具体', '未输入', '未给出具体',
)


def _looks_like_hallucination(text):
    if not text:
        return True
    return any(kw in text for kw in LLM_HALLUCINATION_KEYWORDS)


# ---------- 6. 路由 ----------
@agent.route('/api/agent/configs', methods=['GET'])
def get_agent_configs():
    return jsonify({'success': True, 'configs': AGENT_CONFIGS})


@agent.route('/api/agent/query', methods=['POST'])
def query_agent():
    try:
        data = request.get_json(silent=True) or {}
        agent_type = data.get('agent_type', 'general')
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
            payload = gather_inventory_data()

        effective_type = agent_type if agent_type in AGENT_CONFIGS else intent

        llm_text = ask_llm(
            build_system_prompt(effective_type),
            build_user_prompt(effective_type, message, payload),
        )
        # 异常 1: LLM 调用失败 → 走兜底
        if llm_text is None:
            llm_text = fallback_response(effective_type, message, payload)
            source = 'rule'
        # 异常 2: LLM 返回幻觉（说问题为空之类） → 也退回兜底
        elif _looks_like_hallucination(llm_text):
            llm_text = fallback_response(effective_type, message, payload)
            source = 'rule-fallback'
        else:
            source = 'llm'

        AGENT_CONTEXT['last_agent_type'] = effective_type
        AGENT_CONTEXT['last_query_time'] = datetime.now().isoformat()

        return jsonify({
            'success': True,
            'response': llm_text,
            'agent_type': effective_type,
            'source': source,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as exc:  # noqa: BLE001
        return jsonify({'success': False, 'error': str(exc)}), 500


@agent.route('/api/agent/context', methods=['GET'])
def get_agent_context():
    return jsonify({'success': True, 'context': AGENT_CONTEXT})


@agent.route('/api/agent/context', methods=['POST'])
def update_agent_context():
    try:
        data = request.get_json(silent=True) or {}
        if 'inventory_threshold' in data:
            Config.AGENT_INVENTORY_THRESHOLD = int(data['inventory_threshold'])
            AGENT_CONTEXT['inventory_threshold'] = Config.AGENT_INVENTORY_THRESHOLD
        return jsonify({'success': True, 'context': AGENT_CONTEXT})
    except Exception as exc:  # noqa: BLE001
        return jsonify({'success': False, 'error': str(exc)}), 500
