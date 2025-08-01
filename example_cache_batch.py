import time
import functools
from typing import List

# --- 1. 캐싱 성능 비교 (Caching Performance Comparison) ---

# 캐시가 적용되지 않은 일반 함수
def fetch_data_from_db_no_cache(item_id: int):
    """DB에서 데이터를 가져오는 것을 시뮬레이션 (캐시 없음)"""
    print(f"[캐시 미적용] ID '{item_id}' 데이터 요청 중... (1초 소요)")
    time.sleep(1)
    return f"데이터: {item_id}"

# @functools.lru_cache 데코레이터로 캐시가 적용된 함수
@functools.lru_cache(maxsize=128)
def fetch_data_from_db_with_cache(item_id: int):
    """DB에서 데이터를 가져오는 것을 시뮬레이션 (캐시 적용)"""
    print(f"[캐시 적용] ID '{item_id}' 데이터 요청 중... (1초 소요)")
    time.sleep(1)
    return f"데이터: {item_id}"

def run_caching_comparison():
    """캐싱 적용 전/후의 성능을 비교하는 예제"""
    print("--- 1. 캐싱(Caching) 성능 비교 시작 ---")
    ids_to_fetch = [101, 102, 101, 103, 102, 101]
    print(f"요청할 ID 목록: {ids_to_fetch}\n")

    # 1. 캐시 미적용 테스트
    print("--- 캐시 미적용 테스트 시작 ---")
    start_time = time.time()
    for item_id in ids_to_fetch:
        fetch_data_from_db_no_cache(item_id)
    no_cache_duration = time.time() - start_time
    print(f"--- 캐시 미적용 테스트 종료 ---\n")

    # 2. 캐시 적용 테스트
    print("--- 캐시 적용 테스트 시작 ---")
    start_time = time.time()
    for item_id in ids_to_fetch:
        fetch_data_from_db_with_cache(item_id)
    cache_duration = time.time() - start_time
    print(f"--- 캐시 적용 테스트 종료 ---\n")

    # 3. 결과 비교
    print("--- 최종 비교 결과 ---")
    print(f"캐시 미적용 시 총 소요 시간: {no_cache_duration:.2f}초")
    print(f"캐시 적용 시 총 소요 시간:   {cache_duration:.2f}초")
    print("="*50 + "\n")


# --- 2. 배치 처리 성능 비교 (Batching Performance Comparison) ---

# 개별 처리 함수
def process_item_individually(item: str):
    """아이템을 하나씩 개별적으로 처리 (0.2초 소요)"""
    print(f"[개별 처리] '{item}' 처리 중...")
    time.sleep(0.2)

# 배치 처리 함수
def process_items_in_batch(items: List[str]):
    """아이템 목록(배치)을 한 번에 처리 (0.5초 소요)"""
    print(f"[배치 처리] {len(items)}개 아이템 일괄 처리 중: {items}")
    time.sleep(0.5)

class BatchProcessor:
    """아이템을 모아 배치로 처리하는 클래스"""
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.batch: List[str] = []

    def add(self, item: str):
        self.batch.append(item)
        if len(self.batch) >= self.batch_size:
            process_items_in_batch(self.batch)
            self.batch.clear()

    def flush(self):
        if self.batch:
            process_items_in_batch(self.batch)
            self.batch.clear()

def run_batching_comparison():
    """배치 처리 적용 전/후의 성능을 비교하는 예제"""
    print("--- 2. 배치(Batching) 성능 비교 시작 ---")
    items_to_process = [f"항목_{i+1}" for i in range(12)]
    print(f"처리할 아이템 총 {len(items_to_process)}개\n")

    # 1. 개별 처리 테스트
    print("--- 개별 처리 테스트 시작 ---")
    start_time = time.time()
    for item in items_to_process:
        process_item_individually(item)
    individual_duration = time.time() - start_time
    print(f"--- 개별 처리 테스트 종료 ---\n")

    # 2. 배치 처리 테스트
    print("--- 배치 처리 테스트 시작 ---")
    processor = BatchProcessor(batch_size=5)
    start_time = time.time()
    for item in items_to_process:
        processor.add(item)
    processor.flush()
    batch_duration = time.time() - start_time
    print(f"--- 배치 처리 테스트 종료 ---\n")

    # 3. 결과 비교
    print("--- 최종 비교 결과 ---")
    print(f"개별 처리 시 총 소요 시간: {individual_duration:.2f}초")
    print(f"배치 처리 시 총 소요 시간: {batch_duration:.2f}초")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_caching_comparison()
    run_batching_comparison()