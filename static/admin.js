document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const uploadBtn = document.getElementById("uploadBtn");
  const uploadStatus = document.getElementById("uploadStatus");
  const fileTableBody = document.getElementById("fileTableBody");

  async function loadFiles() {
    fileTableBody.innerHTML = `
      <tr><td colspan="3" class="small">로딩 중...</td></tr>
    `;
    try {
      const res = await fetch("/api/admin/files");
      const data = await res.json();
      const files = data.files || [];

      if (!files.length) {
        fileTableBody.innerHTML = `
          <tr><td colspan="4" class="small">아직 업로드된 파일이 없습니다.</td></tr>
        `;
        return;
      }

      fileTableBody.innerHTML = "";
      files.forEach((f) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${f.display_name || ""}</td>
          <td>${f.filename || ""}</td>
          <td class="small">${f.uploaded_at || ""}</td>
          <td>
            <button class="delete-btn" data-id="${f.id}" style="margin-top:0; background:#dc2626; padding:4px 8px; font-size:0.8rem;">삭제</button>
          </td>
        `;
        fileTableBody.appendChild(tr);
      });

      // 삭제 버튼 이벤트 리스너 추가
      document.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
          const fileId = e.target.getAttribute("data-id");
          if (confirm("정말 삭제하시겠습니까? (복구 불가)")) {
            await deleteFile(fileId);
          }
        });
      });
    } catch (err) {
      console.error(err);
      fileTableBody.innerHTML = `
        <tr><td colspan="4" class="small">파일 목록을 불러오는 중 오류가 발생했습니다.</td></tr>
      `;
    }
  }

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("file");
    const displayNameInput = document.getElementById("displayName");

    if (!fileInput.files.length) {
      alert("업로드할 파일을 선택해 주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (displayNameInput.value.trim()) {
      formData.append("display_name", displayNameInput.value.trim());
    }

    uploadBtn.disabled = true;
    uploadStatus.textContent = "업로드 및 인덱싱 중입니다… (조금 걸릴 수 있어요)";
    uploadStatus.className = "status";

    try {
      const res = await fetch("/api/admin/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok || !data.ok) {
        const msg = data.error || "업로드 중 오류가 발생했습니다.";
        uploadStatus.textContent = msg;
        uploadStatus.className = "status err";
      } else {
        uploadStatus.textContent = "업로드 및 인덱싱이 완료되었습니다!";
        uploadStatus.className = "status ok";
        fileInput.value = "";
        displayNameInput.value = "";
        await loadFiles();
      }
    } catch (err) {
      console.error(err);
      uploadStatus.textContent = "요청 중 오류가 발생했습니다.";
      uploadStatus.className = "status err";
    } finally {
      uploadBtn.disabled = false;
    }
  });

  // 처음 진입 시 파일 목록 로딩
  loadFiles();

  async function deleteFile(fileId) {
    try {
      const res = await fetch(`/api/admin/files/${fileId}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (!res.ok || !data.ok) {
        alert("삭제 실패: " + (data.error || "알 수 없는 오류"));
      } else {
        alert("삭제되었습니다.");
        await loadFiles();
      }
    } catch (err) {
      console.error(err);
      alert("삭제 요청 중 오류가 발생했습니다.");
    }
  }
});
