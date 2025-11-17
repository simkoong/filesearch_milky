from google import genai
from google.genai import types

from .config import GOOGLE_API_KEY, FILE_SEARCH_STORE_NAME, GEMINI_MODEL

# Milky 시스템 프롬프트 (필요하면 계속 다듬어도 됨)
MILKY_SYSTEM_PROMPT = """
너의 이름은 밀키(Milky)이고, 소모임 아이온(AION)에서 Gemini File search 시현을 위한 AI 어시스턴트야. 

역할:
1. 사용자의 문서(파일 검색 결과)를 기반으로 최대한 정확하게 설명한다.
2. 반드시 사용자의 문서를 최우선 근거로 삼고, 문서 내용과 추론을 명확히 구분한다.
3. 모르면 아는 척하지 말고, "문서 범위 내에서는 확인되지 않는다"라고 솔직히 말한다.
4. 표현은 친절하고, 가끔 고양이 말투(예: ~해요, ~좋겠어요, 살짝 귀엽게)를 섞되
   전문성은 절대 떨어뜨리지 않는다.

주의:
- 실제 법률·규정 해석은 참고용일 뿐, 최종 의사결정은 항상 관련 부서/전문가 확인이 필요함을
  부드럽게 한 줄 정도 덧붙인다.
"""

# Google GenAI 클라이언트 (프로세스 단위 1개만)
_client = genai.Client(api_key=GOOGLE_API_KEY)


def ask_milky_rag(question: str) -> str:
    """
    File Search Store를 도구로 사용하는 Milky RAG 호출 함수.
    """
    file_search_tool = types.Tool(
        file_search=types.FileSearch(
            file_search_store_names=[FILE_SEARCH_STORE_NAME]
        )
    )

    resp = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[file_search_tool],
            system_instruction=MILKY_SYSTEM_PROMPT,
        ),
    )

    # 기본 텍스트만 추출
    answer = resp.text or ""
    return answer.strip()

