
import feedparser
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 설정 사항 ---
# GitHub Secrets에서 값을 가져옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 이메일 설정
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME") # 발송 이메일
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # 앱 비밀번호
EMAIL_RECEIVER = "beomwoo.park@bonerobotics.ai"

# 필수 환경변수 확인
if not GEMINI_API_KEY or not EMAIL_USERNAME or not EMAIL_PASSWORD:
    print(f"❌ 설정 오류: 필수 환경변수(GEMINI_API_KEY, EMAIL_USERNAME, EMAIL_PASSWORD)를 확인해주세요.")
    exit(1)

RSS_FEEDS = {
    "Breaking Defense": "https://breakingdefense.com/feed/",
    "Defense One": "https://www.defenseone.com/rss/all/",
    "Naval News": "https://www.navalnews.com/feed/",
    "Anduril Blog": "https://blog.anduril.com/feed/"
}

# Gemini AI 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def fetch_news():
    today = datetime.now()
    # 월요일이면 주말(3일)치, 아니면 1일치
    lookback_days = 3 if today.weekday() == 0 else 2 
    since_date = today - timedelta(days=lookback_days)
    
    collected_news = []
    
    print(f"[{today.strftime('%Y-%m-%d')}] 뉴스 수집 시작 (최근 {lookback_days}일 기준)...")
    
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            
            if published and published > since_date:
                collected_news.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary if 'summary' in entry else ""
                })
        print(f"- {source}: {len(feed.entries)}개 기사 확인됨")
                
    return collected_news

def summarize_with_gemini(news_list):
    if not news_list:
        return "최근 수집된 뉴스가 없습니다."

    context = ""
    for i, item in enumerate(news_list):
        context += f"Source: {item['source']}\nTitle: {item['title']}\nSummary: {item['summary']}\nLink: {item['link']}\n\n"

    prompt = f"""
활동명: 글로벌 국방 전략 에이전트
목표: 국방 빅테크 스타트업을 위해 주요 뉴스를 분석하고 요약한다.

수집된 뉴스 목록을 바탕으로 아래 3개 카테고리에 맞춰 이메일 본문용 리포트를 작성해줘:
1. Global: 예산, 규제, 구매 동향
2. 벤치마킹: 주요 방산기업 및 스타트업(Anduril, Shield AI 등) 소식 (★가장 우선적으로 비중 높게 다룰 것)
3. 신기술: 국방 관련 신기술 실증 및 연구 (★비중 높게 다룰 것)

[작성 규칙]
- 전체 요약은 10개 내외의 주요 뉴스 항목으로 구성한다.
- 카테고리 제목(1. Global 등)은 볼드체로 작성한다.
- 뉴스 제목 줄의 형식:
  * [국가 국기] [제목](링크) 형식의 표준 마크다운을 사용한다.
  * 예시: 🇺🇸 [미국, 새로운 드론 예산 확정](https://link.com)
- 뉴스 요약(상세 내용) 형식:
  * 제목 바로 아랫줄에 대시(-)를 사용하여 작성한다.
- 마지막에 한국 스타트업의 성장에 도움이 될 만한 인사이트를 한 줄로 추가한다.

뉴스 목록:
{context}
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API 오류 발생: {e}")
        return None

def send_email(text):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"🚀 [자동 브리핑] 글로벌 국방 전략 리포트 ({datetime.now().strftime('%Y-%m-%d')})"

    # 마크다운 텍스트를 이메일 본문에 삽입 (간단히 텍스트로 전송하거나 HTML 변환 필요)
    # 여기서는 가독성을 위해 텍스트 형식으로 보냅니다.
    msg.attach(MIMEText(text, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("이메일 전송 성공!")
    except Exception as e:
        print(f"이메일 전송 실패: {e}")

if __name__ == "__main__":
    raw_news = fetch_news()
    if raw_news:
        print(f"총 {len(raw_news)}개의 뉴스를 요약 중...")
        report = summarize_with_gemini(raw_news)
        if report:
            print("리포트 생성 완료. 이메일로 전송합니다.")
            send_email(report)
        else:
            print("리포트 생성에 실패했습니다.")
            exit(1)
    else:
        print("수집된 뉴스가 없습니다.")
