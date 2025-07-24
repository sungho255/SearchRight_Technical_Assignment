import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def chunk_and_save_csv():
    """
    CSV 파일을 읽고, 제목과 내용을 결합한 후, 결합된 텍스트를 청크로 나누어
    새로운 CSV 파일에 저장합니다.

    이 함수는 다음 단계를 수행합니다:
    1. 지정된 경로에서 CSV 파일을 읽습니다.
    2. 'title'과 'content' 열을 결합하여 'full_text' 열을 생성합니다.
    3. RecursiveCharacterTextSplitter를 사용하여 'full_text'를 청크로 분할합니다.
    4. 각 청크와 원본 행의 메타데이터를 포함하는 새로운 데이터프레임을 생성합니다.
    5. 청크된 데이터를 새 CSV 파일로 저장합니다.

    Args:
        None

    Returns:
        None
    """
    logger.info("chunk_and_save_csv 프로세스 시작.")
    # 파일 경로 정의
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # util 디렉토리의 상위 디렉토리인 searchright_technical_assignment를 기준으로 경로 설정
    base_dir = os.path.dirname(script_dir)
    input_csv_path = os.path.join(base_dir, '..', 'example_datas', 'company_news_with_content.csv')
    output_csv_path = os.path.join(base_dir, '..', 'example_datas', 'company_news_with_content_chunked.csv')

    # 1. CSV 파일 읽기
    try:
        df = pd.read_csv(input_csv_path)
        logger.info("CSV 파일을 성공적으로 읽었습니다.")
    except FileNotFoundError:
        logger.error(f"오류: '{input_csv_path}'를 찾을 수 없습니다.")
        return

    # 2. 제목과 내용 결합 (NaN 값 처리 포함)
    df['full_text'] = df['title'].fillna('') + " " + df['content'].fillna('')
    logger.info("제목과 내용을 결합했습니다.")

    # 3. 텍스트를 청크로 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,  # 컨텍스트 보존을 위해 약간의 겹침 추가
        length_function=len,
    )
    logger.info("텍스트를 청크로 분할합니다.")

    new_rows = []
    for index, row in df.iterrows():
        # 원본 메타데이터 유지
        original_data = row.to_dict()
        # 청크로 대체될 텍스트 필드 제거
        original_data.pop('full_text', None)
        original_data.pop('content', None)
        
        chunks = text_splitter.split_text(row['full_text'])
        for i, chunk in enumerate(chunks):
            new_row = original_data.copy()
            new_row['chunked_content'] = chunk
            new_row['chunk_index'] = i
            new_rows.append(new_row)
    logger.info(f"총 {len(new_rows)}개의 청크를 생성했습니다.")

    # 4. 청크 데이터로 새 데이터프레임 생성
    new_df = pd.DataFrame(new_rows)

    # 5. 새 데이터프레임을 새 CSV 파일에 저장
    new_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

    logger.info(f"청크된 CSV 파일을 성공적으로 생성했습니다: {output_csv_path}")

if __name__ == "__main__":
    chunk_and_save_csv()