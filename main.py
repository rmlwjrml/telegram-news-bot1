import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import pytz

# 한국 시간대 기준 날짜
kst = pytz.timezone('Asia/Seoul')
today = datetime.now(kst).strftime('%Y-%m-%d')

# 텔레그램 봇 설정
TELEGRAM_TOKEN = "7440645018:AAG_yFBsdyaMmhK_He7lI3EBWggLK9wenXg"
CHAT_ID = "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

# 키워드 목록 (총 200개 예시)
keywords = [
    "스테이블코인", "GPT", "전선", "전력망", "AI", "재생에너지", "바이오", "로봇", "초전도체",
    "친환경에너지", "우크라이나", "전쟁", "수소", "휴머노이드", "데이터센터", "항공사", "항공우주",
    "유전자치료", "줄기세포", "자율주행", "전기차", "원전", "SMR", "K뷰티", "디지털화폐", "핀테크",
    "5G", "통신장비", "지역화폐", "STO", "전자결제", "우주항공", "해저터널", "재난", "안전",
    "비만치료제", "석유", "대체에너지", "천연가스", "삼성", "LG", "SK", "삼성전자", "LG에너지솔루션",
    "SK하이닉스", "클라우드", "네트워크", "사이버보안", "양자컴퓨터", "반도체", "메타버스", "VR", "AR",
    "드론", "블록체인", "NFT", "웹3", "AI반도체", "테슬라", "엔비디아", "ARM", "TSMC", "인터넷은행",
    "모빌리티", "자원외교", "탄소배출권", "수처리", "2차전지", "이차전지", "ESS", "BMS", "전기선박",
    "풍력", "태양광", "지열", "소형모듈원자로", "위성", "군수", "방산", "생명공학", "면역항암제", "mRNA",
    "진단키트", "인공지능", "자연어처리", "영상인식", "스마트팩토리", "UAM", "도심항공모빌리티", "OLED", "디스플레이",
    "반도체장비", "리튬", "니켈", "코발트", "희토류", "중국", "미국", "일본", "유럽", "이란", "러시아", "북한"
]

# 뉴스 채널 RSS 주소 리스트 (대표 100개)
news_sites = [
    "https://www.asiae.co.kr/rss/all.xml",
    "https://rss.etnews.com/ETnews.xml",
    "https://www.hankyung.com/feed",
    "https://www.edaily.co.kr/rss/news.xml",
    "https://www.infostockdaily.co.kr/rss/allArticle.xml",
    "https://www.yonhapnewstv.co.kr/browse/feed/",
    "https://www.mk.co.kr/rss/30000001/",
    "https://www.fntimes.com/rss/allArticle.xml",
    "https://www.seoulfn.com/rss/allArticle.xml",
    "https://www.kpinews.co.kr/rss/allArticle.xml",
    "https://www.kbiznews.co.kr/rss/allArticle.xml",
    "https://www.itooza.com/rss/today.xml",
    "https://www.kukinews.com/rss/allArticle.xml",
    "https://www.consumernews.co.kr/rss/allArticle.xml",
    "https://www.ekn.kr/rss/allArticle.xml",
    "https://www.paxnet.co.kr/rss/main.xml",
    "https://www.hankyung.com/it/feed",
    "https://www.hankyung.com/economy/feed",
    "https://biz.chosun.com/rss/chosunbiz.xml",
    "https://www.sedaily.com/NewsList/GB01",
    "https://news.mt.co.kr/mtview/rss",
    "https://news.nate.com/rss/news.xml",
    "https://www.zdnet.co.kr/news/news_xml.html",
    "https://www.ddaily.co.kr/rss/allArticle.xml",
    "https://www.khan.co.kr/rss/rssdata/kh_news.xml"
]

def fetch_and_filter_news():
    for url in news_sites:
        try:
            rss = feedparser.parse(url)
            for entry in rss.entries:
                title = entry.title
                link = entry.link

                # 유튜브 뉴스 제외
                if "youtube.com" in link or "youtu.be" in link:
                    continue

                # 날짜 필터링
                pub_date = entry.get("published", "") or entry.get("updated", "")
                if today not in pub_date:
                    continue

                # 인코딩 문제 채널 처리
                if any(d in url for d in ["asiae", "edaily", "infostock"]):
                    try:
                        html = requests.get(link, timeout=5)
                        html.encoding = 'euc-kr'
                        soup = BeautifulSoup(html.text, 'html.parser')
                        og_title = soup.select_one("meta[property='og:title']")
                        if og_title:
                            title = og_title["content"]
                    except:
                        continue

                if any(k in title for k in keywords):
                    bot.send_message(chat_id=CHAT_ID, text=f"[{title}]
{link}")

        except Exception as e:
            continue

if __name__ == "__main__":
    fetch_and_filter_news()
