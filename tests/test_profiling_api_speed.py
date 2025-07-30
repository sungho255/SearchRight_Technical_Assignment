import pytest
import httpx
import time
import json
import os

# FastAPI 애플리케이션이 실행 중인 주소 (개발 환경에 따라 변경될 수 있습니다)
# 일반적으로 Uvicorn으로 실행하면 http://127.0.0.1:8000 입니다.
BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_profiling_api_speed():
    """
    /profilling API의 응답 속도를 측정하는 테스트.
    """
    api_endpoint = f"{BASE_URL}/profilling"
    
    # 테스트에 사용할 샘플 데이터 로드
    # 프로젝트 루트 디렉토리에서 example_datas/talent_ex1.json 경로를 찾습니다.
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, "..", "example_datas", "talent_ex4.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except FileNotFoundError:
        pytest.fail(f"테스트 데이터 파일이 없습니다: {json_path}")
    except json.JSONDecodeError:
        pytest.fail(f"JSON 파일 디코딩 오류: {json_path}")

    print(f"\nAPI 엔드포인트: {api_endpoint}")
    print(f"페이로드 크기: {len(json.dumps(payload))} bytes")

    async with httpx.AsyncClient() as client:
        start_time = time.time()
        try:
            response = await client.post(api_endpoint, json=payload, timeout=30.0) # 타임아웃 설정
        except httpx.ConnectError as e:
            pytest.fail(f"API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요: {e}")
        except httpx.TimeoutException:
            pytest.fail(f"API 요청이 {30.0}초 안에 완료되지 않았습니다. 타임아웃 발생.")
        
        end_time = time.time()
        response_time = end_time - start_time

        print(f"응답 시간: {response_time:.4f} 초")
        print(f"응답 상태 코드: {response.status_code}")
        
        assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}, 응답: {response.text}"
        
        response_json = response.json()
        assert response_json["status"] == "success", f"API 응답 상태가 'success'가 아닙니다: {response_json}"
        assert "output" in response_json, "응답에 'output' 필드가 없습니다."
        
        print("API 응답이 성공적입니다.")
        print(f"응답 내용 미리보기: {str(response_json['output'])[:200]}...") # 응답 내용 일부 출력
