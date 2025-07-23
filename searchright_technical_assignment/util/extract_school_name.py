import os
import json

def get_final_school_name(educations):
    if not educations:
        return "최종 학력 정보 없음"
    
    latest_end_year = -1
    final_education = None

    for edu in educations:
        # 'originStartEndDate' 필드 확인
        if 'originStartEndDate' in edu and 'endDateOn' in edu['originStartEndDate']:
            end_year = edu['originStartEndDate']['endDateOn'].get('year')
            if end_year and end_year > latest_end_year:
                latest_end_year = end_year
                final_education = edu
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
            except ValueError:
                # 연도 파싱 실패 시 무시
                pass

    if final_education:
        return final_education.get('schoolName', '최종 학력 정보 없음')
    else:
        return "최종 학력 정보 없음"

if __name__ == "__main__":
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
    print(f"최종 학력 학교 이름: {school_name}")
