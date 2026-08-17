"""
广告过滤逻辑
"""
import re

from config import AD_KEYWORDS, AD_LINK_PATTERNS, STRIP_PATTERNS, USE_AI_FILTER

_ai_client = None  # 延迟初始化，只有真正开启 AI 过滤时才会用到 anthropic 包


def is_advertisement_by_rules(text: str) -> bool:
    """基于关键词 / 正则规则判断是否为广告，命中任意一条即判定为广告"""
    if not text:
        return False

    for kw in AD_KEYWORDS:
        if kw in text:
            return True

    for pattern in AD_LINK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def is_advertisement_by_ai(text: str) -> bool:
    """
    （可选）用 Claude 模型做二次判断，比纯关键词更能识别没写进关键词表里的新型广告。
    只有 config.py 里 USE_AI_FILTER = True 时才会被调用。
    """
    global _ai_client
    from config import ANTHROPIC_API_KEY

    if _ai_client is None:
        import anthropic
        _ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = (
        "判断下面这条 Telegram 群消息是否属于广告/推广/营销内容。"
        "只回答一个字：是 或 否，不要输出任何其他内容。\n\n"
        f"消息内容：\n{text}"
    )
    # Haiku 速度快、成本低，适合这种短文本二分类场景；
    # 如果广告形式比较隐蔽、需要更强的语义判断，可以换成 "claude-sonnet-5"
    resp = _ai_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = resp.content[0].text.strip()
    return answer.startswith("是")


def is_advertisement(text: str) -> bool:
    """综合判断入口：先走关键词规则，未命中且开启了 AI 过滤时再调用模型二次确认"""
    if is_advertisement_by_rules(text):
        return True
    if USE_AI_FILTER and text:
        return is_advertisement_by_ai(text)
    return False


def clean_message(text: str) -> str:
    """清洗消息中夹带的广告文本片段（不影响整条消息是否被转发的判断）"""
    if not text:
        return text
    cleaned = text
    for pattern in STRIP_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()
