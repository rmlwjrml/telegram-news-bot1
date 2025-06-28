import requests
from bs4 import BeautifulSoup
import telegram
import time

TOKEN = "7877805562:AAGR6N_eqSf8tB19k_MIj4u1WLbU-MT8lDA"
CHAT_ID = "5639589613"

bot = telegram.Bot(token=TOKEN)
sent = set()

def get_naver_news():
    url = 'https://finance.naver.com/news/mainnews.naver'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    headlines = soup.select('ul.newsList li dl dt a')
    return [h.get_text(strip=True) for h in headlines[:20]]

while True:
    try:
        news_list = get_naver_news()
        for news in news_list:
            if news not in sent:
                bot.send_message(chat_id=CHAT_ID, text=f"[속보] {news}")
                sent.add(news)
        time.sleep(30)
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"[오류] {e}")
        time.sleep(30)
