import requests
import os
import json
import csv # ✅ CSV 저장을 위해 csv 라이브러리를 사용합니다.

# --- 1. 사용자 설정 ---
JIRA_URL = "https://jira.suprema.co.kr"
JIRA_USERNAME = "dhwoo"
JIRA_PASSWORD = "android0237@"

PROJECT_KEY = "COMMONR"
ISSUE_TYPE_NAME = "Test"

JQL_QUERY = f'project = "{PROJECT_KEY}" AND issuetype = "{ISSUE_TYPE_NAME}"'
# ✅ 저장될 CSV 파일 이름을 지정합니다.
OUTPUT_CSV_FILE = "Jira_Test_Cases_Export.csv"
JIRA_AUTH = (JIRA_USERNAME, JIRA_PASSWORD)


# --- 2. Jira에서 모든 이슈 검색 (페이지네이션 적용) ---
def get_all_jira_test_cases(jql):
    """JQL로 모든 이슈를 검색합니다."""
    all_issues = []
    start_at = 0
    max_results = 100

    while True:
        url = f"{JIRA_URL}/rest/api/2/search"
        headers = {"Accept": "application/json"}
        params = {'jql': jql, 'fields': 'summary', 'startAt': start_at, 'maxResults': max_results}

        try:
            response = requests.get(url, headers=headers, params=params, auth=JIRA_AUTH)
            response.raise_for_status()
            data = response.json()
            issues_on_page = data.get('issues', [])
            if not issues_on_page:
                break
            all_issues.extend(issues_on_page)
            start_at += len(issues_on_page)
            print(f"현재까지 {len(all_issues)} / {data['total']} 개 이슈를 가져왔습니다...")
        except requests.exceptions.RequestException as e:
            print(f"Jira 이슈 검색 오류: {e}")
            break
    return all_issues

# --- 3. Xray 상세 스텝 정보 가져오기 ---
def get_xray_test_steps(issue_key):
    """주어진 테스트 케이스의 상세 스텝 정보를 Xray API로 가져옵니다."""
    url = f"{JIRA_URL}/rest/raven/latest/api/test/{issue_key}/step"
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, auth=JIRA_AUTH)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

# --- 4. 모든 내용을 하나의 CSV 파일로 저장 ---
def export_to_csv(issues):
    """가져온 모든 이슈와 스텝을 하나의 CSV 파일로 저장합니다."""
    
    # CSV 파일의 헤더(첫 번째 줄)를 정의합니다.
    header = ['Issue Key', 'Title', 'Step Index', 'Step', 'Data', 'Expected Result']
    
    # utf-8-sig 인코딩으로 Excel에서 한글이 깨지지 않게 합니다.
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(header) # 헤더 쓰기
        
        print(f"\n결과를 '{OUTPUT_CSV_FILE}' 파일에 저장합니다.")
        
        for issue in issues:
            issue_key = issue['key']
            summary = issue['fields'].get('summary', '제목 없음')
            steps = get_xray_test_steps(issue_key)
            
            if not steps:
                # 스텝이 없는 경우, 이슈 정보만 기록합니다.
                writer.writerow([issue_key, summary, '', '', '', ''])
                continue
            
            # 각 스텝을 별도의 행으로 기록합니다.
            for index, step in enumerate(steps):
                step_obj = step.get('step')
                action = step_obj.get('raw', '').strip() if isinstance(step_obj, dict) else 'N/A'

                data_obj = step.get('data')
                data = data_obj.get('raw', '').strip() if isinstance(data_obj, dict) else 'N/A'
                
                result_obj = step.get('result')
                result = result_obj.get('raw', '').strip() if isinstance(result_obj, dict) else 'N/A'
                
                if not action: action = 'N/A'
                if not data: data = 'N/A'
                if not result: result = 'N/A'
                
                writer.writerow([issue_key, summary, index + 1, action, data, result])


# --- 메인 실행 로직 ---
if __name__ == "__main__":
    print(f"✅ [ {PROJECT_KEY} ] 프로젝트의 '{ISSUE_TYPE_NAME}' 이슈를 대상으로 검색을 시작합니다.")
    print(f"JQL 쿼리: {JQL_QUERY}")
    print("-" * 50)

    print("1. Jira에서 모든 테스트 케이스 이슈를 가져옵니다.")
    all_jira_issues = get_all_jira_test_cases(JQL_QUERY)
    
    if all_jira_issues:
        print(f"\n총 {len(all_jira_issues)}개의 테스트 케이스를 모두 찾았습니다.")
        print("2. 모든 내용을 CSV 파일로 저장합니다.")
        export_to_csv(all_jira_issues)
        print(f"\n✅ 완료! '{OUTPUT_CSV_FILE}' 파일이 생성되었습니다.")
    else:
        print("\nJQL에 해당하는 테스트 케이스를 찾지 못했습니다.")