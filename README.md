# LinkSafe Bot

Telegram bot that checks any link for phishing before you click — built for Singapore, where scam messages impersonating DBS, Singpass, SingPost, and other local brands are common.

Companion bot to [LinkSafe](https://github.com/shakhsg/linksafe), the web version.

## Features

- **Send any link** — the bot scans it instantly, no command needed
- **Singapore-focused detection** — recognizes impersonation of 25+ local brands (DBS, POSB, OCBC, UOB, Singpass, IRAS, Shopee, Lazada, SingPost, and more)
- **Heuristic engine** — suspicious TLDs, phishing keywords, URL structure analysis, brand-in-subdomain tricks
- **Inline keyboards** — clean UX with `/start`, `/help`, `/check`, and `/about` commands

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token
2. Install dependencies and run:

```bash
pip install -r requirements.txt
echo "BOT_TOKEN=your_token_here" > .env
python bot.py
```

## Deployment

Includes a `Procfile` (`worker: python bot.py`) and `runtime.txt` for one-click deployment to Heroku-compatible platforms.

## Tech Stack

Python · python-telegram-bot · Regex-based heuristic detection

## License

MIT
