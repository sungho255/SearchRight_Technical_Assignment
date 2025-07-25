import unittest
from unittest.mock import MagicMock, patch

from searchright_technical_assignment.node.profiling_node import college_level, leadership, company_size, experience, combine
from searchright_technical_assignment.state.profiling_state import ProfilingState
from searchright_technical_assignment.schema.response_dto import LeadershipResponse, CompanySizeResponse, ExperienceResponse, CompanySizeItem, ExperienceItem
from langchain.schema import Document

class TestProfilingNode(unittest.TestCase):

    def test_college_level(self):
        # Mock ChatOpenAI and PromptTemplate
        mock_chat_openai = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        mock_chat_openai.return_value.invoke.return_value = "상위권 대학"

        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value = MagicMock()
        mock_prompt_template.__or__.return_value.__or__.return_value = mock_chat_openai.return_value

        # Create a sample state
        state = ProfilingState(
            talent_id="test_id",
            college="서울대학교",
            skills=[],
            titles=[],
            companynames_and_dates=[],
            descriptions=[]
        )

        # Call the function with mocks
        with patch('searchright_technical_assignment.node.profiling_node.ChatOpenAI', return_value=mock_chat_openai), \
             patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', return_value=mock_prompt_template), \
             patch('searchright_technical_assignment.node.profiling_node.StrOutputParser', return_value=MagicMock()):
            
            result = college_level(state, mock_prompt_template)

            # Assert the result
            self.assertEqual(result, {'college_level': '상위권 대학'})
            mock_chat_openai.return_value.invoke.assert_called_once_with({'college': '서울대학교'})

    def test_leadership(self):
        # Mock ChatOpenAI and PromptTemplate
        mock_leadership_response = LeadershipResponse(leadership="리더십 경험 있음", reason=["팀 프로젝트 리더 경험"])
        
        # Mock the llm_with_tool part
        mock_llm_with_tool = MagicMock()
        mock_llm_with_tool.invoke.return_value = mock_leadership_response

        # Mock ChatOpenAI to return an instance whose with_structured_output returns mock_llm_with_tool
        mock_chat_openai_instance = MagicMock()
        mock_chat_openai_instance.with_structured_output.return_value = mock_llm_with_tool
        mock_chat_openai_class = MagicMock(return_value=mock_chat_openai_instance) # Mock the class itself

        # Mock the prompt template and its __or__ method
        mock_prompt_template_instance = MagicMock()
        # When prompt | llm_with_tool is called, it's prompt_instance.__or__(llm_with_tool)
        # We want this to return something that has an .invoke() method.
        # The chain is `prompt | llm_with_tool`. So, `mock_prompt_template_instance.__or__` should return the chain mock.
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_leadership_response # The chain's invoke returns the final answer

        mock_prompt_template_instance.__or__.return_value = mock_chain
        mock_prompt_template_class = MagicMock(return_value=mock_prompt_template_instance)

        # Create a sample state
        state = ProfilingState(
            talent_id="test_id",
            college="",
            skills=["팀 리더", "프로젝트 관리"],
            titles=["팀장"],
            companynames_and_dates=[],
            descriptions=[]
        )

        # Call the function with mocks
        with patch('searchright_technical_assignment.node.profiling_node.ChatOpenAI', new=mock_chat_openai_class), \
             patch('searchright_technical_assignment.node.profiling_node.PromptTemplate', new=mock_prompt_template_class):
            
            result = leadership(state, mock_prompt_template_instance)

            # Assert the result
            self.assertEqual(result, {
                'leadership': '리더십 경험 있음',
                'leadership_reason': ['팀 프로젝트 리더 경험']
            })
            mock_chain.invoke.assert_called_once_with(
                {'skills': ['팀 리더', '프로젝트 관리'], 'titles': ['팀장']}
            )
            # Also check that with_structured_output was called correctly
            mock_chat_openai_instance.with_structured_output.assert_called_once_with(LeadershipResponse)

    @patch('searchright_technical_assignment.node.profiling_node.get_db')
    @patch('searchright_technical_assignment.node.profiling_node.CompanyDAO')
    @patch('searchright_technical_assignment.node.profiling_node.search_by_keyword')
    @patch('searchright_technical_assignment.node.profiling_node.ChatOpenAI')
    def test_company_size(self, MockChatOpenAI, MockSearchByKeyword, MockCompanyDAO, MockGetDb):
        # Mock dependencies
        mock_db_session = MagicMock()
        MockGetDb.return_value.__enter__.return_value = mock_db_session

        mock_company_dao_instance = MockCompanyDAO.return_value
        mock_company_dao_instance.get_data_by_names.return_value = [
            ("네이버", {"mae": "대기업", "investment": "대규모", "organization": "대규모"}),
            ("스타트업A", None) # DB에 없는 회사
        ]

        MockSearchByKeyword.return_value = [
            Document(page_content="스타트업A는 2020년 50억 투자 유치.")
        ]

        # The actual Pydantic response object that the LLM chain should return
        expected_llm_response_company_size = CompanySizeResponse(
            company_size_and_reason=[
                CompanySizeItem(company_size="대기업 경험", reasons=["네이버"]),
                CompanySizeItem(company_size="스타트업 경험", reasons=["스타트업A"])
            ]
        )

        mock_llm_with_tool_company_size = MagicMock()
        mock_llm_with_tool_company_size.invoke.return_value = expected_llm_response_company_size

        mock_chat_openai_instance = MagicMock()
        mock_chat_openai_instance.with_structured_output.return_value = mock_llm_with_tool_company_size
        MockChatOpenAI.return_value = mock_chat_openai_instance

        # Mock prompt template
        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value = mock_llm_with_tool_company_size

        # Create a sample state
        state = ProfilingState(
            talent_id="test_id",
            college="",
            skills=[],
            titles=[],
            companynames_and_dates=[
                {"companyName": "네이버", "startEndDates": []},
                {"companyName": "스타트업A", "startEndDates": [{"start": "2020-01-01", "end": "2021-12-31"}]}
            ],
            descriptions=[]
        )

        # Call the function
        result = company_size(state, mock_prompt_template)

        # Assertions
        self.assertEqual(result, {
            'company_size_and_reason': [
                CompanySizeItem(company_size="대기업 경험", reasons=["네이버"]),
                CompanySizeItem(company_size="스타트업 경험", reasons=["스타트업A"])
            ]
        })
        MockCompanyDAO.assert_called_once_with(mock_db_session)
        mock_company_dao_instance.get_data_by_names.assert_called_once_with(state['companynames_and_dates'])
        mock_llm_with_tool_company_size.invoke.assert_called_once()

    @patch('searchright_technical_assignment.node.profiling_node.get_db')
    @patch('searchright_technical_assignment.node.profiling_node.CompanyDAO')
    @patch('searchright_technical_assignment.node.profiling_node.ChatOpenAI')
    def test_experience(self, MockChatOpenAI, MockCompanyDAO, MockGetDb):
        # Mock dependencies
        mock_db_session = MagicMock()
        MockGetDb.return_value.__enter__.return_value = mock_db_session

        mock_company_dao_instance = MockCompanyDAO.return_value
        mock_company_dao_instance.get_data_by_names.return_value = [
            ("네이버", {"products": ["네이버 검색", "네이버 쇼핑"]}),
            ("카카오", {"products": ["카카오톡"]})
        ]

        # The actual Pydantic response object that the LLM chain should return
        expected_llm_response_experience = ExperienceResponse(
            experience_and_reason=[
                ExperienceItem(experience="검색 서비스 개발", reasons="네이버 검색"),
                ExperienceItem(experience="메신저 서비스 개발", reasons="카카오톡")
            ]
        )

        mock_llm_with_tool_experience = MagicMock()
        mock_llm_with_tool_experience.invoke.return_value = expected_llm_response_experience

        mock_chat_openai_instance = MagicMock()
        mock_chat_openai_instance.with_structured_output.return_value = mock_llm_with_tool_experience
        MockChatOpenAI.return_value = mock_chat_openai_instance

        # Mock prompt template
        mock_prompt_template = MagicMock()
        mock_prompt_template.__or__.return_value = mock_llm_with_tool_experience

        # Create a sample state
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

        # Call the function
        result = experience(state, mock_prompt_template)

        # Assertions
        self.assertEqual(result, {
            'experience_and_reason': [
                ExperienceItem(experience="검색 서비스 개발", reasons="네이버 검색"),
                ExperienceItem(experience="메신저 서비스 개발", reasons="카카오톡")
            ]
        })
        MockCompanyDAO.assert_called_once_with(mock_db_session)
        mock_company_dao_instance.get_data_by_names.assert_called_once_with(state['companynames_and_dates'])
        mock_llm_with_tool_experience.invoke.assert_called_once()

    def test_combine(self):
        # Create a sample state with various profiling results
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

        # Call the combine function
        result = combine(state)

        # Assert the combined profile
        expected_profile = {
            "상위권 대학": "고려대학교",
            "리더십 경험 있음": ["프로젝트 리더 경험"],
            "스타트업 경험": ["A 스타트업", "B 스타트업"],
            "대기업 경험": ["C 대기업"],
            "백엔드 개발 경험": "Python, Django 사용",
            "클라우드 경험": "AWS, Docker 사용"
        }
        self.assertEqual(result, {'profile': expected_profile})

        # Test case for "최종학력없음" and "리더쉽경험없음"
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