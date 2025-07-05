import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
import pytz

# 한국 시간대 기준
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
one_hour_ago = now - timedelta(hours=1)

# 텔레그램 봇 설정
TELEGRAM_TOKEN = "7440645018:AAG_yFBsdyaMmhK_He7lI3EBWggLK9wenXg"
CHAT_ID = "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

# 키워드 (200여개 그대로 유지)
keywords = [
    "스테이블코인", "GPT", "전선", "전력망", "AI", "재생에너지", "바이오", "로봇", "초전도체", "친환경에너지",
    "우크라이나", "전쟁", "수소", "휴머노이드", "데이터센터", "항공사", "항공우주", "유전자치료", "줄기세포", "자율주행",
    "전기차", "원전", "SMR", "K뷰티", "디지털화폐", "핀테크", "5G", "통신장비", "지역화폐", "STO", "전자결제",
    "우주항공", "해저터널", "재난", "안전", "비만치료제", "석유", "대체에너지", "천연가스", "삼성", "LG", "SK",
    "삼성전자", "LG에너지솔루션", "SK하이닉스", "클라우드", "네트워크", "사이버보안", "양자컴퓨터", "반도체", "메타버스",
    "VR", "AR", "드론", "블록체인", "NFT", "웹3", "AI반도체", "테슬라", "엔비디아", "ARM", "TSMC", "인터넷은행",
    "모빌리티", "자원외교", "탄소배출권", "수처리", "2차전지", "이차전지", "ESS", "BMS", "전기선박", "풍력", "태양광",
    "지열", "소형모듈원자로", "위성", "군수", "방산", "생명공학", "면역항암제", "mRNA", "진단키트", "인공지능", "자연어처리",
    "영상인식", "스마트팩토리", "UAM", "도심항공모빌리티", "OLED", "디스플레이", "반도체장비", "리튬", "니켈", "코발트",
    "희토류", "중국", "미국", "일본", "유럽", "이란", "러시아", "북한", "원유", "IRA", "탄소포집", "탄소중립",
    "탄소세", "감세", "투자유치", "규제완화", "규제자유특구", "지정학리스크", "오펙", "오펙플러스", "국제유가", "리오프닝",
    "백화점", "스마트시티", "도시재생", "스마트팜", "메타", "옵션매수", "특허", "특허등록", "특허취득", "참전", "창업지원",
    "회계감리", "회계조작", "회계이슈", "회생절차", "약업신문", "SM", "SG", "LNG", "FDA", "임상", "임상1상", "임상2상",
    "임상3상", "임상완료", "정비사업", "방사능", "지진", "수해", "산불", "AI고속도로", "에너지고속도로", "에너지정책",
    "에너지안보", "에너지저장장치", "도입계획", "상용화", "속보", "실시간 속보", "참여기업", "참가사", "참가국", "딥러닝",
    "챗GPT", "핑크퐁", "아기상어", "마귀상어", "대왕고래", "국가전략산업", "국산화", "기업결합", "넷플릭스", "구글", "카카오페이"
]

# 뉴스 채널 (20개 그대로 유지)
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
    "https://www.sedaily.com/NewsList/GB01"
]

def fetch_and_filter_news():
    for url in news_sites:
        try:
            rss = feedparser.parse(url)
            for entry in rss.entries:
                raw_title = entry.title
                title = raw_title.strip()
                link = entry.link.strip()

                # 유튜브 제외
                if "youtube.com" in link or "youtu.be" in link:
                    continue

                # 날짜 파싱
                pub_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                if not pub_struct:
                    continue
                pub_datetime = datetime(*pub_struct[:6], tzinfo=pytz.utc).astimezone(kst)

                # ▶▶ 1시간 이내 기사만 통과 ◀◀
                if pub_datetime < one_hour_ago or pub_datetime > now:
                    continue

                # 제목 깨짐 보정
                if any(domain in url for domain in ["asiae", "edaily", "infostock"]):
                    try:
                        html = requests.get(link, timeout=5)
                        html.encoding = "euc-kr"
                        soup = BeautifulSoup(html.text, "html.parser")
                        og_title = soup.select_one("meta[property='og:title']")
                        if og_title:
                            raw_title = og_title["content"]
                            title = raw_title.strip()
                    except:
                        continue

                # 키워드 필터링
                if any(k in raw_title for k in keywords):
                    bot.send_message(chat_id=CHAT_ID, text=f"[{raw_title}]\n{link}")

        except Exception:
            continue

if __name__ == "__main__":
    fetch_and_filter_news()

if __name__ == "__main__":
    fetch_and_filter_news()
