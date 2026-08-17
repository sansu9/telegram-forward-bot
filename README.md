# Telegram 广告过滤转发机器人

监听你已加入的源群组消息，过滤掉广告后，自动转发到你自己的频道或群。

## 本项目赞助商
 三俗数字商城 https://sansu6.com [专注解决苹果ID、ins、谷歌、电报、推特、静态住宅IP等海外社媒问题，提供一站式服务！
<!-- -->


## 为什么用 Telethon 而不是 Bot API

如果源群组不是你管理的群，普通 Bot（BotFather 创建的那种）通常读不到群里的全部消息——除非群主把它设为管理员。
本项目用 **Telethon** 模拟你自己的 Telegram 账号登录（MTProto 协议），只要你本人是这个群的成员，就能读到里面的消息，不需要任何额外权限。

## 搭建步骤

### 1. 获取 API 凭证
访问 https://my.telegram.org → 登录你的 Telegram 账号 → "API development tools" → 创建一个应用，会得到 `api_id` 和 `api_hash`。

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
如果不打算用 AI 智能过滤，可以不装 `anthropic` 这个包。

### 3. 配置
```bash
cp config.example.py config.py
```
`config.py` 已经在 `.gitignore` 里，不会被提交到 Git，可以放心填真实信息。编辑这个文件：
- 填入 `API_ID` / `API_HASH` / `PHONE`
- `SOURCE_CHATS` 填源群组的用户名或数字 ID（可以填多个）
- `DESTINATION_CHAT` 填你自己的频道/群（你的账号需要已经加入，且有发消息权限；如果目标是频道，你的账号要是管理员）
- 按需调整 `AD_KEYWORDS`（广告关键词）

### 4. 运行
```bash
python bot.py
```
第一次运行会要求在终端里输入 Telegram 发到你手机上的验证码，登录成功后会在本地生成 `forward_session.session` 文件，之后再运行就不用重新输验证码了。

## 广告过滤是怎么工作的

- **默认（关键词规则）**：消息命中 `config.py` 里的 `AD_KEYWORDS` 或 `AD_LINK_PATTERNS`，整条跳过不转发。免费、零延迟，但需要你根据实际观察到的广告持续补充关键词。
- **可选（AI 智能过滤）**：把 `config.py` 里的 `USE_AI_FILTER` 改成 `True`，并填入 `ANTHROPIC_API_KEY`。这样关键词规则没命中的消息会再交给 Claude 模型判断一次，能识别没写进关键词表里的新型广告，但每条消息会有少量 API 调用成本和延迟。
- 除了整条过滤，`STRIP_PATTERNS` 还可以把消息里夹带的广告尾巴（比如正文之后加的联系方式）单独清洗掉，不影响正文本身被转发。

## 推送到 GitHub

```bash
git init
git add .
git status   # 务必检查一下：不应该出现 config.py 或 *.session，只应该有 config.example.py
git commit -m "init"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

`git status` 那一步不要跳过——如果看到 `config.py` 或 `forward_session.session` 被列为待提交的文件，说明 `.gitignore` 没生效（比如文件名写错，或者之前已经 `git add` 过一次被缓存了），先解决掉再 commit，不然密钥就传上去了。

## 注意事项

- `forward_session.session` 和 `config.py` 里的 `api_hash` / `ANTHROPIC_API_KEY` 都是敏感信息，相当于账号凭证，不要上传到公开仓库或分享给别人。
- 用个人账号做自动化监听和转发，虽然是很常见的用法，但仍建议用小号而不是主力账号，避免万一触发风控影响正常使用。
- 转发前建议留意一下源群组的规则，避免因为搬运内容引发争议。
- 程序需要保持在后台持续运行才能实时转发；如果想 7x24 小时挂机，可以部署到云服务器上，用 `systemd`、`screen`、`tmux` 或 `pm2` 之类的工具保活，或者打包成 Docker 容器运行。

## 文件说明

| 文件 | 作用 |
|---|---|
| `config.example.py` | 配置模板，会被提交到 Git，仅含占位符 |
| `config.py` | 你本地的真实配置（由模板复制而来），**已 gitignore，不会被提交** |
| `ad_filter.py` | 广告判断 + 消息清洗逻辑 |
| `bot.py` | 主程序，监听消息并转发 |
| `requirements.txt` | 依赖列表 |
| `.gitignore` | 排除 `config.py`、`*.session` 等敏感文件 |
