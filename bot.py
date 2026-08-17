"""
主程序：监听源群组消息，过滤广告后转发到目标频道/群

运行前：
1. pip install -r requirements.txt
2. 编辑 config.py，填好 API 凭证 / 源群组 / 目标频道
3. python bot.py（首次运行会要求在终端输入 Telegram 发来的验证码）
"""
import asyncio
import logging

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

from config import (
    API_ID, API_HASH, PHONE,
    SOURCE_CHATS, DESTINATION_CHAT, USE_NATIVE_FORWARD,
)
from ad_filter import is_advertisement, clean_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# "forward_session" 是本地会话文件名，登录成功后会生成 forward_session.session，
# 之后再次运行无需重新输验证码。这个文件相当于账号凭证，注意不要泄露。
client = TelegramClient("forward_session", API_ID, API_HASH)


@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    text = event.raw_text or ""

    try:
        # is_advertisement 内部可能调用 Claude API（同步阻塞调用），丢进线程池执行，
        # 避免在开启 AI 过滤时卡住整个事件循环
        if await asyncio.to_thread(is_advertisement, text):
            logger.info("已过滤广告消息：%s", text[:30].replace("\n", " "))
            return

        if USE_NATIVE_FORWARD:
            await client.forward_messages(DESTINATION_CHAT, event.message)
        else:
            cleaned_text = clean_message(text)
            if event.message.media:
                await client.send_message(
                    DESTINATION_CHAT, cleaned_text, file=event.message.media
                )
            elif cleaned_text:
                await client.send_message(DESTINATION_CHAT, cleaned_text)

        logger.info("已转发消息：%s", text[:30].replace("\n", " "))

    except FloodWaitError as e:
        logger.warning("触发 Telegram 限流，等待 %s 秒后继续", e.seconds)
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error("处理消息失败：%s", e)


async def main():
    await client.start(phone=PHONE)
    me = await client.get_me()
    logger.info("已登录账号：%s，开始监听消息...", me.first_name)
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
