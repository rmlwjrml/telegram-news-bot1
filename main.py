import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
import pytz
import time
import os
from urllib.parse import urlparse

# 설정
kst = pytz.timezone('Asia/Seoul')
TELEGRAM_TOKEN = "7440645018:AAG_yFBsdyaMmhK_He7lI3EBWggLK9wenXg"
CHAT_ID = "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

# 중복 전송 방지 파일 및 구조
sent_title_map = {}  # {domain: set([title])}
sent_titles_file = "sent_titles.txt"

# 3일 기준
def load_sent_titles():
    global sent_title_map
    now = datetime.now(kst)
    cutoff = now - timedelta(days=1)

    if os.path.exists(sent_titles_file):
        with open(sent_titles_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) != 3:
                continue
            domain, title, date_str = parts
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                if date_obj >= cutoff:
                    if domain not in sent_title_map:
                        sent_title_map[domain] = set()
                    sent_title_map[domain].add(title)
                    new_lines.append(line.strip())
            except:
                continue

        with open(sent_titles_file, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

def save_sent_title(domain, title):
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    with open(sent_titles_file, "a", encoding="utf-8") as f:
        f.write(f"{domain}|{title}|{now_str}\n")

# 키워드
keywords = [ "2차전지", "韓", "中", "배터리", "4인뱅", "인구정책", "K콘텐츠", "출산", 
"4인터넷", "6G", "AI", "ESS", "FDA", "GPT", 
"K문화", "K뷰티", "K콘텐츠", "LNG", "NFT", "SMR", "STO", "VR", "블록체인", "구글", "국내최초", "국가전략산업", "국산화", "데이터센터", "대북지원", 
"대왕고래", "대통령", "에너지", "라이다", "로보택시", "로봇", "마귀상어", 
"메타", "항암제", "모빌리티", "바이오", "방사능", "방산", "백신", "북극항로", "블랙웰", 
"비만치료제", "보안", "산불", "상용화", "생명공학", "석유", "세계최대", "세계최초", "스마트", "속보", "수소", "수출", 
"수해", "스테이블", "코인", "신약", "알래스카", "알츠하이머", 
"애플", "양자컴퓨터", "고속도로", "엔비디아", "옵티머스", "원유", "원전", "유전자치료", "이차전지", "이재명", 
"인터넷은행", "임상", "자율주행", "재건", "재난", "전기차", "전력", "전선", "전자결제", "전쟁", "정부", "제재", "지역화폐", "지진", "진단", "철강", "초고속인터넷", "초소형모듈", "초전도체", "치매", "친환경", "카지노", "클라우드", "키오스크", "탄소", "테슬라", 
"트럼프", "특허", "투자유치", "핀테크", "핑크퐁", "풍력", 
"퓨리오사", "풍력", "해저터널", "해외수주", "핵심", "핵폐기물", "화장품", "환경규제", 
"황사", "휴머노이드", "휴전", "희토류", "잭슨황", 
"우주", "항공", "한류", "한한령", "생명과학", "줄기", "세포", "mRNA", "ms", "네이버페이", 
"리튬", "니켈", "도시재생", "완화", "감세", "세제혜택", "李", "兆", "美", "한미", "폭염", "러시아", 
"우크라이나", "세종", "구리", "K반도체", "피부암", "피부", "연골", "재생", "플랫폼", "동물", "식약처", "의료", "장기", "플라스틱", "선박", "조선", "드론", "헬스케어", "인공", "이식", "이스라엘", "이란", "하마스", "중국", "신약개발", "치료제", "항체", "토큰", "디지털자산", "가상화폐", "철강", "가스" ]

# RSS 뉴스 사이트 목록 (생략 가능)
news_sites = [
"https://rss.donga.com/politics.xml",  # 동아일보(정치)
"https://rss.donga.com/national.xml",  # 동아일보(사회)
"https://rss.donga.com/economy.xml",   # 동아일보(경제)
"https://rss.donga.com/science.xml",   # 동아일보(의학과학)
"https://www.hani.co.kr/rss/politics/",   # 한겨레(정치)
"https://www.hani.co.kr/rss/economy/",    # 한겨레(경제)
"https://www.hani.co.kr/rss/society/",    # 한겨레(사회)
"https://www.hani.co.kr/rss/science/",    # 한겨레(과학)
"https://www.khan.co.kr/rss/rssdata/politic_news.xml",   # 경향신문(정치)
"https://www.khan.co.kr/rss/rssdata/economy_news.xml",   # 경향신문(경제)
"https://www.khan.co.kr/rss/rssdata/society_news.xml",   # 경향신문(사회)
"https://www.khan.co.kr/rss/rssdata/science_news.xml",   # 경향신문(과학환경)
"http://www.khan.co.kr/rss/rssdata/it_news.xml",         # 경향신문(IT)
"https://www.segye.com/Articles/RSSList/segye_politic.xml",   # 세계일보(정치)
"https://www.segye.com/Articles/RSSList/segye_economy.xml",   # 세계일보(경제)
"https://www.segye.com/Articles/RSSList/segye_society.xml",   # 세계일보(사회)
"https://www.segyefn.com/views/rss/finance.xml",              # 세계파이낸스(금융)
"https://www.segyefn.com/views/rss/industry.xml",             # 세계파이낸스(산업)
"https://www.segyefn.com/views/rss/stock.xml",                # 세계파이낸스(증권)
"http://rss.nocutnews.co.kr/nocutnews.xml",   # 노컷뉴스(전체)
"https://rss.ohmynews.com/rss/society.xml",   # 오마이뉴스(사회)
"https://rss.ohmynews.com/rss/politics.xml",  # 오마이뉴스(정치)
"https://rss.ohmynews.com/rss/economy.xml",   # 오마이뉴스(경제)
"https://rss.ohmynews.com/rss/education.xml", # 오마이뉴스(교육)
"https://www.mediatoday.co.kr/rss/S1N2.xml",        # 미디어오늘(정치)
"https://www.mediatoday.co.kr/rss/S1N3.xml",        # 미디어오늘(경제)
"https://www.mediatoday.co.kr/rss/S1N4.xml",        # 미디어오늘(사회)
"https://www.mediatoday.co.kr/rss/S1N7.xml",        # 미디어오늘(IT과학)
"https://www.mediatoday.co.kr/rss/S1N6.xml",        # 미디어오늘(세계)
"http://rss.edaily.co.kr/edaily_news.xml",   # 이데일리(전체)
"http://www.fnnews.com/rss/new/fn_realnews_all.xml",   # 파이낸셜뉴스(전체)
"https://www.yna.co.kr/rss/politics.xml",   # 연합뉴스(정치)
"https://www.yna.co.kr/rss/economy.xml",    # 연합뉴스(경제)
"https://www.yna.co.kr/rss/industry.xml",   # 연합뉴스(산업)
"https://www.yna.co.kr/rss/international.xml",   # 연합뉴스(세계)
"http://www.yonhapnewstv.co.kr/category/news/politics/feed/",      # 연합뉴스TV(정치)
"http://www.yonhapnewstv.co.kr/category/news/economy/feed/",       # 연합뉴스TV(경제)
"http://www.yonhapnewstv.co.kr/category/news/society/feed/",       # 연합뉴스TV(사회)
"http://www.yonhapnewstv.co.kr/category/news/international/feed/", # 연합뉴스TV(세계)
"https://www.yonhapnewseconomytv.com/rss/allArticle.xml",  # 연합뉴스경제tv(전체)
"https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADER",   # SBS(정치)
"https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02&plink=RSSREADER",   # SBS(경제)
"https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03&plink=RSSREADER",   # SBS(사회)
"https://news-ex.jtbc.co.kr/v1/get/rss/section/10",   # JTBC(정치)
"https://news-ex.jtbc.co.kr/v1/get/rss/section/20",   # JTBC(경제)
"https://news-ex.jtbc.co.kr/v1/get/rss/section/30",   # JTBC(사회)
"http://www.bosa.co.kr/rss/allArticle.xml",      # 의학신문(전체)   
"https://www.hankyung.com/feed/economy",     # 한국경제(경제)
"https://www.hankyung.com/feed/it",          # 한국경제(IT)
"https://www.hankyung.com/feed/politics",    # 한국경제(정치)
"https://www.hankyung.com/feed/society",     # 한국경제(사회)
"https://www.hankyung.com/feed/finance",     # 한국경제(증권)
"https://www.newsis.com/RSS/politics.xml",                    # 뉴시스 정치
"https://www.newsis.com/RSS/economy.xml",                     # 뉴시스 경제
"https://www.newsis.com/RSS/bank.xml",                        # 뉴시스 금융
"https://www.newsis.com/RSS/industry.xml",                    # 뉴시스 산업
"https://www.newsis.com/RSS/society.xml",                     # 뉴시스 사회
"https://www.newsis.com/RSS/health.xml",                      # 뉴시스 바이오-IT
"www.asiae.co.kr/rss/stock.htm",        # 아시아경제(증권)
"www.asiae.co.kr/rss/economy.htm",      # 아시아경제(경제)
"www.asiae.co.kr/rss/industry-IT.htm",  # 아시아경제(산업IT)
"www.asiae.co.kr/rss/politics.htm",     # 아시아경제(정치)
"www.asiae.co.kr/rss/society.htm",      # 아시아경제(사회)
"https://rss.etoday.co.kr/eto/finance_news.xml",       # 이투데이(증권금융)
"https://rss.etoday.co.kr/eto/company_news.xml",       # 이투데이(기업뉴스)
"https://rss.etoday.co.kr/eto/global_news.xml",        # 이투데이(글로벌경제)
"https://rss.etoday.co.kr/eto/political_economic_news.xml",   # 이투데이(정치경제)
"https://rss.etoday.co.kr/eto/social_news.xml",        # 이투데이(사회)
"https://www.newswire.co.kr/rss?md=A31",     # 뉴스와이어(전체)
"https://www.kmib.co.kr/rss/data/kmibPolRss.xml",     # 국민일보(정치)
"https://www.kmib.co.kr/rss/data/kmibEcoRss.xml",     # 국민일보(경제)
"https://www.kmib.co.kr/rss/data/kmibSocRss.xml",     # 국민일보(사회)
"http://rss.moneytoday.co.kr/mt_news.xml",    # 머니투데이(전체)
"https://rss.dt.co.kr/rss/news/Economy.xml",   # 디지털타임즈(경제)
"https://rss.dt.co.kr/rss/news/Industry.xml",  # 디지털타임즈(산업)
"https://rss.dt.co.kr/rss/news/Infotech.xml",  # 디지털타임즈(정보화)
"https://rss.dt.co.kr/rss/news/ICT.xml",       # 디지털타임즈(IT)
"https://rss.dt.co.kr/rss/news/Society.xml",   # 디지털타임즈(사회)
"https://news.einfomax.co.kr/rss/S1N2.xml",         # 연합인포맥스(증권)
"https://news.einfomax.co.kr/rss/S1N7.xml",         # 연합인포맥스(IB기업)
"https://news.einfomax.co.kr/rss/S1N15.xml",        # 연합인포맥스(정책금융)
"http://rss.newspim.com/news/category/101",     #  뉴스핌(정치)
"http://rss.newspim.com/news/category/103",     #  뉴스핌(경제)
"http://rss.newspim.com/news/category/102",     #  뉴스핌(사회)
"http://rss.newspim.com/news/category/107",     #  뉴스핌(글로벌)
"http://rss.newspim.com/news/category/105",     #  뉴스핌(증권금융)
"https://www.mk.co.kr/rss/30100041/",   # 매일경제(경제)
"https://www.mk.co.kr/rss/30200030/",   # 매일경제(정치)
"https://www.mk.co.kr/rss/50400012/",   # 매일경제(사회)
"https://www.mk.co.kr/rss/50100032/",   # 매일경제(기업경영)
"https://www.mk.co.kr/rss/50200011/",   # 매일경제(증권)
"https://www.mk.co.kr/rss/40200003/",   # 매일경제(머니 앤 리치스)
"https://www.businesspost.co.kr/rss/Article_1.xml",    # 비즈니스포스트(글로벌)
"https://www.businesspost.co.kr/rss/Article_2.xml",    # 비즈니스포스트(기후에너지)
"https://www.businesspost.co.kr/rss/Article_3.xml",    # 비즈니스포스트(기업산업)
"https://www.businesspost.co.kr/rss/Article_4.xml",    # 비즈니스포스트(금융)
"https://www.businesspost.co.kr/rss/Article_5.xml",    # 비즈니스포스트(시장과머니)
"https://www.businesspost.co.kr/rss/Article_6.xml",    # 비즈니스포스트(시민과경제)
"https://www.businesspost.co.kr/rss/Article_7.xml",    # 비즈니스포스트(정치사회)
"http://www.joseilbo.com/Contents/rss/rss_tax.php",         # 조세일보(조세회계)
"http://www.joseilbo.com/Contents/rss/rss_finance.php",     # 조세일보(금융증권)
"http://www.joseilbo.com/Contents/rss/rss_industry.php",    # 조세일보(산업)
"http://www.joseilbo.com/Contents/rss/rss_economy.php",     # 조세일보(경제)
"http://www.joseilbo.com/Contents/rss/rss_politics.php",    # 조세일보(정치사회)
"http://rss.etnews.com/02.xml",      # 전자시문(경제)
"http://rss.etnews.com/02027.xml",   # 전자시문(금융)
"http://rss.etnews.com/03.xml",      # 전자시문(IT)
"http://rss.etnews.com/20.xml",      # 전자시문(과학)
"https://www.tokenpost.kr/rss",      # 토큰포스트
"https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",   # 조선일보(전체)
]

def fetch_and_filter_news():
    now = datetime.now(kst)
    five_minutes_ago = now - timedelta(minutes=5)

    for url in news_sites:
        try:
            rss = feedparser.parse(url)
            for entry in rss.entries:
                raw_title = entry.title.strip()
                link = entry.link.strip()

                # 언론사 도메인 구하기
                domain = urlparse(link).netloc

                # YouTube 제거
                if "youtube.com" in link or "youtu.be" in link:
                    continue

                # 게시 시간 필터
                pub_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                if not pub_struct:
                    continue
                pub_datetime = datetime(*pub_struct[:6], tzinfo=pytz.utc).astimezone(kst)
                if pub_datetime < five_minutes_ago or pub_datetime > now:
                    continue

                # 인코딩 문제 있는 사이트들
                if any(site in url for site in ["asiae", "edaily", "infostock"]):
                    try:
                        html = requests.get(link, timeout=5)
                        html.encoding = "euc-kr"
                        soup = BeautifulSoup(html.text, "html.parser")
                        og_title = soup.select_one("meta[property='og:title']")
                        if og_title:
                            raw_title = og_title["content"].strip()
                    except:
                        continue

                # 제목 중복 확인
                if domain in sent_title_map and raw_title in sent_title_map[domain]:
                    continue  # 같은 언론사에서 같은 제목이면 무시

                # 키워드 필터링
                if any(k in raw_title for k in keywords):
                    bot.send_message(chat_id=CHAT_ID, text=f"[{raw_title}]\n{link}")

                    # 저장
                    if domain not in sent_title_map:
                        sent_title_map[domain] = set()
                    sent_title_map[domain].add(raw_title)
                    save_sent_title(domain, raw_title)

        except Exception:
            continue

# 실행 시작
if __name__ == "__main__":
    load_sent_titles()
    while True:
        fetch_and_filter_news()
        time.sleep(3)
