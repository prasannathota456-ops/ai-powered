/* ================= CONFIG ================= */

const API =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000"
    : "https://ai-powered11.vercel.app";

/* ================= PAGE NAV ================= */

function showPage(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById(page).classList.add("active");
}

/* ================= EMAIL ================= */

async function generateEmail() {
  try {
    const prompt = document.getElementById("emailPrompt").value.trim();
    if (!prompt) return alert("Please enter a prompt");

    const res = await fetch(`${API}/generate-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();

    document.getElementById("emailBox").innerText =
      data.email || data.error || "No response";

  } catch (err) {
    console.error(err);
    alert("Email generation failed");
  }
}

/* ================= CRM ================= */

async function saveLead() {
  try {
    const name = document.getElementById("leadName").value.trim();
    const company = document.getElementById("leadCompany").value.trim();
    const status = document.getElementById("leadStatus").value;

    if (!name || !company) return alert("Enter Name & Company");

    await fetch(`${API}/save-lead`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, company, status })
    });

    document.getElementById("leadName").value = "";
    document.getElementById("leadCompany").value = "";

    loadLeads();

  } catch (err) {
    console.error(err);
    alert("Failed to save lead");
  }
}

/* ================= LOAD LEADS ================= */

async function loadLeads() {
  try {
    const res = await fetch(`${API}/get-leads`);
    const data = await res.json();

    const board = document.getElementById("leadBoard");

    if (!data.leads || data.leads.length === 0) {
      board.innerHTML = "<p>No leads found</p>";
      return;
    }

    board.innerHTML = data.leads
      .map(l => `
        <p>
          <b>${l.name || "-"}</b> |
          ${l.company || "-"} |
          ${l.status || "New"}
        </p>
      `)
      .join("");

  } catch (err) {
    console.error("Load Leads Error:", err);
  }
}

/* ================= REPORT ================= */

window.generateReport = async function () {

  const topic = document.getElementById("topic").value.trim();
  const category = document.getElementById("category").value;

  if (!topic) {
    alert("Enter topic first");
    return;
  }

  try {
    const res = await fetch(`${API}/generate-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: category + " - " + topic
      })
    });

    const data = await res.json();

    document.getElementById("reportBox").innerText =
      data.report || data.error || "No response";

  } catch (err) {
    console.log(err);
    alert("Server error");
  }
};

/* ================= CHAT (FINAL FIXED) ================= */

window.sendChat = async function () {

  const input = document.getElementById("chatMsg");
  const box = document.getElementById("chatBox");

  const message = input.value.trim();
  if (!message) return;

  // show user message
  box.innerHTML += `<div><b>You:</b> ${message}</div>`;
  input.value = "";
  box.scrollTop = box.scrollHeight;

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const text = await res.text();

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { reply: text };
    }

    if (!res.ok) {
      box.innerHTML += `<div style="color:red;"><b>Error:</b> ${data.error || text}</div>`;
      return;
    }

    box.innerHTML += `<div><b>AI:</b> ${data.reply || "No response"}</div>`;
    box.scrollTop = box.scrollHeight;

  } catch (err) {
    console.error(err);
    box.innerHTML += `<div style="color:red;">Server Error</div>`;
  }
};

/* ================= INIT ================= */

window.onload = function () {
  loadLeads();
};