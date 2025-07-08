import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
import pytz
import time
import os
from urllib.parse import urlparse, quote

# 설정
kst = pytz.timezone('Asia/Seoul')
TELEGRAM_TOKEN = "7440645018:AAG_yFBsdyaMmhK_He7lI3EBWggLK9wenXg"
CHAT_ID = "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

# 중복 전송 방지
sent_title_map = {}  # {domain: set([title])}
sent_titles_file = "sent_titles.txt"

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

# 키워드 목록
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

# 네이버 뉴스 RSSHub 링크 생성
news_sites = [f"https://rsshub.app/naver/news/keyword/{quote(k)}" for k in keywords]

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

                # 제목 중복 확인
                if domain in sent_title_map and raw_title in sent_title_map[domain]:
                    continue

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

if __name__ == "__main__":
    load_sent_titles()
    while True:
        fetch_and_filter_news()
        time.sleep(3)
