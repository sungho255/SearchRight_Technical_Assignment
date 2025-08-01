import sys
import os
import asyncio
import json
from line_profiler import LineProfiler
from unittest.mock import patch, AsyncMock # patch와 AsyncMock 임포트

# 프로젝트 루트를 sys.path에 추가하여 절대 임포트가 가능하도록 합니다.
# 이 파일의 위치: C:\SearchRight_Technical_Assignment\tests
# 프로젝트 루트: C:\SearchRight_Technical_Assignment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 프로파일링할 모듈과 필요한 DTO, PromptTemplate 임포트
from searchright_technical_assignment.node import profiling_node
from searchright_technical_assignment.state.profiling_state import ProfilingState
from langchain_core.prompts import PromptTemplate # Mock prompt에 필요

# --- PGVector 및 관련 함수들을 모의(Mock)하는 더미 클래스/함수 ---
class MockRetriever:
    def get_relevant_documents(self, keyword):
        return []

class MockPGVector:
    def __init__(self, *args, **kwargs):
        pass

    def as_retriever(self, *args, **kwargs):
        return MockRetriever()

async def mock_search_by_keyword(*args, **kwargs):
    return []
# --- 모의 끝 ---

# --- DB 및 CompanyDAO를 모의(Mock)하는 더미 클래스/함수 ---
class MockDBSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def close(self):
        pass

class MockCompanyDAO:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_data_by_names(self, company_names_and_dates):
        # 더미 데이터 반환 (실제 DB 호출 없음)
        return [
            ('쿠팡', {'products': [{'name': '로켓배송'}]}),
            ('우아한형제들', {'products': [{'name': '배달의민족'}]})
        ]

async def mock_get_db():
    yield MockDBSession()
# --- 모의 끝 ---

async def run_profiling_test():
    # kernprof 출력 헤더 모방
    print("Wrote profile results to 'profiling_node.py.lprof' (This is a mock output, no file is actually written)")
    print("Timer unit: 1e-06 s")
    print()

    # talent_ex4.json 파일 로드
    talent_data_path = os.path.join(project_root, 'example_datas', 'talent_ex4.json')
    with open(talent_data_path, 'r', encoding='utf-8') as f:
        talent_data = json.load(f)

    # talent_ex4.json 데이터에서 ProfilingState에 필요한 정보 추출
    extracted_college = talent_data['educations'][0]['schoolName'] if talent_data['educations'] else ''
    extracted_skills = talent_data['skills']
    extracted_titles = [pos['title'] for pos in talent_data['positions']]
    
    extracted_companynames_and_dates = []
    extracted_descriptions = []
    for pos in talent_data['positions']:
        company_name = pos.get('companyName')
        description = pos.get('description')
        start_end_date = pos.get('startEndDate')

        if company_name:
            # startEndDates 형식 변환
            formatted_start_end_dates = []
            if start_end_date:
                start_date_obj = start_end_date.get('start')
                end_date_obj = start_end_date.get('end')
                
                start_str = f"{start_date_obj['year']}-{start_date_obj['month']}-01" if start_date_obj and 'year' in start_date_obj else None
                end_str = f"{end_date_obj['year']}-{end_date_obj['month']}-01" if end_date_obj and 'year' in end_date_obj else None
                
                formatted_start_end_dates.append({
                    'start': start_str,
                    'end': end_str
                })
            
            extracted_companynames_and_dates.append({
                'companyName': company_name,
                'startEndDates': formatted_start_end_dates
            })
        
        if description:
            extracted_descriptions.append(description)

    # 테스트용 ProfilingState 객체 생성
    test_state = ProfilingState(
        college=extracted_college,
        skills=extracted_skills,
        titles=extracted_titles,
        companynames_and_dates=extracted_companynames_and_dates,
        descriptions=extracted_descriptions,
        # 나머지 필드는 기본값 또는 빈 값으로 초기화
        college_level='',
        leadership='',
        leadership_reason=[],
        investment={},
        organiztion={},
        company_size_and_reason=[],
        products={},
        experience_and_reason=[],
        profile={}
    )

    # Mock 프롬프트 템플릿 (실제 프롬프트는 외부에서 주입되어야 함)
    mock_prompt = PromptTemplate.from_template("This is a mock prompt for {college}")
    mock_leadership_prompt = PromptTemplate.from_template("Analyze leadership for {skills} and {titles}")
    mock_company_size_prompt = PromptTemplate.from_template("Analyze company size for {companynames_and_dates} with db: {grouped_company_data} and news: {company_news_contents}")
    mock_experience_prompt = PromptTemplate.from_template("Analyze experience for {descriptions} with products: {grouped_company_data}")

    # LineProfiler 인스턴스 생성
    lp = LineProfiler()

    # 프로파일링할 함수들을 명시적으로 추가
    lp.add_function(profiling_node.college_level)
    lp.add_function(profiling_node.leadership)
    lp.add_function(profiling_node.company_size)
    lp.add_function(profiling_node.experience)
    lp.add_function(profiling_node.combine)

    # PGVector, DB, CompanyDAO 관련 객체들을 모의(Mock)하여 외부 의존성 제거
    with patch('searchright_technical_assignment.retriever.pgvector.PGVector', new=MockPGVector):
        with patch('searchright_technical_assignment.retriever.pgvector.search_by_keyword', new=mock_search_by_keyword):
            with patch('searchright_technical_assignment.db.conn.get_db', new=mock_get_db):
                with patch('searchright_technical_assignment.crud.company_dao.CompanyDAO', new=MockCompanyDAO):

                    # 프로파일링 시작
                    lp.enable_by_count()

                    # 각 노드 함수 호출
                    college_result = await profiling_node.college_level(test_state, mock_prompt)
                    test_state.update(college_result)

                    leadership_result = await profiling_node.leadership(test_state, mock_leadership_prompt)
                    test_state.update(leadership_result)

                    company_size_result = await profiling_node.company_size(test_state, mock_company_size_prompt)
                    test_state.update(company_size_result)

                    experience_result = await profiling_node.experience(test_state, mock_experience_prompt)
                    test_state.update(experience_result)

                    combine_result = profiling_node.combine(test_state)
                    test_state.update(combine_result)

                    print("--- 최종 프로파일링 결과 (test_line_profile.py) ---")
                    print(test_state['profile'])

                    # 프로파일링 종료
                    lp.disable_by_count()

    # 프로파일링 통계 출력
    lp.print_stats()

if __name__ == "__main__":
    asyncio.run(run_profiling_test())