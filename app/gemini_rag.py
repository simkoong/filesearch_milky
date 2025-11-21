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
    
    # 실제 참고한 문서 추출 (grounding_metadata 사용)
    referenced_docs = set()  # 중복 제거를 위해 set 사용
    
    if hasattr(resp, "candidates") and resp.candidates:
        for cand in resp.candidates:
            # grounding_metadata에서 실제 참고 문서 추출
            if hasattr(cand, "grounding_metadata") and cand.grounding_metadata:
                gm = cand.grounding_metadata
                if hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                    for chunk in gm.grounding_chunks:
                        # retrieved_context에 document_name이 있으면 추출
                        if hasattr(chunk, "retrieved_context") and chunk.retrieved_context:
                            rc = chunk.retrieved_context
                            # document_name 또는 title 사용
                            doc_name = getattr(rc, "title", None) or getattr(rc, "document_name", None)
                            if doc_name:
                                referenced_docs.add(doc_name)
    
    # 참고 문서가 있으면 마크다운 블록 추가
    if referenced_docs:
        citation_md = "\n\n**📚 참고 문서**\n"
        for doc_name in sorted(referenced_docs):  # 정렬해서 표시
            citation_md += f"- {doc_name}\n"
        answer = answer.strip() + citation_md
    
    return answer.strip()

