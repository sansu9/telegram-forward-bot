"""
去重逻辑：给转发过的消息内容生成指纹，避免同一内容被重复转发
（比如同一条广告/公告在好几个源群里都发了一遍）

限制：只对文本内容去重（基于消息文本算哈希）。没有文字、纯图片/视频且没写
说明文字的消息，没有内容可以用来去重，会照常转发，不受影响。
"""
import hashlib
import json
import os
import time

from config import DEDUP_WINDOW_DAYS

DEDUP_FILE = "seen_messages.json"


def _normalize(text: str) -> str:
    """归一化文本：去掉多余空白、统一大小写，减少因为细微差异被误判成"不同内容" """
    return "".join(text.split()).lower()


def _fingerprint(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def _load() -> dict:
    if not os.path.exists(DEDUP_FILE):
        return {}
    try:
        with open(DEDUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    with open(DEDUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def is_duplicate(text: str) -> bool:
    """
    判断这条消息内容是否在 DEDUP_WINDOW_DAYS 天内已经出现过。
    第一次出现：记录指纹，返回 False（正常转发）。
    之前出现过：返回 True（应跳过，不再转发）。
    """
    if not text:
        return False

    data = _load()
    now = time.time()
    cutoff = now - DEDUP_WINDOW_DAYS * 86400

    # 顺手清理过期记录，避免文件无限增长
    data = {fp: ts for fp, ts in data.items() if ts > cutoff}

    fp = _fingerprint(text)
    if fp in data:
        _save(data)
        return True

    data[fp] = now
    _save(data)
    return False
