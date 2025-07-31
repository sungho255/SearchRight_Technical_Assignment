import pytest
import httpx
import time
import json
import os
import numpy as np # 통계 계산을 위해 numpy 추가

# 테스트 설정
BASE_URL = "http://127.0.0.1:8000"
RUN_COUNT = 5  # 테스트 반복 횟수
SUCCESS_THRESHOLD_SECONDS = 5.0 # 성공 기준 시간 (초)

@pytest.mark.asyncio
async def test_profiling_api_speed():
    """
    /profilling API의 응답 속도를 여러 번 측정하고 평균을 계산하는 테스트.
    """
    api_endpoint = f"{BASE_URL}/profilling"
    
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, "..", "example_datas", "talent_ex4.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except FileNotFoundError:
        pytest.fail(f"테스트 데이터 파일이 없습니다: {json_path}")
    except json.JSONDecodeError:
        pytest.fail(f"JSON 파일 디코딩 오류: {json_path}")

    response_times = []
    print(f"\nAPI 엔드포인트: {api_endpoint}")
    print(f"테스트를 {RUN_COUNT}회 반복합니다...")

    async with httpx.AsyncClient() as client:
        for i in range(RUN_COUNT):
            start_time = time.time()
            try:
                response = await client.post(api_endpoint, json=payload, timeout=30.0)
                response.raise_for_status() # 2xx 이외의 상태 코드에 대해 예외 발생
            except httpx.RequestError as e:
                pytest.fail(f"API 요청 실패 (실행 {i+1}/{RUN_COUNT}): {e}")
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            print(f"  실행 {i+1}/{RUN_COUNT}: {response_time:.4f} 초")

    # 통계 계산
    avg_time = np.mean(response_times)
    min_time = np.min(response_times)
    max_time = np.max(response_times)
    std_dev = np.std(response_times)

    print("\n--- 성능 테스트 결과 ---")
    print(f"평균 응답 시간: {avg_time:.4f} 초")
    print(f"최소 응답 시간: {min_time:.4f} 초")
    print(f"최대 응답 시간: {max_time:.4f} 초")
    print(f"표준 편차: {std_dev:.4f}")
    print("------------------------")

    # 최종 응답 검증 (마지막 응답 기준)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert "output" in response_json
    print("마지막 API 응답 내용 검증 완료.")

    # 성능 기준 검증
    assert avg_time < SUCCESS_THRESHOLD_SECONDS, f"평균 응답 시간({avg_time:.4f}초)이 기준치({SUCCESS_THRESHOLD_SECONDS}초)를 초과했습니다."
