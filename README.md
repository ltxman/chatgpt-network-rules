# ChatGPT Network Rules

给 Mihomo / Clash Verge Rev / Clash Meta for Android 共用的 ChatGPT 网络规则源。

## ChatGPT Voice 自动更新

OpenAI 官方说明 ChatGPT Voice 使用 UDP 3478，当前服务器 IP 范围维护在 `chatgpt-voice.json`，并会持续更新。

本仓库每 6 小时由 GitHub Actions：

1. 下载 OpenAI 官方 `https://openai.com/chatgpt-voice.json`
2. 验证 JSON
3. 提取并校验 IP/CIDR
4. 生成 Mihomo `ipcidr + text` 格式
5. 只有规则变化时才提交新版本

规则地址：

```text
https://raw.githubusercontent.com/ltxman/chatgpt-network-rules/main/rules/chatgpt-voice.txt
```

## Mihomo rule-provider

```yaml
rule-providers:
  chatgpt-voice-auto:
    type: http
    behavior: ipcidr
    format: text
    url: "https://raw.githubusercontent.com/ltxman/chatgpt-network-rules/main/rules/chatgpt-voice.txt"
    path: ./ruleset/openai/chatgpt-voice.txt
    interval: 21600
```

ChatGPT Voice 分流：

```yaml
rules:
  - AND,((NETWORK,UDP),(DST-PORT,3478),(RULE-SET,chatgpt-voice-auto)),💸 ChatGPT-Gemini-XAI-Perplexity
  - AND,((NETWORK,UDP),(DST-PORT,3478),(RULE-SET,chatgpt-voice-auto)),REJECT
```

第二条 `REJECT` 是防泄漏兜底：如果命中的 AI 节点不支持 UDP，避免继续向后匹配到普通机场出口。

## 文件

- `rules/chatgpt-voice.txt`：给 Mihomo 使用的 HTTP rule-provider
- `scripts/update_chatgpt_voice.py`：官方 JSON -> Mihomo text 转换器
- `.github/workflows/update-chatgpt-voice.yml`：每 6 小时自动检查
- `.github/workflows/keepalive.yml`：每周轻量活动提交
- `examples/`：Clash Verge Rev / CMFA 引用示例

## 安全

仓库只存公开网络规则，不要提交：
- 机场订阅 URL
- 代理用户名/密码
- 静态 ISP 账号
- Token / Cookie / API Key
