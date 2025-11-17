# create_store.py
import os
from dotenv import load_dotenv
from google import genai

# .env 로드
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY 환경변수가 없습니다!")

client = genai.Client(api_key=api_key)

store = client.file_search_stores.create(
    config={"display_name": "my-file_search-store-7235"}
)

print("=== File Search Store 생성 완료 ===")
print("store.name =", repr(store.name))
