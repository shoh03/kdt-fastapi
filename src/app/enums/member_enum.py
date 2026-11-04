from enum import Enum

class MemberProvider(str, Enum):  # enum으로 각 provider에 해당하는 타입을 새로 만듦
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"
    NAVER = "NAVER"