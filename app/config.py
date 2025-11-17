import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FILE_SEARCH_STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GOOGLE_API_KEY:
    raise RuntimeError("환경변수 GOOGLE_API_KEY 가 설정되어 있지 않습니다.")

if not FILE_SEARCH_STORE_NAME:
    raise RuntimeError("환경변수 FILE_SEARCH_STORE_NAME 가 설정되어 있지 않습니다.")
