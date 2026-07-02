/* ==========================================================
   FraudShield AI — chat frontend logic
   ========================================================== */

const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typingRow = document.getElementById("typingRow");
const sidebarShield = document.getElementById("sidebarShield");
const clearChatBtn = document.getElementById("clearChatBtn");

const statTotal = document.getElementById("statTotal");
const statScam = document.getElementById("statScam");
const statSafe = document.getElementById("statSafe");

const emergencyStepsList = document.getElementById("emergencyStepsList");
const emergencyModalEl = document.getElementById("emergencyModal");
const emergencyModal = new bootstrap.Modal(emergencyModalEl);

let stats = { total: 0, scam: 0, safe: 0 };

// ---------- Auto-grow textarea ---------- //
messageInput.addEventListener("input", () => {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
});

messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

// ---------- Helpers ---------- //
function scrollToBottom() {
  chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
}

function timeNow() {
  return new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function appendUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `
    <div class="avatar user-avatar"><i class="bi bi-person-fill"></i></div>
    <div class="bubble user-bubble">
      <p class="mb-0">${escapeHtml(text)}</p>
      <span class="bubble-time">${timeNow()}</span>
    </div>
  `;
  chatWindow.appendChild(row);
  scrollToBottom();
}

function riskColor(riskScore) {
  if (riskScore >= 80) return "var(--danger)";
  if (riskScore >= 55) return "#B85C1E";
  if (riskScore >= 30) return "#C99A00";
  return "var(--safe)";
}

function appendBotVerdict(result) {
  const isScam = result.scam_status === "Scam";
  const row = document.createElement("div");
  row.className = "msg-row bot";

  const stepsHtml = result.emergency_steps
    .map((s) => `<li>${escapeHtml(s)}</li>`)
    .join("");
  // stash steps for modal use
  row.dataset.steps = JSON.stringify(result.emergency_steps);

  row.innerHTML = `
    <div class="avatar bot-avatar"><i class="bi bi-shield-lock-fill"></i></div>
    <div class="bubble bot-bubble" style="padding:0; overflow:hidden;">
      <div class="verdict-card">
        <div class="verdict-header ${isScam ? "scam" : "safe"}">
          <i class="bi ${isScam ? "bi-exclamation-triangle-fill" : "bi-check-circle-fill"}"></i>
          <span>${isScam ? "Likely SCAM Detected" : "Message Appears Safe"}</span>
        </div>
        <div class="verdict-body">
          <div class="verdict-grid">
            <div class="verdict-metric">
              <span class="metric-label">Fraud Type</span>
              <span class="metric-value">${escapeHtml(result.fraud_type)}</span>
            </div>
            <div class="verdict-metric">
              <span class="metric-label">Confidence</span>
              <span class="metric-value">${result.confidence}%</span>
            </div>
            <div class="verdict-metric">
              <span class="metric-label">Risk Score</span>
              <span class="metric-value">${result.risk_score}/100</span>
            </div>
            <div class="verdict-metric">
              <span class="metric-label">Risk Level</span>
              <span class="risk-badge ${result.risk_level}">${result.risk_level}</span>
            </div>
          </div>
          <div class="risk-bar-track">
            <div class="risk-bar-fill" style="background:${riskColor(result.risk_score)}"></div>
          </div>
          <div class="advice-text">${escapeHtml(result.advice)}</div>
          <div class="verdict-actions">
            ${isScam ? `<button class="btn btn-danger btn-sm view-steps-btn"><i class="bi bi-life-preserver me-1"></i>Emergency Steps</button>` : ""}
            <a href="https://cybercrime.gov.in" target="_blank" rel="noopener" class="btn btn-outline-secondary btn-sm"><i class="bi bi-box-arrow-up-right me-1"></i>Report Portal</a>
          </div>
        </div>
      </div>
      <span class="bubble-time" style="padding:0 14px 10px; display:block;">FraudShield AI &middot; ${timeNow()}</span>
    </div>
  `;

  chatWindow.appendChild(row);
  scrollToBottom();

  // Animate risk bar after insertion
  requestAnimationFrame(() => {
    const fill = row.querySelector(".risk-bar-fill");
    setTimeout(() => { fill.style.width = result.risk_score + "%"; }, 80);
  });

  // Wire emergency modal button
  const stepsBtn = row.querySelector(".view-steps-btn");
  if (stepsBtn) {
    stepsBtn.addEventListener("click", () => {
      emergencyStepsList.innerHTML = result.emergency_steps
        .map((s) => `<li>${escapeHtml(s)}</li>`)
        .join("");
      emergencyModal.show();
    });
  }

  // Update shield state
  setShieldState(isScam);
}

function setShieldState(isScam) {
  if (isScam) {
    sidebarShield.classList.add("danger-state");
    sidebarShield.innerHTML = '<i class="bi bi-shield-fill-exclamation"></i>';
  } else {
    sidebarShield.classList.remove("danger-state");
    sidebarShield.innerHTML = '<i class="bi bi-shield-fill-check"></i>';
  }
}

function updateStats(isScam) {
  stats.total += 1;
  if (isScam) stats.scam += 1; else stats.safe += 1;
  statTotal.textContent = stats.total;
  statScam.textContent = stats.scam;
  statSafe.textContent = stats.safe;
}

function showTyping() {
  typingRow.classList.remove("d-none");
  scrollToBottom();
}
function hideTyping() {
  typingRow.classList.add("d-none");
}

function appendErrorMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="avatar bot-avatar"><i class="bi bi-shield-lock-fill"></i></div>
    <div class="bubble bot-bubble">
      <p class="mb-0 text-danger"><i class="bi bi-exclamation-circle me-1"></i>${escapeHtml(text)}</p>
    </div>
  `;
  chatWindow.appendChild(row);
  scrollToBottom();
}

// ---------- Submit handler ---------- //
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  appendUserMessage(text);
  messageInput.value = "";
  messageInput.style.height = "auto";
  sendBtn.disabled = true;

  showTyping();

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();

    // Minimum typing delay for natural feel
    await new Promise((r) => setTimeout(r, 500));
    hideTyping();

    if (!res.ok) {
      appendErrorMessage(data.error || "Something went wrong. Please try again.");
    } else {
      appendBotVerdict(data);
      updateStats(data.scam_status === "Scam");
    }
  } catch (err) {
    hideTyping();
    appendErrorMessage("Network error: could not reach FraudShield AI server.");
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
});

// ---------- Clear chat ---------- //
clearChatBtn?.addEventListener("click", () => {
  document.querySelectorAll(".msg-row").forEach((row, i) => {
    if (i > 0) row.remove(); // keep the welcome message
  });
  setShieldState(false);
});