import pandas as pd
import trafilatura
import asyncio
import aiohttp
import os
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 이 스크립트 파일의 절대 경로를 가져옵니다.
script_dir = os.path.dirname(os.path.abspath(__file__))
# 프로젝트 루트 디렉토리 경로를 계산합니다.
project_root = os.path.dirname(os.path.dirname(script_dir))

async def fetch(session, url):
    """
    주어진 URL에서 비동기적으로 콘텐츠를 가져옵니다.

    Args:
        session (aiohttp.ClientSession): HTTP 요청을 위한 클라이언트 세션.
        url (str): 가져올 URL.

    Returns:
        bytes: 성공적으로 가져온 경우 HTML 콘텐츠의 바이트, 그렇지 않으면 None.
    """
    try:
        async with session.get(url, timeout=10, ssl=False) as response:
            if response.status == 200:
                logger.info(f"URL을 성공적으로 가져왔습니다: {url}")
                # 여기서 디코딩하는 대신 원시 바이트를 반환합니다
                return await response.read()
            else:
                logger.warning(f"URL 가져오기 오류 {url}: 상태 {response.status}")
                return None
    except Exception as e:
        logger.error(f"URL 가져오기 오류 {url}: {e}")
        return None

async def main():
    """
    회사 뉴스 CSV 파일을 읽고, 각 링크에서 콘텐츠를 추출하여 새로운 CSV 파일로 저장합니다.
    중복된 링크는 제거됩니다.
    """
    logger.info("read_and_extract_final_attempt 메인 함수 시작.")
    # 프로젝트 루트를 기준으로 파일 경로를 설정합니다.
    input_csv_path = os.path.join(project_root, "example_datas", "company_news.csv")
    output_csv_path = os.path.join(project_root, "example_datas", "company_news_with_content.csv")
    
    try:
        df = pd.read_csv(input_csv_path)
        logger.info(f"{input_csv_path}에서 CSV를 성공적으로 로드했습니다.")
    except FileNotFoundError:
        logger.error(f"입력 CSV 파일을 찾을 수 없습니다: {input_csv_path}")
        return
    
    initial_row_count = len(df)
    # 중복을 제거하고 인덱스를 재설정하여 잠재적인 인덱싱 문제를 방지합니다.
    df.drop_duplicates(subset=['original_link'], keep='first', inplace=True, ignore_index=True)
    final_row_count = len(df)
    logger.info(f"원본 행 수: {initial_row_count}, 중복 제거 후 행 수: {final_row_count}, 제거된 중복 행 수: {initial_row_count - final_row_count}")
    
    urls = df['original_link'].tolist()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        logger.info(f"{len(urls)}개의 URL에서 콘텐츠를 가져오는 중입니다.")
        tasks = [fetch(session, url) for url in urls]
        html_contents_list = await asyncio.gather(*tasks)

        contents = []
        for i, html_bytes in enumerate(html_contents_list):
            if html_bytes:
                try:
                    # 인코딩을 처리하도록 trafilatura에 원시 바이트를 전달합니다.
                    extracted_text = trafilatura.extract(html_bytes, include_comments=False, include_tables=False, include_images=False, favor_precision=True)
                    # 추가하기 전에 extracted_text가 None이 아닌지 확인합니다.
                    contents.append(extracted_text if extracted_text else '')
                    logger.debug(f"URL에서 콘텐츠 추출됨: {urls[i][:50]}...")
                except Exception as e:
                    logger.error(f"URL에서 콘텐츠 추출 오류 {urls[i]}: {e}")
                    contents.append('')
            else:
                # 가져오기 실패 시 콘텐츠를 비워 둡니다.
                contents.append('')
                logger.warning(f"URL에 대한 콘텐츠 가져오기 실패: {urls[i]}")
        
        # 새 'content' 열을 데이터프레임에 직접 할당합니다.
        df['content'] = contents

    # 수정된 데이터프레임을 저장합니다.
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"수정된 DataFrame이 {output_csv_path}에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())