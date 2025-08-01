import asyncio
import os
from dotenv import load_dotenv
from searchright_technical_assignment.util.embedding import generate_embedding
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

async def test_openai_embedding():
    """
    OpenAI 임베딩 생성을 테스트하는 비동기 함수입니다.
    테스트 텍스트에 대한 임베딩을 생성하고 성공 여부를 로깅합니다.
    """
    logger.info("OpenAI 임베딩 테스트를 시작합니다...")
    test_text = "이것은 OpenAI 임베딩 테스트를 위한 문장입니다."
    
    try:
        # generate_embedding 함수는 이제 텍스트 리스트를 받습니다.
        embeddings = await generate_embedding([test_text])
        
        if embeddings and embeddings[0]:
            logger.info(f"임베딩 생성 성공! 차원: {len(embeddings[0])}")
            logger.info(f"첫 5개 요소: {embeddings[0][:5]}...")
        else:
            logger.warning("임베딩 생성 실패: 빈 임베딩이 반환되었습니다.")
            logger.warning("API 키가 유효한지, 네트워크 연결이 원활한지 확인해주세요.")
            
    except Exception as e:
        logger.error(f"임베딩 테스트 중 예외 발생: {e}")
        logger.error("API 키 문제, 네트워크 문제 또는 기타 설정 오류일 수 있습니다.")

if __name__ == "__main__":
    # OPENAI_API_KEY 환경 변수가 설정되어 있는지 확인
    if os.getenv('OPENAI_API_KEY'):
        asyncio.run(test_openai_embedding())
    else:
        logger.error("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        logger.error(".env 파일에 OPENAI_API_KEY를 추가해주세요.")