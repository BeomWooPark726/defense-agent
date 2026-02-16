
import feedparser
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
import time

import os

# --- 설정 사항 ---
# GitHub Secrets에서 값을 가져옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 필수 환경변수 확인
if not GEMINI_API_KEY or not SLACK_WEBHOOK_URL:
    print(f"❌ 설정 오류: {'GEMINI_API_KEY' if not GEMINI_API_KEY else ''} {'SLACK_WEBHOOK_URL' if not SLACK_WEBHOOK_URL else ''} 환경변수를 확인해주세요.")
    exit(1)

# (기존 코드와 동일하게 수정을 위한 로컬 변수 제거)

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
    # 월요일이면 주말(3일)치, 아니면 1일치 (테스트용으로 3일치 기본 설정)
    lookback_days = 3 if today.weekday() == 0 else 2 
    since_date = today - timedelta(days=lookback_days)
    
    collected_news = []
    
    print(f"[{today.strftime('%Y-%m-%d')}] 뉴스 수집 시작 (최근 {lookback_days}일 기준)...")
    
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # 기사 게시 날짜 확인 (구조가 다를 수 있어 예외처리)
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

    # 뉴스 텍스트 구성
    context = ""
    for i, item in enumerate(news_list):
        context += f"Source: {item['source']}\nTitle: {item['title']}\nSummary: {item['summary']}\nLink: {item['link']}\n\n"

    prompt = f"""
활동명: 글로벌 국방 전략 에이전트
목표: 국방 빅테크 스타트업을 위해 주요 뉴스를 분석하고 요약한다.

수집된 뉴스 목록을 바탕으로 아래 3개 카테고리에 맞춰 리포트를 작성해줘:
1. Global: 예산, 규제, 구매 동향
2. 벤치마킹: 주요 방산기업 및 스타트업(Anduril, Shield AI 등) 소식 (★가장 우선적으로 비중 높게 다룰 것)
3. 신기술: 국방 관련 신기술 실증 및 연구 (★비중 높게 다룰 것)

[작성 규칙]
- 전체 요약은 10개 내외의 주요 뉴스 항목으로 구성하되, '벤치마킹'과 '신기술' 카테고리의 기사를 우선적으로 풍부하게 선정한다.
- 카테고리 제목(1. Global 등)은 *볼드체*로 작성한다. 예: *1. Global*
- 뉴스 제목 줄의 형식:
  * 뉴스 제목 전체를 *볼드체*로 만든다.
  * 뉴스 제목 자체에 하이퍼링크를 건다. (Slack 형식: <URL|표시할텍스트>)
  * 제목에 관련 국가가 있다면 제목 맨 앞에 해당 국가의 국기 이모지를 넣는다.
  * 예시: *<https://link.com|• 🇺🇸 미국, 새로운 드론 예산 확정>*
- 뉴스 요약(상세 내용) 형식:
  * 제목 바로 아랫줄에 대시(-)를 사용하여 작성한다.
  * 슬랙에서 들여쓰기가 적용되도록 대시 앞에 공백 2개를 넣는다.
- '원문 링크'나 '이미지 참고' 섹션은 아예 삭제한다.

[전체 리포트 예시 형식]
🚀 *글로벌 국방 전략 리포트 (날짜)*

*1. Global*
*<https://link.com|• 🇮🇳 인도, 400억 달러 규모의 라팔 전투기 조달 승인>*
  - 내용...

...

*인사이트*
마지막에 한국 스타트업의 성장에 도움이 될 만한 인사이트를 한 줄로 추가한다.

뉴스 목록:
{context}
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini API 오류 발생: {e}")
        return None

def send_to_slack(text):
    payload = {
        "text": f"🚀 *오늘의 글로벌 국방 뉴스 자동 브리핑* ({datetime.now().strftime('%Y-%m-%d')})\n\n{text}"
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("슬랙 전송 성공!")
    else:
        print(f"슬랙 전송 실패: {response.status_code}, {response.text}")

if __name__ == "__main__":
    raw_news = fetch_news()
    if raw_news:
        print(f"총 {len(raw_news)}개의 뉴스를 요약 중...")
        report = summarize_with_gemini(raw_news)
        if report:
            print("리포트 생성 완료. 슬랙으로 전송합니다.")
            send_to_slack(report)
        else:
            print("리포트 생성에 실패했습니다.")
            exit(1)
    else:
        print("수집된 뉴스가 없습니다.")
