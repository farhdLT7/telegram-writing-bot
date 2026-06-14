#!/bin/bash
# ─────────────────────────────────────────────────
# اسکریپت راه‌اندازی ربات نویسندگی تلگرام
# ─────────────────────────────────────────────────

echo "🤖 راه‌اندازی ربات نویسندگی تلگرام..."

# بررسی API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  متغیر ANTHROPIC_API_KEY تنظیم نشده!"
    echo "   لطفاً اجرا کن:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    read -p "کلید API خودت رو وارد کن: " api_key
    export ANTHROPIC_API_KEY="$api_key"
fi

echo "✅ شروع ربات..."
python3 bot.py
