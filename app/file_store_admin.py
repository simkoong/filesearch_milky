# app/file_store_admin.py

import json
import os
import time
import uuid
from datetime import datetime
from typing import List, Dict

from fastapi import UploadFile

from google import genai
from .config import GOOGLE_API_KEY, FILE_SEARCH_STORE_NAME

# 로컬 저장 경로 & 인덱스 파일 경로
UPLOAD_DIR = "uploaded_docs"
INDEX_FILE = "data/file_index.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)

_client = genai.Client(api_key=GOOGLE_API_KEY)


def _load_index() -> List[Dict]:
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_index(records: List[Dict]) -> None:
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def list_files() -> List[Dict]:
    """
    업로드된 파일 목록을 반환 (최신 업로드가 위로 오도록 정렬)
    """
    records = _load_index()
    # uploaded_at 역순 정렬
    records.sort(key=lambda r: r.get("uploaded_at", ""), reverse=True)
    return records

def upload_file_and_index(file: UploadFile, display_name: str | None = None) -> Dict:
    """
    1) 업로드된 파일을 로컬 디스크에 저장 (ASCII-only 파일명 사용)
    2) File Search Store에 업로드 & 인덱싱
    3) file_index.json에 기록 추가
    """
    # 원본 파일명 (한글 등 그대로 유지)
    original_name = file.filename or "uploaded_file"

    # 확장자만 추출 (예: ".pdf", ".docx")
    _, ext = os.path.splitext(original_name)

    # 파일명은 ASCII-safe 로 생성 (UUID 사용)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = uuid.uuid4().hex  # ASCII 32자
    stored_filename = f"{timestamp}_{random_part}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)

    # 1) 로컬에 저장
    with open(stored_path, "wb") as out:
        # 업로드 파일 포인터를 처음으로 돌려두는 것이 안전
        file.file.seek(0)
        out.write(file.file.read())

    # 2) File Search Store에 업로드
    if not display_name:
        # 표시 이름에는 한글 그대로 써도 괜찮음 (JSON/UTF-8)
        display_name = original_name

    op = _client.file_search_stores.upload_to_file_search_store(
        file=stored_path,
        file_search_store_name=FILE_SEARCH_STORE_NAME,
        config={"display_name": display_name},
    )

    # 인덱싱 완료까지 대기 (간단 폴링)
    while not op.done:
        time.sleep(3)
        op = _client.operations.get(op)

    # 3) 인덱스 기록 저장
    records = _load_index()
    now = datetime.utcnow().isoformat()
    record = {
        "id": now,
        "filename": original_name,      # 원본 파일명(한글 그대로)
        "stored_filename": stored_filename,  # 실제 디스크에 저장된 ASCII-only 파일명
        "stored_path": stored_path,
        "display_name": display_name,
        "uploaded_at": now,
    }
    _save_index(records + [record])

    return record
