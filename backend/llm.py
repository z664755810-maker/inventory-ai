"""DeepSeek（OpenAI 兼容协议）大模型调用封装。

设计原则：
- API Key 只从环境变量读取，绝不硬编码、绝不落库。
- 调用失败（无 Key / 网络异常 / 配额不足）一律返回 None，
  由调用方降级到本地规则答复，保证演示不崩。
"""
import os
from openai import OpenAI

_client = None
_client_ready = False


def get_client():
    """懒加载并缓存 OpenAI 客户端；无 Key 时返回 None。"""
    global _client, _client_ready
    if _client_ready:
        return _client

    api_key = os.getenv('LLM_API_KEY')
    if not api_key:
        _client_ready = True
        _client = None
        return None

    base_url = os.getenv('LLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
    try:
        _client = OpenAI(api_key=api_key, base_url=base_url)
    except Exception as exc:  # noqa: BLE001
        print(f'[LLM] 客户端初始化失败: {exc}')
        _client = None
    _client_ready = True
    return _client


def ask_llm(system_prompt: str, user_prompt: str,
            max_tokens: int = 800, temperature: float = 0.3) -> str | None:
    """调用大模型，成功返回文本，失败/未配置返回 None。"""
    client = get_client()
    if client is None:
        return None

    model = os.getenv('LLM_MODEL', 'glm-4-flash')
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001
        print(f'[LLM] 调用失败: {exc}')
        return None
