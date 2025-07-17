import os
import csv
import re

# --- 1. 설정 ---
# 소스 .txt 파일들이 들어있는 폴더 이름
INPUT_FOLDER = "Jira_Test_Cases"
# 결과 .csv 파일들이 저장될 폴더 이름
OUTPUT_FOLDER = "Jira_Test_Cases_CSV"


# --- 2. LLM의 '의도' 요약 기능 시뮬레이션 ---
def generate_intent_summary(step_text, data_text, result_text):
    """주어진 스텝, 데이터, 결과 텍스트를 바탕으로 핵심 의도를 요약합니다."""
    # 간단한 규칙 기반 요약 예시 (실제로는 더 복잡한 LLM 로직)
    if "설정" in step_text and "적용되는지" in result_text:
        return f"다양한 설정을 적용하고 정상적으로 반영되는지 검증"
    if "접근" in step_text and "실패" in result_text:
        return f"특정 조건에서 사용자의 메뉴 접근이 권한에 따라 실패하는지 확인"
    if "접근" in step_text and ("가능해야" in result_text or "표시가 되어야" in result_text):
        return f"특정 조건에서 권한 있는 사용자가 메뉴에 정상 접근하는지 확인"
    if "오류 메세지를 표시" in result_text:
        return f"잘못된 조건이나 권한 없는 접근 시, 정확한 오류 메시지가 출력되는지 검증"
    # 일반적인 경우
    return f"'{step_text.splitlines()[0]}' 실행 시 '{result_text.splitlines()[0]}' 결과가 나오는지 확인"


# --- 3. 단일 .txt 파일 파싱 및 데이터 처리 ---
def process_single_file(file_path):
    """하나의 .txt 파일을 읽고 파싱하여 구조화된 데이터로 반환합니다."""
    all_steps_data = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        issue_key = re.search(r"■ 이슈 키: (.*?)\n", content).group(1)
        title = re.search(r"■ 제목: (.*?)\n", content).group(1)
        steps_raw_block = content.split("■ 테스트 스텝\n\n")[1]
        steps_list = steps_raw_block.strip().split("------------------------------------------------------------\n")
    except (AttributeError, IndexError):
        print(f"경고: '{os.path.basename(file_path)}' 파일의 형식이 맞지 않아 건너뜁니다.")
        return None

    for step_block in steps_list:
        if not step_block.strip():
            continue

        step_index = re.search(r"\[Step (\d+)\]\n", step_block).group(1) if re.search(r"\[Step (\d+)\]\n", step_block) else "N/A"
        
        step_text = re.search(r"스텝 \(Step\)\n(.*?)\n\n데이터", step_block, re.DOTALL)
        step_text = step_text.group(1).strip() if step_text else "N/A"

        data_text = re.search(r"데이터 \(Data\)\n(.*?)\n\n예상 결과", step_block, re.DOTALL)
        data_text = data_text.group(1).strip() if data_text else "N/A"
        
        result_text = re.search(r"예상 결과 \(Expected Result\)\n(.*)", step_block, re.DOTALL)
        result_text = result_text.group(1).strip() if result_text else "N/A"
        
        #intent = generate_intent_summary(step_text, data_text, result_text)
        
        all_steps_data.append([
            issue_key, title, step_index, step_text, data_text, result_text
        ])
        
    return all_steps_data


# --- 4. 단일 CSV 파일로 저장 ---
def save_to_csv(data, output_path):
    """처리된 데이터를 지정된 경로의 CSV 파일로 저장합니다."""
    header = ['Issue Key', 'Title', 'Step Index', 'Step', 'Data', 'Expected Result']
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


# --- 메인 실행 로직 ---
if __name__ == "__main__":
    # 입력 폴더 존재 여부 확인
    if not os.path.exists(INPUT_FOLDER):
        print(f"오류: 입력 폴더 '{INPUT_FOLDER}'를 찾을 수 없습니다. 폴더를 생성하고 .txt 파일을 넣어주세요.")
        exit()

    # 출력 폴더 생성
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    print(f"'{INPUT_FOLDER}' 폴더의 .txt 파일들을 변환합니다...")
    
    # 입력 폴더의 모든 파일을 순회
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".txt"):
            input_path = os.path.join(INPUT_FOLDER, filename)
            
            # 1. 단일 파일 처리
            processed_data = process_single_file(input_path)
            
            # 2. 처리된 데이터가 있으면 CSV로 저장
            if processed_data:
                base_name = os.path.splitext(filename)[0]
                output_filename = f"{base_name}.csv"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                save_to_csv(processed_data, output_path)
                print(f"  - '{filename}'  ->  '{output_filename}' 변환 완료")

    print("\n✅ 모든 파일 변환이 완료되었습니다.")