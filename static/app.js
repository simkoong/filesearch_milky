document.addEventListener("DOMContentLoaded", () => {
  const questionEl = document.getElementById("question");
  const answerEl = document.getElementById("answer");
  const sendBtn = document.getElementById("sendBtn");
  const loadingEl = document.getElementById("loading");

  async function sendQuestion() {
    const question = questionEl.value.trim();
    if (!question) {
      alert("질문을 입력해 주세요.");
      return;
    }

    sendBtn.disabled = true;
    loadingEl.style.display = "block";
    answerEl.textContent = "";

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      if (!res.ok) {
        answerEl.textContent = data.error || "오류가 발생했습니다.";
      } else {
        answerEl.textContent = data.answer || "(빈 응답)";
      }
    } catch (err) {
      console.error(err);
      answerEl.textContent = "요청 중 오류가 발생했습니다.";
    } finally {
      sendBtn.disabled = false;
      loadingEl.style.display = "none";
    }
  }

  sendBtn.addEventListener("click", sendQuestion);

  // Ctrl+Enter로 전송
  questionEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      sendQuestion();
    }
  });
});

