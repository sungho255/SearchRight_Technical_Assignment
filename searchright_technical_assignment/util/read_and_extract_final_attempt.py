import pandas as pd
import trafilatura
import asyncio
import aiohttp
import chardet
import os

# 이 스크립트 파일의 절대 경로를 가져옵니다.
script_dir = os.path.dirname(os.path.abspath(__file__))
# 프로젝트 루트 디렉토리 경로를 계산합니다.
project_root = os.path.dirname(os.path.dirname(script_dir))

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10, ssl=False) as response:
            if response.status == 200:
                # 여기서 디코딩하는 대신 원시 바이트를 반환합니다
                return await response.read()
            else:
                print(f"URL 가져오기 오류 {url}: 상태 {response.status}")
                return None
    except Exception as e:
        print(f"URL 가져오기 오류 {url}: {e}")
        return None

async def main():
    # 프로젝트 루트를 기준으로 파일 경로를 설정합니다.
    input_csv_path = os.path.join(project_root, "example_datas", "company_news.csv")
    output_csv_path = os.path.join(project_root, "example_datas", "company_news_with_content.csv")
    
    df = pd.read_csv(input_csv_path)
    
    initial_row_count = len(df)
    # 중복을 제거하고 인덱스를 재설정하여 잠재적인 인덱싱 문제를 방지합니다.
    df.drop_duplicates(subset=['original_link'], keep='first', inplace=True, ignore_index=True)
    final_row_count = len(df)
    print(f"원본 행 수: {initial_row_count}, 중복 제거 후 행 수: {final_row_count}, 제거된 중복 행 수: {initial_row_count - final_row_count}")
    
    urls = df['original_link'].tolist()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
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
                except Exception as e:
                    print(f"URL에서 콘텐츠 추출 오류 {urls[i]}: {e}")
                    contents.append('')
            else:
                # 가져오기 실패 시 콘텐츠를 비워 둡니다.
                contents.append('')
        
        # 새 'content' 열을 데이터프레임에 직접 할당합니다.
        df['content'] = contents

    # 수정된 데이터프레임을 저장합니다.
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    asyncio.run(main())