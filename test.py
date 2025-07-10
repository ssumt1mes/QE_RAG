import requests
import json

# --- 1. 사용자 설정 ---
JIRA_URL = "https://jira.suprema.co.kr"
JIRA_USERNAME = "dhwoo"
JIRA_PASSWORD = "android0237@"

# ✅ 스텝이 확실하게 들어있는 테스트 케이스의 ID 하나를 정확히 입력해주세요.
ISSUE_KEY = "COMMONR-375"  # 예시 ID

JIRA_AUTH = (JIRA_USERNAME, JIRA_PASSWORD)

# --- 2. 진단 실행 ---
def diagnose_xray_api_structure(issue_key):
    """하나의 이슈에 대한 Xray API 응답의 전체 데이터 구조를 확인합니다."""
    
    url = f"{JIRA_URL}/rest/raven/latest/api/test/{issue_key}/step"
    headers = {"Accept": "application/json"}
    
    print(f"진단 대상 이슈: {issue_key}")
    print(f"요청 주소: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=headers, auth=JIRA_AUTH)
        response.raise_for_status()
        
        print(f"HTTP 응답 코드: {response.status_code} (성공)")
        print("\n[서버가 반환한 실제 데이터 구조]")
        
        # JSON 데이터를 파싱하여 예쁘게 출력
        # 한글이 깨지지 않도록 ensure_ascii=False 설정
        pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
        print(pretty_json)

    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    diagnose_xray_api_structure(ISSUE_KEY)