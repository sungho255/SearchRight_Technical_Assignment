import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def get_final_school_name(educations):
    """
    주어진 학력(educations) 리스트에서 최종 학력 학교 이름을 추출합니다.
    가장 최근의 종료 연도를 기준으로 최종 학력을 판단합니다.

    Args:
        educations (list): 학력 정보를 포함하는 딕셔너리 리스트.

    Returns:
        str: 최종 학력 학교 이름 또는 학력 정보가 없는 경우 "최종 학력 정보 없음".
    """
    logger.info("학력 정보에서 최종 학교 이름을 추출하는 중입니다.")
    if not educations:
        logger.info("제공된 학력 데이터가 없습니다. '최종 학력 정보 없음'을 반환합니다.")
        return "최종 학력 정보 없음"
    
    latest_end_year = -1
    final_education = None

    for edu in educations:
        logger.debug(f"학력 항목 처리 중: {edu}")
        # 'originStartEndDate' 필드 확인
        if 'originStartEndDate' in edu and 'endDateOn' in edu['originStartEndDate']:
            end_year = edu['originStartEndDate']['endDateOn'].get('year')
            if end_year and end_year > latest_end_year:
                latest_end_year = end_year
                final_education = edu
                logger.debug(f"종료 연도 {end_year}를 가진 최신 학력 발견: {edu.get('schoolName')}")
        # 'startEndDate' 필드가 문자열인 경우 파싱 시도 (예: "2010 - 2015")
        elif 'startEndDate' in edu and isinstance(edu['startEndDate'], str):
            try:
                # ' - ' 기준으로 분리하여 마지막 연도 추출
                parts = edu['startEndDate'].split(' - ')
                if len(parts) > 1:
                    end_year = int(parts[1].strip())
                    if end_year > latest_end_year:
                        latest_end_year = end_year
                        final_education = edu
                        logger.debug(f"문자열 날짜에서 종료 연도 {end_year}를 가진 최신 학력 발견: {edu.get('schoolName')}")
            except ValueError:
                logger.warning(f"startEndDate 문자열에서 연도 파싱 실패: {edu['startEndDate']}")
                pass

    if final_education:
        school_name = final_education.get('schoolName', '최종 학력 정보 없음')
        logger.info(f"최종 학교 이름 결정됨: {school_name}")
        return school_name
    else:
        logger.info("최종 학력을 찾을 수 없습니다. '최종 학력 정보 없음'을 반환합니다.")
        return "최종 학력 정보 없음"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # 예시 실행 시 INFO 레벨 로깅 활성화
    educations = [
        {
            "grade": "",
            "degreeName": "학사",
            "schoolName": "연세대학교",
            "description": "",
            "fieldOfStudy": "컴퓨터 공학",
            "startEndDate": "2010 - 2015",
            "originStartEndDate": {
                "endDateOn": {
                    "year": 2015
                },
                "startDateOn": {
                    "year": 2010
                }
            }
        }
    ]
    school_name = get_final_school_name(educations)
    logger.info(f"최종 학력 학교 이름: {school_name}")