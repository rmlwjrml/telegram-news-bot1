
import requests
from bs4 import BeautifulSoup
import telegram
import time

TOKEN = "7877805562:AAGR6N_eqSf8tB19k_MIj4u1WLbU-MT8lDA"
CHAT_ID = "5639589613"
bot = telegram.Bot(token=TOKEN)

keywords = [
    "스테이블코인", "SMR", "AI", "로봇", "전선", "해저터널", "전력", "수소", "석유", "재생에너지", "천연가스", 
    "GPT", "우주항공", "전쟁", "바이오", "비만치료제", "초전도체", "전자결제", "STO", "지역화폐", 
    "5G", "통신장비", "우크라이나", "원전해체", "휴머노이드", "항공사", "대체에너지", "친환경에너지",
    "삼성", "LG", "SK", "FDA", "임상", "백신", "양자컴퓨터", "반도체", "수출계약", "미국", "이란"
]

news_urls = [
    "https://finance.naver.com/news/mainnews.naver",
    "https://www.hankyung.com/all-news",
    "https://www.infostock.co.kr/news/list.html",
    "https://www.edaily.co.kr/news/",
    "https://www.yna.co.kr/news/",
    "https://news.mt.co.kr/newsList.html",
    "https://www.etoday.co.kr/news/news_list.html",
    "https://www.channelk.co.kr/news/list.php",
    "https://www.newspim.com/news/list",
    "https://www.asiae.co.kr/news/list.htm"
]

sent_news = set()

def fetch_news(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        headlines = soup.find_all('a')
        result = []
        for tag in headlines:
            title = tag.get_text(strip=True)
            link = tag.get('href')
            if link and title:
                if not link.startswith("http"):
                    link = requests.compat.urljoin(url, link)
                result.append((title, link))
        return result
    except:
        return []

while True:
    try:
        for site in news_urls:
            news_items = fetch_news(site)
            for title, link in news_items:
                lower_title = title.lower()
                if any(keyword.lower() in lower_title for keyword in keywords):
                    if title not in sent_news:
                        bot.send_message(chat_id=CHAT_ID, text=f"[속보] {title}\n{link}")
                        sent_news.add(title)
        time.sleep(30)
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"[오류] {e}")
        time.sleep(30)
