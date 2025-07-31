import logging

class ColoredFormatter(logging.Formatter):
    """
    로그 메시지에 색상을 추가하는 커스텀 포매터 클래스입니다.
    '완료'가 포함된 INFO 로그는 파란색으로, '닫혔습니다'가 포함된 INFO 로그는 노란색으로 변경합니다.
    """

    BLUE = '\x1b[34m'
    YELLOW = '\x1b[33m'
    RESET = '\x1b[0m'

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # 기본 포매팅을 먼저 수행합니다.
        log_message = super().format(record)

        # INFO 레벨에서만 특정 단어에 따라 색상을 변경합니다.
        if record.levelno == logging.INFO:
            if '완료' in record.getMessage() or '성공' in record.getMessage():
                return f"{self.BLUE}{log_message}{self.RESET}"
            elif '닫혔습니다' in record.getMessage():
                return f"{self.YELLOW}{log_message}{self.RESET}"
        
        return log_message
