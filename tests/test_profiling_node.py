import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from searchright_technical_assignment.node.profiling_node import college_level, leadership, company_size, experience, combine
from searchright_technical_assignment.state.profiling_state import ProfilingState
from searchright_technical_assignment.schema.response_dto import LeadershipResponse, CompanySizeResponse, ExperienceResponse, CompanySizeItem, ExperienceItem
from langchain.schema import Document

class TestProfilingNode(unittest.IsolatedAsyncioTestCase):

    async def test_college_level(self):
        # Mock chain
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = "상위권 대학"

        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value.__or__.return_value = mock_chain

        state = ProfilingState(
            talent_id="test_id",
            college="서울대학교",
            skills=[],
            titles=[],
            companynames_and_dates=[],
            descriptions=[]
        )

        with patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', return_value=mock_prompt_template):
            result = await college_level(state, mock_prompt_template)

            self.assertEqual(result, {'college_level': '상위권 대학'})
            mock_chain.ainvoke.assert_called_once_with({'college': '서울대학교'})

    async def test_leadership(self):
        mock_leadership_response = LeadershipResponse(leadership="리더십 경험 있음", reason=["팀 프로젝트 리더 경험"])
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = mock_leadership_response

        mock_prompt_template_instance = MagicMock()
        mock_prompt_template_instance.__or__.return_value = mock_chain

        state = ProfilingState(
            talent_id="test_id",
            college="",
            skills=["팀 리더", "프로젝트 관리"],
            titles=["팀장"],
            companynames_and_dates=[],
            descriptions=[]
        )

        with patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', return_value=mock_prompt_template_instance):
            result = await leadership(state, mock_prompt_template_instance)

            self.assertEqual(result, {
                'leadership': '리더십 경험 있음',
                'leadership_reason': ['팀 프로젝트 리더 경험']
            })
            mock_chain.ainvoke.assert_called_once_with(
                {'skills': ['팀 리더', '프로젝트 관리'], 'titles': ['팀장']}
            )

    @patch('searchright_technical_assignment.node.profiling_node.get_db')
    @patch('searchright_technical_assignment.node.profiling_node.CompanyDAO')
    @patch('searchright_technical_assignment.node.profiling_node.search_by_keyword', new_callable=AsyncMock)
    async def test_company_size(self, MockSearchByKeyword, MockCompanyDAO, MockGetDb):
        mock_db_session = AsyncMock()
        MockGetDb.return_value.__aenter__.return_value = mock_db_session
        
        mock_company_dao_instance = MockCompanyDAO.return_value
        mock_company_dao_instance.get_data_by_names = AsyncMock(return_value=[
            ("네이버", {"mae": "대기업", "investment": {"data": []}, "organization": {"data": []}}),
            ("스타트업A", None)
        ])

        MockSearchByKeyword.return_value = [
            Document(page_content="스타트업A는 2020년 50억 투자 유치.")
        ]

        expected_llm_response = CompanySizeResponse(
            company_size_and_reason=[
                CompanySizeItem(company_size="대기업 경험", reasons=["네이버"]),
                CompanySizeItem(company_size="스타트업 경험", reasons=["스타트업A"])
            ]
        )

        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = expected_llm_response

        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value = mock_chain

        state = ProfilingState(
            talent_id="test_id",
            college="",
            skills=[],
            titles=[],
            companynames_and_dates=[
                {"companyName": "네이버", "startEndDates": []},
                {"companyName": "스타트업A", "startEndDates": [{"start": {"year": 2020, "month": 1, "day": 1}, "end": {"year": 2021, "month": 12, "day": 31}}]}
            ],
            descriptions=[]
        )

        with patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', return_value=mock_prompt_template):
            result = await company_size(state, mock_prompt_template)

        self.assertEqual(result, {
            'company_size_and_reason': [
                CompanySizeItem(company_size="대기업 경험", reasons=["네이버"]),
                CompanySizeItem(company_size="스타트업 경험", reasons=["스타트업A"])
            ]
        })
        mock_chain.ainvoke.assert_called_once()

    @patch('searchright_technical_assignment.node.profiling_node.get_db')
    @patch('searchright_technical_assignment.node.profiling_node.CompanyDAO')
    async def test_experience(self, MockCompanyDAO, MockGetDb):
        mock_db_session = AsyncMock()
        MockGetDb.return_value.__aenter__.return_value = mock_db_session

        mock_company_dao_instance = MockCompanyDAO.return_value
        mock_company_dao_instance.get_data_by_names = AsyncMock(return_value=[
            ("네이버", {"products": [{"name": "네이버 검색"}, {"name": "네이버 쇼핑"}]}),
            ("카카오", {"products": [{"name": "카카오톡"}]})
        ])

        expected_llm_response = ExperienceResponse(
            experience_and_reason=[
                ExperienceItem(experience="검색 서비스 개발", reasons="네이버 검색"),
                ExperienceItem(experience="메신저 서비스 개발", reasons="카카오톡")
            ]
        )

        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = expected_llm_response

        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value = mock_chain

        state = ProfilingState(
            talent_id="test_id",
            college="",
            skills=[],
            titles=[],
            companynames_and_dates=[
                {"companyName": "네이버", "startEndDates": []},
                {"companyName": "카카오", "startEndDates": []}
            ],
            descriptions=["네이버에서 검색 서비스 개발", "카카오에서 메신저 서비스 개발"]
        )

        with patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', return_value=mock_prompt_template):
            result = await experience(state, mock_prompt_template)

        self.assertEqual(result, {
            'experience_and_reason': [
                ExperienceItem(experience="검색 서비스 개발", reasons="네이버 검색"),
                ExperienceItem(experience="메신저 서비스 개발", reasons="카카오톡")
            ]
        })
        mock_chain.ainvoke.assert_called_once()

    def test_combine(self):
        state = ProfilingState(
            talent_id="test_id",
            college="고려대학교",
            skills=[],
            titles=[],
            companynames_and_dates=[],
            descriptions=[],
            college_level="상위권 대학",
            leadership="리더십 경험 있음",
            leadership_reason=["프로젝트 리더 경험"],
            company_size_and_reason=[
                CompanySizeItem(company_size="스타트업 경험", reasons=["A 스타트업", "B 스타트업"]),
                CompanySizeItem(company_size="대기업 경험", reasons=["C 대기업"])
            ],
            experience_and_reason=[
                ExperienceItem(experience="백엔드 개발 경험", reasons="Python, Django 사용"),
                ExperienceItem(experience="클라우드 경험", reasons="AWS, Docker 사용")
            ]
        )

        result = combine(state)

        expected_profile = {
            "상위권 대학": "고려대학교",
            "리더십 경험 있음": ["프로젝트 리더 경험"],
            "스타트업 경험": ["A 스타트업", "B 스타트업"],
            "대기업 경험": ["C 대기업"],
            "백엔드 개발 경험": "Python, Django 사용",
            "클라우드 경험": "AWS, Docker 사용"
        }
        self.assertEqual(result, {'profile': expected_profile})

        state_no_experience = ProfilingState(
            talent_id="test_id_no_exp",
            college="최종학력없음",
            skills=[],
            titles=[],
            companynames_and_dates=[],
            descriptions=[],
            college_level="최종학력없음",
            leadership="리더쉽경험없음",
            leadership_reason=[],
            company_size_and_reason=[],
            experience_and_reason=[]
        )
        result_no_experience = combine(state_no_experience)
        self.assertEqual(result_no_experience, {'profile': {}})

if __name__ == '__main__':
    unittest.main()
