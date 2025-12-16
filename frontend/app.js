const API = "http://127.0.0.1:8000";

window.onload = () => {
  loadSummary();
};

// ================= UPLOAD =================
async function uploadFile() {
  const f = document.getElementById("uploadFileInput").files[0];
  const box = document.getElementById("uploadResult");
  if (!f) return box.innerText = "No file selected";

  const fd = new FormData();
  fd.append("file", f);

  const r = await fetch(`${API}/upload`, { method: "POST", body: fd });
  box.innerText = JSON.stringify(await r.json(), null, 2);
  loadSummary();
}

// ================= DOWNLOAD =================
async function downloadFile() {
  const hash = document.getElementById("downloadHashInput").value.trim();
  const box = document.getElementById("downloadResult");
  if (!hash) return;

  const r = await fetch(`${API}/download/${hash}`);
  if (!r.ok) return box.innerText = "File not found / verification failed";

  const blob = await r.blob();
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  const cd = r.headers.get("Content-Disposition");
  a.href = url;
  a.download = cd ? cd.split("filename=")[1].replace(/"/g, "") : "file";
  a.click();
  URL.revokeObjectURL(url);
}

// ================= SUMMARY =================
async function loadSummary() {
  const r = await fetch(`${API}/summary`);
  const data = await r.json();

  const box = document.getElementById("summaryBox");
  box.innerHTML = `<pre class="text-xs bg-slate-900 p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
}
