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
error_log_file = "error_log.txt"

# 1일 기준
def load_sent_titles():
    global sent_title_map
    now = datetime.now(kst)
    cutoff = now - timedelta(days=1)

    if os.path.exists(sent_titles_file):
        with open(sent_titles_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        # 파일이 없으면 생성
        open(sent_titles_file, "w", encoding="utf-8").close()
        lines = []

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
        except Exception as e:
            log_error(f"날짜 파싱 오류: {line} / {str(e)}")
            continue

    with open(sent_titles_file, "w", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line + "\n")

def save_sent_title(domain, title):
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(sent_titles_file, "a", encoding="utf-8") as f:
            f.write(f"{domain}|{title}|{now_str}\n")
    except Exception as e:
        log_error(f"sent_title 저장 실패: {domain} | {title} | {str(e)}")

def log_error(message):
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    with open(error_log_file, "a", encoding="utf-8") as f:
        f.write(f"[{now_str}] {message}\n")

# 키워드
keywords = [ "2차전지", "韓", "中", "배터리", "4인뱅", "저출산", "인구정책", "K콘텐츠", "출산", "특징주", 
"4인터넷", "5G", "AI", "AI고속도로", "AI반도체", "AR", "AWS", "BMS", "ESS", "FDA승인", "GPT", "GPT칩", "IRA", 
"K문화", "K뷰티", "K콘텐츠", "LNG", "NFT", "SG", "SMR", "SOC", "STO", "VR", "ai", "ai고속도로", "ai반도체", 
"ar", "aws", "bms", "블록체인", "챗GPT", "구글", "국내최초", "국가전략산업", "국산화", "데이터센터", "대북지원", 
"대왕고래", "대통령", "대체에너지", "딥러닝", "라이다", "로보택시", "로봇", "로봇눈", "로봇손", "마귀상어", 
"메타", "메타버스", "면역항암제", "모빌리티", "바이오", "방사능", "방산", "백신", "북극항로", "블랙웰", 
"비만치료제", "사이버보안", "산불", "상용화", "생명공학", "석유", "세계최대", "세계최초", "스마트공장", 
"스마트시티", "스마트안경", "스마트팩토리", "스마트팜", "속보", "수소", "수출계약", "수출공시", "수출허가", 
"수해", "스테이블코인", "스타트업", "시황", "실시간 속보", "신약", "안전", "알래스카", "알츠하이머", 
"애플", "양자컴퓨터", "에너지고속도로", "에너지정책", "에너지안보", "에너지저장장치", "엔비디아", "여론", 
"예비타당성", "옵티머스", "원유", "원전", "원전건설", "원전해체", "유전자치료", "이차전지", "이재명", 
"인터넷은행", "임상", "임상1상", "임상2상", "임상3상", "임상완료", "자율주행", "자동차", "재건", "재난", 
"재생에너지", "전기차", "전력", "전력망", "전선", "전자결제", "전쟁", "전쟁위험", "정비사업", "정부주도", 
"정부지원", "제재완화", "제재해제", "지역화폐", "지능형로봇", "지진", "진단기기", "진단시약", "진단키트", 
"차세대배터리", "챗gpt", "철강", "초고속인터넷", "초소형모듈원자로", "초전도체", "치매", "친환경에너지", 
"카카오페이", "카지노", "클라우드", "키오스크", "탄소배출권", "탄소중립", "탄소세", "탄소포집", "테슬라", 
"트럼프", "특허", "특허등록", "특허취득", "특허획득", "특징주", "투자유치", "핀테크", "핑크퐁", "풍력", 
"퓨리오사", "해상풍력", "해저터널", "해외수주", "핵심기술", "핵심소재", "핵폐기물", "화장품", "환경규제", 
"황사", "황사경보", "황사주의보", "황사특보", "황사피해", "휴머노이드", "휴전", "희토류", "잭슨황", 
"우주항공", "항공사", "항공우주", "한류", "한한령", "생명과학", "줄기세포", "mRNA", "ms", "네이버페이", 
"리튬", "니켈", "도시재생", "규제완화", "감세", "세제혜택", "李", "兆", "美", "한미", "폭염", "러시아", 
"우크라이나", "세종이전", "구리", "K반도체", "피부암", "피부암 재생", "피부재생", "연골재생", "플랫폼", "동물대체", "식약처", "재생의료", "장기재생", "동물시험", "친환경소재", "플라스틱", "선박", "조선", "드론", "헬스케어", "인공장기", "장기이식", "이스라엘", "이란", "하마스", "중국", "신약개발", "세포치료제", "항체치료제", "토큰", "디지털자산", "가상화폐", "철강", "가스" ]  # (사용자 제공 키워드 그대로 유지 — 생략 없이 포함됨)

# RSS 사이트 리스트
news_sites = [ "https://www.asiae.co.kr/rss/all.xml",
"https://rss.etnews.com/ETnews.xml",
"https://www.hankyung.com/feed",
"https://www.edaily.co.kr/rss/news.xml",
"https://www.infostockdaily.co.kr/rss/allArticle.xml",
"https://www.yonhapnewstv.co.kr/browse/feed/",
"https://www.mk.co.kr/rss/30000001/",
"https://www.fntimes.com/rss/allArticle.xml",
"https://rss.mt.co.kr/rss/mt.xml",
"https://www.yna.co.kr/pg/rss",
"https://www.asiatoday.co.kr/rss/rss.xml",
"https://rss.mk.co.kr",
"https://www.tokenpost.kr/rss",
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
"https://www.khan.co.kr/rss/rssdata/kh_news.xml",
"https://www.asiae.co.kr/news/rss/asia_rss.htm",
"https://rss.etnews.com/Section902.xml",
"https://rss.etnews.com/Section901.xml",
"https://rss.etnews.com/Section903.xml",
"https://rss.etnews.com/Section904.xml",
"https://rss.hankyung.com/new/news_stock.xml",
"https://rss.hankyung.com/new/news_economy.xml",
"https://rss.hankyung.com/new/news_industry.xml",
"https://rss.hankyung.com/new/news_intl.xml",
"https://rss.hankyung.com/new/news_politics.xml",
"https://rss.fnnews.com/rss/new/fn_realnews_all.xml",
"https://rss.fnnews.com/rss/new/fn_realnews_economy.xml",
"https://rss.fnnews.com/rss/new/fn_realnews_politics.xml",
"https://rss.fnnews.com/rss/new/fn_realnews_it.xml",
"https://rss.edaily.co.kr/edaily_news.xml",
"https://rss.edaily.co.kr/stock_news.xml",
"https://rss.edaily.co.kr/economy_news.xml",
"https://rss.edaily.co.kr/finance_news.xml",
"https://rss.edaily.co.kr/bondfx_news.xml",
"https://rss.edaily.co.kr/enterprise_news.xml",
"https://rss.edaily.co.kr/world_news.xml",
"https://rss.edaily.co.kr/realestate_news.xml",
"https://rss.edaily.co.kr/happypot_news.xml",
"https://rss.edaily.co.kr/edaily_column.xml",
"https://file.mk.co.kr/news/rss/rss_30100041.xml",
"https://file.mk.co.kr/news/rss/rss_30200030.xml",
"https://file.mk.co.kr/news/rss/rss_30300018.xml",
"https://file.mk.co.kr/news/rss/rss_30000023.xml",
"https://file.mk.co.kr/news/rss/rss_50200011.xml",
"https://file.mk.co.kr/news/rss/rss_50300009.xml",
"https://file.mk.co.kr/news/rss/rss_71000001.xml",
"https://www.fnnews.com/rss/new/fn_realnews_stock.xml",
"https://www.fnnews.com/rss/new/fn_realnews_finance.xml", ]  # (사용자 제공 사이트 그대로 유지 — 생략 없이 포함됨)

def fetch_and_filter_news():
    now = datetime.now(kst)

    for url in news_sites:
        try:
            rss = feedparser.parse(url)
            for entry in rss.entries:
                raw_title = entry.title.strip()
                link = entry.link.strip()

                domain = urlparse(link).netloc

                if "youtube.com" in link or "youtu.be" in link:
                    continue

                pub_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                if not pub_struct:
                    continue

                pub_datetime = datetime(*pub_struct[:6], tzinfo=pytz.utc).astimezone(kst)

                # 발행시간 기준 확인 (5분 제한 제거 → 중복만 확인)
                if pub_datetime > now:
                    continue  # 미래 시간 방지

                # 인코딩 보정
                if any(site in url for site in ["asiae", "edaily", "infostock"]):
                    try:
                        html = requests.get(link, timeout=5)
                        html.encoding = "euc-kr"
                        soup = BeautifulSoup(html.text, "html.parser")
                        og_title = soup.select_one("meta[property='og:title']")
                        if og_title:
                            raw_title = og_title["content"].strip()
                    except Exception as e:
                        log_error(f"인코딩 처리 실패: {link} / {str(e)}")
                        continue

                # 중복 확인
                if domain in sent_title_map and raw_title in sent_title_map[domain]:
                    continue

                if any(k in raw_title for k in keywords):
                    try:
                        bot.send_message(chat_id=CHAT_ID, text=f"[{raw_title}]\n{link}")
                        if domain not in sent_title_map:
                            sent_title_map[domain] = set()
                        sent_title_map[domain].add(raw_title)
                        save_sent_title(domain, raw_title)
                    except Exception as e:
                        log_error(f"텔레그램 전송 실패: {raw_title} / {str(e)}")
                        continue

        except Exception as e:
            log_error(f"RSS 처리 오류: {url} / {str(e)}")
            continue

# 실행
if __name__ == "__main__":
    load_sent_titles()
    while True:
        fetch_and_filter_news()
        time.sleep(5)
