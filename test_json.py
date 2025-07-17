import requests
import json
import os

# --- 1. 사용자 설정 ---
# 이 섹션의 값들은 사용자의 환경에 맞게 수정해주세요.
JIRA_URL = "https://jira.suprema.co.kr"
JIRA_USERNAME = "dhwoo"
JIRA_PASSWORD = "android0237@" # 실제 운영 환경에서는 비밀번호를 코드에 직접 넣는 것을 권장하지 않습니다.

# Jira 인증 정보
JIRA_AUTH = (JIRA_USERNAME, JIRA_PASSWORD)

# 검색할 JQL 쿼리
JQL_QUERY = 'project = "COMMONR" AND issuetype = "Test"'

# 최종 결과가 저장될 폴더 이름
OUTPUT_FOLDER = "jira_issues_output" # 저장 폴더 이름을 더 명확하게 변경
# ---------------------

def get_all_jira_issue_keys(jql):
    """JQL로 모든 이슈를 검색하여 이슈 키 리스트를 반환합니다."""
    all_issue_keys = []
    start_at = 0
    max_results = 100

    print(f"JQL로 이슈 검색을 시작합니다: {jql}")

    while True:
        url = f"{JIRA_URL}/rest/api/2/search"
        headers = {"Accept": "application/json"}
        # 'key' 필드만 요청하여 검색 속도를 높입니다.
        params = {'jql': jql, 'fields': 'key', 'startAt': start_at, 'maxResults': max_results}

        try:
            response = requests.get(url, headers=headers, params=params, auth=JIRA_AUTH)
            response.raise_for_status()
            data = response.json()
            issues_on_page = data.get('issues', [])
            
            if not issues_on_page:
                break # 더 이상 가져올 이슈가 없으면 중단
            
            # 이슈 객체에서 'key' 값만 추출하여 리스트에 추가
            keys_on_page = [issue['key'] for issue in issues_on_page]
            all_issue_keys.extend(keys_on_page)
            
            start_at += len(issues_on_page)
            print(f"  -> 현재까지 {len(all_issue_keys)} / {data['total']} 개 이슈 키를 가져왔습니다...")
            
        except requests.exceptions.RequestException as e:
            print(f"Jira 이슈 검색 오류: {e}")
            return None # 오류 발생 시 None 반환
            
    return all_issue_keys

def get_jira_issue_json(issue_key):
    """
    하나의 이슈 키에 대한 모든 정보를 Jira API를 통해 가져옵니다. (이 함수가 변경되었습니다)
    """
    # Jira 기본 API를 사용하여 이슈의 전체 정보를 요청합니다.
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=JIRA_AUTH)
        response.raise_for_status()
        # 성공 시, 이슈의 전체 JSON 데이터를 반환합니다.
        return response.json() 
    except requests.exceptions.RequestException as e:
        print(f"'{issue_key}'의 정보 조회 중 오류 발생: {e}")
        # 실패 시, None을 반환합니다.
        return None

def save_data_to_json(data, filename):
    """주어진 데이터를 JSON 파일로 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"'{filename}' 파일 저장 중 오류 발생: {e}")
        return False

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    # 1. JQL로 모든 테스트 케이스 이슈 키 검색
    issue_keys = get_all_jira_issue_keys(JQL_QUERY)
    
    if issue_keys:
        # 2. 결과를 저장할 폴더 생성
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        print(f"\n총 {len(issue_keys)}개의 이슈를 대상으로 전체 정보 저장을 시작합니다.")
        print(f"저장 폴더: '{os.path.abspath(OUTPUT_FOLDER)}'")
        
        success_count = 0
        
        # 3. 각 이슈 키를 순회하며 전체 정보 가져오고 개별 파일로 저장
        for i, key in enumerate(issue_keys):
            print(f"[{i+1}/{len(issue_keys)}] '{key}' 전체 정보 조회 중...")
            # 변경된 함수를 호출합니다.
            issue_data = get_jira_issue_json(key)
            
            # issue_data가 정상적으로 반환되었는지 확인합니다.
            if issue_data is not None:
                # 파일 경로 설정 (예: jira_issues_output/COMMONR-375.json)
                output_filepath = os.path.join(OUTPUT_FOLDER, f"{key}.json")
                
                if save_data_to_json(issue_data, output_filepath):
                    success_count += 1
        
        print(f"\n✅ 모든 작업 완료! 총 {len(issue_keys)}개 중 {success_count}개의 파일이 성공적으로 저장되었습니다.")
            
    else:
        print("\nJQL 검색 결과, 조회할 이슈가 없습니다.")
