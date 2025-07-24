import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def get_descriptions(positions):
    """
    주어진 직책(positions) 리스트에서 설명을 추출합니다.

    Args:
        positions (list): 직책 정보를 포함하는 딕셔너리 리스트.

    Returns:
        list: 추출된 설명 문자열 리스트.
    """
    logger.info("직책에서 설명을 추출하는 중입니다.")
    # 설명 추출
    descriptions = [position.get('description') for position in positions if position.get('description')]
    logger.info(f"총 {len(descriptions)}개의 설명을 추출했습니다.")
    return descriptions

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # 예시 실행 시 INFO 레벨 로깅 활성화
    positions = [
        {
            "title": "Tech Lead - Clova X",
            "companyLogo": "",
            "companyName": "네이버",
            "description": "네이버 AI 팀에서 클로바X 개발 리드\n대규모 한국어 LLM 모델 개발 및 서비스 아키텍처 설계\n네이버 클로바 솔루션 개발 총괄\n대용량 데이터 처리 파이프라인 구축 및 모델 서빙 아키텍처 설계",
            "startEndDate": {
                "start": {
                    "year": 2021,
                    "month": 4
                }
            },
            "companyLocation": "대한민국 경기도 성남시"
        },
        {
            "title": "Tech Lead",
            "companyLogo": "",
            "companyName": "네이버",
            "description": "네이버 검색 서비스 백엔드 아키텍처 설계 및 개발\n대용량 트래픽 처리를 위한 MSA 기반 시스템 설계\n백엔드 개발팀 리드 - 팀원 15명\n글로벌 서비스 확장을 위한 인프라 설계 및 구축",
            "startEndDate": {
                "end": {
                    "year": 2021,
                    "month": 4
                },
                "start": {
                    "year": 2019,
                    "month": 2
                }
            },
            "companyLocation": "대한민국 경기도 성남시"
        },
        {
            "title": "Backend Chapter Lead",
            "companyLogo": "",
            "companyName": "토스",
            "description": "백엔드 개발팀 리딩 - 팀원 12명\n결제 및 송금 시스템 설계 및 개발\n대규모 트랜잭션 처리를 위한 시스템 아키텍처 설계\nMSA 기반 서비스 구조 설계 및 구현\n쿠버네티스 기반 인프라 구축",
            "startEndDate": {
                "end": {
                    "year": 2019,
                    "month": 1
                },
                "start": {
                    "year": 2017,
                    "month": 6
                }
            },
            "companyLocation": "대한민국 서울 강남구"
        },
        {
            "title": "Backend Engineer",
            "companyLogo": "",
            "companyName": "토스",
            "description": "금융 API 서비스 개발\n송금 및 결제 시스템 백엔드 개발\n실시간 트랜잭션 처리 시스템 구현\n보안 인증 시스템 개발",
            "startEndDate": {
                "end": {
                    "year": 2017,
                    "month": 6
                },
                "start": {
                    "year": 2016,
                    "month": 1
                }
            },
            "companyLocation": "대한민국 서울 강남구"
        }
    ]
    extracted_data = get_descriptions(positions)
    logger.info(f"설명: {extracted_data}")