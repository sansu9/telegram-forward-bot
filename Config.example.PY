"""
配置文件模板 —— 复制为 config.py 后再填入你自己的真实信息
    cp config.example.py config.py
config.py 已经写进 .gitignore，不会被提交到 Git，放心填真实值。
"""

# === Telegram API 凭证 ===
# 前往 https://my.telegram.org 登录后进入 "API development tools" 创建应用获取
API_ID = 12345678                    # 替换为你的 api_id（整数）
API_HASH = "your_api_hash_here"      # 替换为你的 api_hash
PHONE = "+8613800138000"             # 你的 Telegram 登录手机号（含国家区号）

# === 监听的源群组（可以是你没有管理权限、只是普通成员的群） ===
# 支持群组用户名（如 "somegroup"）或数字ID（形如 -1001234567890），可以填多个
SOURCE_CHATS = [
    "source_group_username",
]

# === 转发目标：你自己的频道或群 ===
# 需要你的账号已经是该频道/群成员，且有发送消息的权限（频道的话需要是管理员）
DESTINATION_CHAT = "your_channel_username"

# === 转发方式 ===
# True  = 使用 Telegram 原生"转发"功能（会显示 "Forwarded from XXX"）
# False = 以自己账号名义重新发送内容（不显示来源，可配合下面的清洗规则去掉消息里的广告尾巴）
USE_NATIVE_FORWARD = False

# === 广告关键词：命中任意一条，整条消息将被跳过，不转发 ===
# 请根据你实际观察到的广告内容持续补充调整
AD_KEYWORDS = [
    "加V", "加威信", "私聊详谈", "一手货源", "代理招募",
    "免费领取", "限时优惠", "扫码领取", "点击链接领取",
]

# === 广告链接特征（正则），命中即视为广告 ===
AD_LINK_PATTERNS = [
    r"t\.me/joinchat/",
    r"t\.me/\+",
]

# === 是否启用 AI 智能过滤 ===
# 关键词规则未命中的消息，会再交给大模型判断一次是否为广告，更准但有调用成本和延迟
USE_AI_FILTER = False
ANTHROPIC_API_KEY = ""   # 启用 AI 过滤时必填，从 https://console.anthropic.com 获取

# === 消息内容清洗规则（正则）===
# 用于去掉消息里夹带的广告文本片段（不影响该条消息本身是否被判定为广告/是否转发）
STRIP_PATTERNS = [
    r"👉.*(加|扫码).{0,4}(微信|威信|[vV]).*$",
]

# === 去重设置 ===
# 相同文字内容在这么多天内重复出现会被跳过，不会重复转发
# （只对文字去重，纯图片/视频且没有文字说明的消息不受影响，照常转发）
DEDUP_WINDOW_DAYS = 30
