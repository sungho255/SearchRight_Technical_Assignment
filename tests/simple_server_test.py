import requests

def test_server_connection():
    """
    서버 연결을 시도하고 성공 여부를 출력하는 간단한 테스트 함수입니다.
    """
    server_url = "http://localhost:8000/"
    print(f"서버 연결 테스트 시작: {server_url}...")
    try:
        response = requests.get(server_url, timeout=5)
        if response.status_code == 200:
            print(f"서버 연결 성공! 응답: {response.json()}")
            return True
        else:
            print(f"서버 연결 실패: 상태 코드 {response.status_code}, 응답: {response.text}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"서버 연결 실패: 서버가 실행 중이 아니거나 접근할 수 없습니다. 오류: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"서버 연결 실패: 요청 시간 초과. 오류: {e}")
        return False
    except Exception as e:
        print(f"서버 연결 중 예상치 못한 오류 발생: {e}")
        return False

if __name__ == "__main__":
    test_server_connection()