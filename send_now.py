
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_to_slack(text):
    payload = {
        "text": f"🚀 *오늘의 글로벌 국방 뉴스 자동 브리핑* ({datetime.now().strftime('%Y-%m-%d')})\n\n{text}"
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("슬랙 전송 성공!")
    else:
        print(f"슬랙 전송 실패: {response.status_code}, {response.text}")

report = """
### **[2026. 02. 14. 국방 전략 리포트]**

#### **1. Global: 예산, 규제, 구매 동향**
*   **🇮🇳 인도, 400억 달러 규모의 라팔 전투기 및 P-8I 초계기 도입 승인**
    *   인도가 114대의 라팔 전투기와 6대의 P-8I 해상초계기 구매를 공식 승인하며 아시아권 해공군력 판도를 바꾸고 있습니다. 글로벌 방산 시장의 거대 자본이 아시아권으로 집중되고 있음을 시사합니다.
    *   *이미지 참고:* 인도 공군 문장이 선명하게 박힌 라팔(Rafale) 전투기의 측면 사진
    *   *원문 링크:* https://www.navalnews.com/naval-news/2026/02/india-set-to-order-114-rafale-fighters-and-six-p-8i-patrol-aircraft/
*   **🇧🇪 벨기에, 추가 F-35 도입 조건으로 '유럽 중심 공급망' 강력 요구**
    *   벨기에 국방장관은 추가 도입할 스텔스기가 단순 구매를 넘어 유럽 방위 산업 생태계와 통합되어야 함을 강조하며 기술 주권 이슈를 제기했습니다.
    *   *이미지 참고:* 비행 중인 F-35 스텔스 전투기의 고화질 이미지
    *   *원문 링크:* https://breakingdefense.com/2026/02/belgium-wants-additional-f-35-jets-to-be-as-european-as-possible-says-defense-minister/

#### **2. 벤치마킹: 주요 기업 및 스타트업 소식**
*   **🤖 미 해군 무인 수상함(Robot-Boat) 수주를 향한 스타트업들의 무한 경쟁**
    *   Blue Water Autonomy 등 신흥 강자들이 미 해군의 자율 함정 수요에 맞춰 저비용 자율 주행 선박 솔루션을 경쟁적으로 선보이고 있습니다. 하드웨어보다 자율 주행 알고리즘의 신뢰성이 성패를 가릅니다.
    *   *이미지 참고:* 거대 무인 선박 'Liberty USV'가 바다 위를 가르는 컨셉 아트
    *   *원문 링크:* https://www.defenseone.com/business/2026/02/crowded-field-robot-boat-makers-vying-navys-attention/411390/
*   **🚀 Anduril, 'Arsenal-1' 소프트웨어 정의 공장 가동 1주년 성과 발표**
    *   안두릴은 제조 시설 혁신을 통해 방산 장비 생산 속도를 소프트웨어 업데이트만큼 빠르게 혁신하고 있음을 선언했습니다. 대량 생산 능력이 스타트업의 핵심 자산입니다.
    *   *이미지 참고:* 안두릴의 대규모 제조 시설 공사 현장 사진
    *   *원문 링크:* https://www.anduril.com/news/arsenal-1-one-year-in

#### **3. 신기술: 국방 관련 신기술 실증 및 연구**
*   **⚓️ Aselsan, 무인기에서 투하하여 잠수함 잡는 'aselBUOY' 실증 임박**
    *   터키 아셀산이 드론에서 투하하여 적 잠수함을 탐지하는 새로운 대잠전 기술의 최종 테스트에 착수했습니다. 대잠전의 무인화가 빠르게 진행 중입니다.
    *   *이미지 참고:* WDS 2026 전시회에서 공개된 수중 음향 시스템 전시 부스
    *   *원문 링크:* https://www.navalnews.com/naval-news/2026/02/aselsan-tests-of-aselbuoy-sonobuoys-from-uav-are-imminent/

---
**💡 한국 스타트업 관점의 오늘자 One-liner**
"소프트웨어 정의 제조(Arsenal)와 저비용 자율 알고리즘 경쟁이 스타트업이 글로벌 방산 시장을 흔드는 강력한 무기가 되고 있습니다."
"""

if __name__ == "__main__":
    send_to_slack(report)
