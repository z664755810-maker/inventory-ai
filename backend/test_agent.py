"""智能体模块单元测试 + 接口联通测试（无需网络，验证离线兜底路径）。"""
import os
import sys
from pathlib import Path

import pytest

# 确保 backend 目录在导入路径中
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app  # noqa: E402  (导入即初始化 db / 注册蓝图)
from routes.agent import (  # noqa: E402
    analyze_intent,
    gather_inventory_data,
    gather_sales_data,
    gather_report_data,
)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    # 强制走离线兜底，避免测试时触发真实大模型调用
    os.environ.pop('LLM_API_KEY', None)
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


def test_analyze_intent():
    assert analyze_intent('库存预警') == 'inventory'
    assert analyze_intent('销售排行') == 'sales'
    assert analyze_intent('本月利润报表') == 'report'
    assert analyze_intent('你好') == 'general'


def test_gather_functions_return_dict():
    with app.app_context():
        inv = gather_inventory_data()
        assert isinstance(inv, dict) and 'threshold' in inv
        sales = gather_sales_data()
        assert isinstance(sales, dict) and 'order_count' in sales
        rep = gather_report_data()
        assert isinstance(rep, dict) and 'profit' in rep


def test_agent_query_without_key_uses_fallback(client):
    r = client.post('/api/agent/query',
                    json={'agent_type': 'inventory', 'message': '库存预警'})
    assert r.status_code == 200
    body = r.get_json()
    assert body['success'] is True
    assert body['source'] == 'rule'          # 无 Key → 离线兜底
    assert isinstance(body['response'], str) and len(body['response']) > 0


def test_agent_query_empty_message(client):
    r = client.post('/api/agent/query', json={'message': ''})
    assert r.status_code == 400
    assert r.get_json()['success'] is False


def test_agent_configs(client):
    r = client.get('/api/agent/configs')
    assert r.status_code == 200
    assert 'configs' in r.get_json()
