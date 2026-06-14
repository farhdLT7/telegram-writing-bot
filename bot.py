#!/usr/bin/env python3
"""
ربات تلگرام - پست خودکار نقل‌قول‌های غم‌انگیز با تصویر
- روی Railway: loop داخلی هر X ساعت
- روی GitHub Actions: یک بار اجرا و تموم
"""

import asyncio
import logging
import random
import requests
import io
import sys
import os
import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot

# ─────────────────────────────────────────────
# تنظیمات
# ─────────────────────────────────────────────
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID  = os.environ.get("CHANNEL_ID", "")
INTERVAL_H  = int(os.environ.get("INTERVAL_HOURS", "1"))   # پیش‌فرض: هر ۴ ساعت
RUN_MODE    = os.environ.get("RUN_MODE", "once")            # "once" یا "loop"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# صفحات نقل‌قول طاقچه
# ─────────────────────────────────────────────
TAAGHCHE_URLS = [
    "https://taaghche.com/quotes",
    "https://taaghche.com/quotes?page=2",
    "https://taaghche.com/quotes?page=3",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fa,en;q=0.9",
}

FALLBACK_QUOTES = [
    ("خوشبختی پرنده‌ای است که همیشه بر شاخه دیگری می‌نشیند.", "صادق هدایت"),
    ("تنها چیزی که از گذشته برایم مانده، آرزوی بازگشتن به آن است.", "سهراب سپهری"),
    ("دل می‌خواهد کسی باشد که بفهمد، نه کسی که بشنود.", "فروغ فرخزاد"),
    ("گاهی سکوت، بلندترین فریادی است که می‌توانی بزنی.", "صادق چوبک"),
    ("همه‌چیز را از دست می‌دهی تا یاد بگیری چه چیزی داشتی.", "احمد شاملو"),
    ("تنهایی درد نیست، درد آن است که کسی نفهمد تنهایی‌ات را.", "محمود دولت‌آبادی"),
    ("وقتی دیگر نگران از دست دادنت نیستم، یعنی از پیش از دست داده‌ام‌ات.", "هوشنگ ابتهاج"),
    ("بعضی آدم‌ها مثل باران‌اند، وقتی می‌روند همه‌چیز را با خود می‌برند.", "فروغ فرخزاد"),
    ("آدم وقتی تنهاست، صدای نفس‌هایش را هم می‌شنود.", "بزرگ علوی"),
    ("چه فرقی می‌کند کجا باشی، وقتی دلت آنجا نیست.", "نادر ابراهیمی"),
]

# ─────────────────────────────────────────────
# دریافت نقل‌قول از طاقچه
# ─────────────────────────────────────────────
def fetch_quote() -> tuple[str, str]:
    url = random.choice(TAAGHCHE_URLS)
    try:
        log.info(f"دریافت از: {url}")
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        quotes = []

        for el in soup.select("[class*='quote'], [class*='Quote']"):
            text_el   = el.select_one("[class*='text'], [class*='Text'], [class*='content'], p")
            author_el = el.select_one("[class*='author'], [class*='Author'], [class*='name'], cite")
            if text_el:
                text   = text_el.get_text(strip=True)
                author = author_el.get_text(strip=True) if author_el else "نامشخص"
                if 20 < len(text) < 400:
                    quotes.append((text, author))

        if not quotes:
            for bq in soup.find_all("blockquote"):
                text = bq.get_text(strip=True)
                if 20 < len(text) < 400:
                    quotes.append((text, "نامشخص"))

        if quotes:
            pick = random.choice(quotes)
            log.info(f"نقل‌قول پیدا شد: {pick[0][:50]}...")
            return pick

    except Exception as e:
        log.warning(f"خطا در طاقچه: {e}")

    log.info("نقل‌قول پشتیبان انتخاب شد")
    return random.choice(FALLBACK_QUOTES)


# ─────────────────────────────────────────────
# ساخت تصویر با Pollinations.ai (رایگان)
# ─────────────────────────────────────────────
def generate_image(quote_text: str) -> bytes | None:
    # پرامپت بر اساس متن نقل‌قول
    base_prompts = [
        f"melancholic Persian poetry scene inspired by: '{quote_text[:60]}', dark moody atmosphere, autumn leaves, lonely figure, misty fog, cinematic, oil painting, masterpiece",
        f"sad emotional artwork, persian garden at night, moonlight, falling petals, melancholy, inspired by quote, artistic, detailed illustration",
        f"dramatic dark landscape, stormy sky, single candle light, emotional depth, cinematic photography, ultra detailed, moody",
        f"lonely person under rain, dark alley, dramatic lighting, melancholic mood, artistic photography, film noir style",
        f"abandoned beautiful garden, autumn golden light, melancholy, impressionist painting, emotional depth, persian art style",
    ]
    prompt  = random.choice(base_prompts)
    encoded = urllib.parse.quote(prompt)
    seed    = random.randint(1, 99999)
    url     = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1080&seed={seed}&model=flux&nologo=true"
    )
    try:
        log.info("در حال ساخت تصویر...")
        resp = requests.get(url, timeout=90)
        resp.raise_for_status()
        if "image" in resp.headers.get("content-type", ""):
            log.info("✅ تصویر ساخته شد")
            return resp.content
    except Exception as e:
        log.warning(f"خطا در ساخت تصویر: {e}")
    return None


# ─────────────────────────────────────────────
# ارسال یک پست
# ─────────────────────────────────────────────
async def send_post(bot: Bot):
    log.info("─── شروع ارسال پست جدید ───")

    quote, author = fetch_quote()
    image_data    = generate_image(quote)
    now           = datetime.now().strftime("%Y/%m/%d  %H:%M")

    caption = (
        f"📖 *{quote}*\n\n"
        f"✍️ _{author}_\n\n"
        f"─────────────────\n"
        f"🕐 {now}\n"
        f"📚 {CHANNEL_ID}"
    )

    if image_data:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=io.BytesIO(image_data),
            caption=caption,
            parse_mode="Markdown"
        )
        log.info("✅ پست با تصویر ارسال شد")
    else:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption,
            parse_mode="Markdown"
        )
        log.info("✅ پست متنی ارسال شد (بدون تصویر)")


# ─────────────────────────────────────────────
# اجرای اصلی
# ─────────────────────────────────────────────
async def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        log.error("❌ BOT_TOKEN یا CHANNEL_ID تنظیم نشده!")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    me  = await bot.get_me()
    log.info(f"🤖 ربات: @{me.username}")
    log.info(f"📢 کانال: {CHANNEL_ID}")
    log.info(f"⚙️  حالت: {RUN_MODE} | فاصله: {INTERVAL_H} ساعت")

    if RUN_MODE == "loop":
        # حالت Railway: loop دائمی
        log.info("🔁 حالت loop فعاله — ربات ۲۴/۷ اجرا می‌شه")
        while True:
            try:
                await send_post(bot)
            except Exception as e:
                log.error(f"❌ خطا در ارسال پست: {e}")
            wait_seconds = INTERVAL_H * 3600
            log.info(f"⏳ پست بعدی در {INTERVAL_H} ساعت دیگه...")
            await asyncio.sleep(wait_seconds)
    else:
        # حالت GitHub Actions: یک بار اجرا
        log.info("1️⃣  حالت once — یک پست می‌فرسته و تموم")
        await send_post(bot)


if __name__ == "__main__":
    asyncio.run(main())
