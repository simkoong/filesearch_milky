from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .gemini_rag import ask_milky_rag
from .file_store_admin import list_files, upload_file_and_index

app = FastAPI(title="Milky - File Search with Gemini RAG")

# 정적 파일 / 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/admin", response_class=HTMLResponse)
async def get_admin(request: Request):
    """
    File Search Store용 파일 관리 웹 UI
    """
    return templates.TemplateResponse(
        "admin.html",
        {"request": request},
    )

@app.get("/api/admin/files")
async def api_admin_files():
    """
    업로드된 파일 목록 반환
    """
    files = list_files()
    return {"files": files}

@app.post("/api/admin/upload")
async def api_admin_upload(
    file: UploadFile = File(...),
    display_name: str = Form(None),
):
    """
    파일 업로드 + File Search Store 인덱싱
    """
    try:
        record = upload_file_and_index(file, display_name)
        return {"ok": True, "file": record}
    except Exception as e:
        # 실제 운영에서는 로깅 추천
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)},
        )


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    메인 페이지 (웹 UI)
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.post("/api/ask")
async def api_ask(payload: dict):
    """
    질문을 받아서 Milky RAG에 전달하고, 답변을 JSON으로 반환
    """
    question = (payload.get("question") or "").strip()
    if not question:
        return JSONResponse(
            status_code=400,
            content={"error": "question 필드는 비어 있을 수 없습니다."},
        )

    try:
        answer = ask_milky_rag(question)
        return {"answer": answer}
    except Exception as e:
        # 실제 운영에서는 로깅 추가
        return JSONResponse(
            status_code=500,
            content={"error": f"서버 오류: {e}"},
        )

