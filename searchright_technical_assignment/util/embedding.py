import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict


# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# .env 파일 로드
load_dotenv()

# 임베딩 캐시 (embedding cache)
embedding_cache: Dict[str, List[float]] = {}

# 배치 사이즈 설정 (조절 가능)
BATCH_SIZE = 32 # 예시 값, 실제 환경에서 최적화 필요

async def generate_embedding(texts: List[str]) -> List[List[float]]:
    """
    텍스트 리스트로부터 1536차원의 임베딩을 생성합니다.
    캐싱, 배치 처리, 비동기 처리를 적용하여 효율성을 높입니다.

    Args:
        texts (List[str]): 임베딩을 생성할 텍스트 문자열 리스트.

    Returns:
        List[List[float]]: 각 텍스트에 대한 1536차원 임베딩 리스트.
                           임베딩 생성에 실패한 경우 해당 위치에 None이 포함될 수 있습니다.
    """
    results: List[List[float]] = [[] for _ in range(len(texts))]
    texts_to_embed: List[str] = []
    indices_to_embed: List[int] = []

    # 캐시 확인 및 임베딩할 텍스트 분류
    for i, text in enumerate(texts):
        if text in embedding_cache:
            results[i] = embedding_cache[text]
        else:
            texts_to_embed.append(text)
            indices_to_embed.append(i)

    if not texts_to_embed:
        logger.info("모든 텍스트가 캐시에 있어 임베딩을 새로 생성하지 않습니다.")
        return results

    # 배치 처리
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    logger.info(f"총 {len(texts_to_embed)}개의 텍스트를 임베딩합니다. 배치 사이즈: {BATCH_SIZE}")

    # tqdm을 사용하여 배치 처리 루프에 진행률 표시줄을 추가합니다.
    for batch_num, i in enumerate(range(0, len(texts_to_embed), BATCH_SIZE)):
        batch_texts = texts_to_embed[i:i + BATCH_SIZE]
        batch_indices = indices_to_embed[i:i + BATCH_SIZE]
        
        try:
            response = await client.embeddings.create(
                input=batch_texts,
                model="text-embedding-ada-002"
            )
            for j, embedding in enumerate(response.data):
                original_index = batch_indices[j]
                results[original_index] = embedding.embedding
                embedding_cache[batch_texts[j]] = embedding.embedding # 캐시에 저장
        
        except Exception as e:
        # 오류 발생 시 해당 배치 내 모든 텍스트에 대해 None 할당
            for j in range(len(batch_texts)):
                original_index = batch_indices[j]
                results[original_index] = None

    return results