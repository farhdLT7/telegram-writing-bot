# 🤖 ربات نویسندگی تلگرام

ربات خودکار که هر **۴ ساعت** یک پست ادبی غمگین با تصویر در کانال تلگرامت منتشر می‌کنه.

---

## ✨ قابلیت‌ها

- 📚 دریافت اطلاعات کتاب از **طاقچه**
- ✍️ تولید تیکه غمگین و ادبی با **Claude AI**
- 🎨 ساخت تصویر زیبا با **۳ سبک تصادفی**:
  - 🌙 مینیمال تاریک (Dark Minimal)
  - 🎨 آبرنگی (Watercolor)
  - 🏔️ طبیعت + متن (Nature Text)
- 📤 ارسال خودکار به **کانال تلگرام**

---

## 🚀 نصب و راه‌اندازی

### ۱. نصب پیش‌نیازها

```bash
pip install -r requirements.txt
```

### ۲. تنظیم کلید Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

> کلید رو از [console.anthropic.com](https://console.anthropic.com) بگیر

### ۳. اجرای ربات

```bash
bash start.sh
```

یا مستقیم:

```bash
python3 bot.py
```

---

## ⚙️ اجرای دائمی (۲۴/۷)

### با tmux (پیشنهادی)
```bash
tmux new -s bot
export ANTHROPIC_API_KEY="sk-ant-..."
python3 bot.py
# Ctrl+B سپس D برای detach
```

### با systemd (سرور لینوکس)
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

محتوا:
```ini
[Unit]
Description=Telegram Writing Bot
After=network.target

[Service]
User=YOUR_USER
WorkingDirectory=/path/to/telegram_bot
Environment=ANTHROPIC_API_KEY=sk-ant-...
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### با Docker
```bash
docker run -d \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -v $(pwd):/app \
  -w /app \
  python:3.11 \
  bash -c "pip install -r requirements.txt && python3 bot.py"
```

---

## 📁 ساختار فایل‌ها

```
telegram_bot/
├── bot.py          ← کد اصلی ربات
├── requirements.txt
├── start.sh        ← اسکریپت راه‌اندازی
├── README.md
└── bot.log         ← لاگ‌ها (خودکار ساخته می‌شه)
```

---

## 🔧 تنظیمات

در `bot.py` می‌تونی تغییر بدی:

| متغیر | توضیح |
|-------|-------|
| `TELEGRAM_TOKEN` | توکن ربات تلگرام |
| `CHANNEL_ID` | آیدی کانال (مثلاً @mychannel) |
| `schedule.every(4).hours` | فاصله زمانی ارسال |
| `IMAGE_STYLES` | سبک‌های تصویر |

---

## 📌 نکات مهم

- ربات باید **ادمین کانال** باشه
- نیاز به **اینترنت** برای طاقچه و Anthropic
- لاگ‌ها در `bot.log` ذخیره می‌شن
