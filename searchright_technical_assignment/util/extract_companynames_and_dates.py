import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def _parse_date(date_obj, is_start=True):
    """
    날짜 객체를 (년, 월) 튜플로 파싱합니다.
    월이 없으면 시작일은 1월, 종료일은 12월로 간주합니다.

    Args:
        date_obj (dict): 년도와 월 정보를 포함하는 딕셔너리.
        is_start (bool, optional): 시작 날짜인지 여부. 기본값은 True.

    Returns:
        tuple: (년, 월) 튜플 또는 None.
    """
    if not date_obj:
        logger.debug("날짜 객체가 None입니다.")
        return None
    
    year = date_obj.get('year')
    month = date_obj.get('month')
    
    if year is None:
        logger.warning(f"날짜 객체에서 년도를 찾을 수 없습니다: {date_obj}")
        return None
    if month is None:
        month = 1 if is_start else 12 # 월이 없으면 시작일은 1월, 종료일은 12월로 간주
        logger.debug(f"월을 찾을 수 없어, 년도 {year}에 대해 {month}로 기본 설정합니다.")
        
    return (year, month)

def _merge_intervals(intervals):
    """
    겹치거나 연속된 기간들을 병합합니다.

    Args:
        intervals (list): (시작 날짜 튜플, 종료 날짜 튜플) 형태의 기간 튜플 리스트.

    Returns:
        list: 병합된 기간 튜플 리스트.
    """
    if not intervals:
        logger.debug("병합할 기간이 없습니다.")
        return []

    # 시작 날짜 기준으로 정렬
    intervals.sort(key=lambda x: x[0])
    logger.debug(f"정렬된 기간: {intervals}")

    merged = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            # 현재 기간이 병합된 마지막 기간과 겹치지 않으면 새 기간으로 추가
            merged.append([start, end])
            logger.debug(f"새 기간 추가: {start}-{end}")
        else:
            # 겹치거나 연속되면 병합
            merged[-1][1] = max(merged[-1][1], end)
            logger.debug(f"기간 병합, 새로운 종료: {merged[-1][1]}")
    return merged

def get_companynames_and_dates(positions):
    """
    주어진 직책(positions) 리스트에서 회사 이름과 해당 근무 기간을 추출하고 병합합니다.

    Args:
        positions (list): 직책 정보를 포함하는 딕셔너리 리스트.

    Returns:
        list: 각 회사별로 회사 이름과 병합된 근무 기간을 포함하는 딕셔너리 리스트.
    """
    logger.info("직책에서 회사 이름과 날짜 추출 시작.")
    # 회사 이름과 해당 근무 기간을 저장할 딕셔너리
    company_data = {}

    for position in positions:
        if isinstance(position, dict) and 'companyName' in position:
            company_name = position['companyName']
            start_end_date_raw = position.get('startEndDate')
            logger.debug(f"회사에 대한 직책 처리 중: {company_name}")

            if start_end_date_raw:
                start_date = _parse_date(start_end_date_raw.get('start'), is_start=True)
                end_date = _parse_date(start_end_date_raw.get('end'), is_start=False)
                
                # 시작일만 있고 종료일이 없는 경우 (현재 재직 중인 경우 등)
                if start_date and not end_date:
                    end_date = (9999, 12) # 임의의 미래 날짜로 설정하여 병합 가능하게 함
                    logger.debug(f"종료 날짜가 제공되지 않아 {company_name}에 대한 미래 종료 날짜 설정.")
                
                if start_date and end_date:
                    if company_name not in company_data:
                        company_data[company_name] = []
                    company_data[company_name].append((start_date, end_date))
                    logger.debug(f"{company_name}에 대한 날짜 범위 {start_date}-{end_date} 추가됨.")
    
    result = []
    for company_name, dates in company_data.items():
        merged_dates = _merge_intervals(dates)
        logger.debug(f"{company_name}에 대한 병합된 날짜: {merged_dates}")
        
        formatted_dates = []
        for start, end in merged_dates:
            # 임의의 미래 날짜를 다시 None으로 변환
            if end == (9999, 12):
                end_obj = None
            else:
                end_obj = {'year': end[0], 'month': end[1]}

            formatted_dates.append({
                'start': {'year': start[0], 'month': start[1]},
                'end': end_obj
            })

        result.append({
            'companyName': company_name,
            'startEndDates': formatted_dates
        })
    logger.info(f"회사 이름과 날짜 추출 완료. 결과 개수: {len(result)}")
    return result

# 이 스크립트가 직접 실행될 때 예시 코드를 실행합니다.
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG) # 예시 실행 시 DEBUG 레벨 로깅 활성화
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
    unique_names = get_companynames_and_dates(positions)
    
    logger.info(f"시작/종료 날짜가 있는 회사 데이터: {unique_names}")
