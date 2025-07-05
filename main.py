import requests
from bs4 import BeautifulSoup
import telegram
import time
from datetime import datetime
import pytz

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

bot = telegram.Bot(token=TOKEN)
sent = set()

# 대한민국 시간 기준으로 오늘 날짜 구하기
kst = pytz.timezone("Asia/Seoul")
today = datetime.now(kst).strftime("%Y-%m-%d")

# 예시: 뉴스 채널 리스트 (일부)
news_sites = [
    {"name": "연합뉴스", "url": "https://www.yna.co.kr/news", "base": "https://www.yna.co.kr", "selector": "div.headline-list ul li a"},
    {"name": "이데일리", "url": "https://www.edaily.co.kr/news", "base": "", "selector": "div.list_news div a"},
    {"name": "인포스탁", "url": "https://news.infostock.co.kr/news", "base": "", "selector": "ul.list_area a"},
    # ... 전체 100개로 확장 가능
]

keywords = [
    "스테이블코인", "GPT", "5G", "AI", "수소", "원전해체", "친환경에너지", "로봇",
    # ... 키워드 200개로 확장 가능
]

def clean_text(text):
    return text.replace("\xa0", " ").replace("\u3000", " ").strip()

def get_news(site):
    try:
        res = requests.get(site["url"], timeout=5)
        res.encoding = res.apparent_encoding  # 인코딩 자동 판단
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(site["selector"])
        results = []
        for item in items:
            title = clean_text(item.get_text())
            href = item.get("href")
            if not href:
                continue
            if not href.startswith("http"):
                href = site["base"] + href
            if today in href or today in title:
                results.append((title, href))
        return results
    except Exception as e:
        return []

while True:
    try:
        for site in news_sites:
            news_items = get_news(site)
            for title, link in news_items:
                if any(k in title for k in keywords):
                    if title not in sent:
                        bot.send_message(chat_id=CHAT_ID, text=f"[{title}]
{link}")
                        sent.add(title)
        time.sleep(30)
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"[오류] {e}")
        time.sleep(60)