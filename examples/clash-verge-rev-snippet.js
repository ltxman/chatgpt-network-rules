// Add this entry to your Clash Verge Rev Script.js ruleProviders object.
"chatgpt-voice-auto": {
  type: "http",
  behavior: "ipcidr",
  format: "text",
  url: "https://raw.githubusercontent.com/ltxman/chatgpt-network-rules/main/rules/chatgpt-voice.txt",
  path: "./ruleset/openai/chatgpt-voice.txt",
  interval: 21600,
  proxy: "🔰 模式选择"
}

// Put these before generic proxy / MATCH rules:
"AND,((NETWORK,UDP),(DST-PORT,3478),(RULE-SET,chatgpt-voice-auto)),💸 ChatGPT-Gemini-XAI-Perplexity",
"AND,((NETWORK,UDP),(DST-PORT,3478),(RULE-SET,chatgpt-voice-auto)),REJECT",
