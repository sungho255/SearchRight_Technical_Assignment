import random
import logging
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass

import io
from PIL import Image as PILImage

# 로깅 설정
logger = logging.getLogger(__name__)

@dataclass
class NodeStyles:
    # 기본 노드 스타일
    default: str = (
        "fill:#45C4B0, fill-opacity:0.3, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:bold, line-height:1.2, font_family: 'Arial'"  # 기본 색상
    )
    # 첫 번째 노드 스타일
    first: str = (
        "fill:#45C4B0, fill-opacity:0.1, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2, font_family: 'Arial'"  # 점선 테두리
    )
    # 마지막 노드 스타일
    last: str = (
        "fill:#45C4B0, fill-opacity:1, color:#000000, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2, font_family: 'Arial'"  # 점선 테두리
    )


def visualize_graph(graph, file_name, xray=False):
    """
    CompiledStateGraph 객체를 시각화하여 표시합니다.

    이 함수는 주어진 그래프 객체가 CompiledStateGraph 인스턴스인 경우
    해당 그래프를 Mermaid 형식의 PNG 이미지로 변환하여 표시합니다.

    Args:
        graph: 시각화할 그래프 객체. CompiledStateGraph 인스턴스여야 합니다.
        file_name (str): 저장될 이미지 파일의 이름 (확장자 제외).
        xray (bool, optional): 그래프의 내부 구조를 표시할지 여부. 기본값은 False.

    Returns:
        None

    Raises:
        Exception: 그래프 시각화 과정에서 오류가 발생한 경우 예외를 출력합니다.
    """
    try:
        file_path = f'./searchright_technical_assignment/image/{file_name}.png'
        logger.info(f"그래프를 {file_path}로 시각화하는 중입니다.")
        # 그래프 시각화
        if isinstance(graph, CompiledStateGraph):
            png_data = graph.get_graph(xray=xray).draw_mermaid_png(
                background_color="white",
                node_colors=NodeStyles(),
                padding=10,
            )
        
            image = PILImage.open(io.BytesIO(png_data))
            # 이미지 파일로 저장
            image.save(file_path)
            logger.info(f"이미지가 '{file_path}'로 저장되었습니다.")
    except Exception as e:
        logger.error(f"[오류] 그래프 시각화 오류: {e}")


def generate_random_hash():
    """
    6자리 16진수 형태의 무작위 해시 문자열을 생성합니다.

    Returns:
        str: 6자리 16진수 해시 문자열.
    """
    return f"{random.randint(0, 0xffffff):06x}"