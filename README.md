# 3X-UI_log_formatter
Script from ChatGPT that makes your log file clear.
Just put it in directory with .log file and start command "python3 log_formatter.py".

# What it does:
• Reverse logs from up to bottom(the fresher, the higher)
• Remove words like from, accept, inbound→direct.
• Remove local logs from 127.0.0.1
• Delete www.google.com and ports(because of flood and spam)
• Add beautiful brackets (because I want)
# Example:

2024/12/07 17:00:00 from {ip:port} accepted tcp:www.google.com:443 [inbound-443 >> direct] email: 2222Na
2024/12/07 17:00:00 from {ip:port} accepted tcp:github.com:443 [inbound-443 >> direct] email: 2222Na
↓↓↓
[2024/12/07 | 17:00:00] 2222Na: {ip} → github.com


//New achievement: reinvent the bike
