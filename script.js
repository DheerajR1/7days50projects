const state = {
  processedFiles: [
    {
      id: crypto.randomUUID(),
      fileName: "qa_regression_run_15.xlsx",
      project: "Checkout UI",
      sheetNumber: 1,
      type: "Functional Regression",
      parser: "ExcelTestReportParserV3",
      datasetId: "ds_98345",
      rows: 382,
      columns: 16,
      passes: 347,
      fails: 35
    }
  ],
  startTime: performance.now()
};

const uploadModal = document.getElementById("uploadModal");
const openUploadModal = document.getElementById("openUploadModal");
const cancelUpload = document.getElementById("cancelUpload");
const uploadForm = document.getElementById("uploadForm");
const processedFilesList = document.getElementById("processedFilesList");
const elapsedTime = document.getElementById("elapsedTime");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatWindow = document.getElementById("chatWindow");

function renderFiles() {
  processedFilesList.innerHTML = "";

  if (!state.processedFiles.length) {
    const empty = document.createElement("li");
    empty.className = "file-item";
    empty.textContent = "No files processed yet.";
    processedFilesList.appendChild(empty);
    return;
  }

  state.processedFiles.forEach((file) => {
    const item = document.createElement("li");
    item.className = "file-item";

    item.innerHTML = `
      <button class="file-btn" type="button" aria-expanded="false">
        <div class="file-name">${file.fileName}</div>
        <div class="file-meta">${file.project} • Sheet ${file.sheetNumber} • ${file.type}</div>
      </button>
      <div class="file-details">
        <div><strong>Parser:</strong> ${file.parser}</div>
        <div><strong>Dataset ID:</strong> ${file.datasetId}</div>
        <div><strong>Rows:</strong> ${file.rows}</div>
        <div><strong>Columns:</strong> ${file.columns}</div>
        <div><strong>Passes:</strong> ${file.passes}</div>
        <div><strong>Fails:</strong> ${file.fails}</div>
      </div>
    `;

    const button = item.querySelector(".file-btn");
    button.addEventListener("click", () => {
      const expanded = item.classList.toggle("expanded");
      button.setAttribute("aria-expanded", String(expanded));
    });

    processedFilesList.appendChild(item);
  });
}

function addMessage(text, role) {
  const article = document.createElement("article");
  article.className = `msg ${role === "user" ? "user-msg" : "assistant-msg"}`;

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.appendChild(paragraph);

  chatWindow.appendChild(article);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

openUploadModal.addEventListener("click", () => {
  uploadForm.reset();
  uploadModal.showModal();
});

cancelUpload.addEventListener("click", () => {
  uploadModal.close();
});

uploadForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(uploadForm);
  const reportFile = formData.get("reportFile");
  const projectName = formData.get("projectName");
  const sheetNumber = Number(formData.get("sheetNumber"));
  const type = formData.get("fileType");

  if (!reportFile || !projectName || !sheetNumber || !type) {
    return;
  }

  const rows = Math.floor(100 + Math.random() * 500);
  const fails = Math.floor(Math.random() * Math.max(1, Math.floor(rows * 0.2)));
  const passes = rows - fails;

  state.processedFiles.unshift({
    id: crypto.randomUUID(),
    fileName: reportFile.name,
    project: projectName.toString(),
    sheetNumber,
    type: type.toString(),
    parser: type === "Performance" ? "PerfReportParserV1" : "ExcelTestReportParserV3",
    datasetId: `ds_${Math.floor(10000 + Math.random() * 90000)}`,
    rows,
    columns: Math.floor(8 + Math.random() * 12),
    passes,
    fails
  });

  renderFiles();
  uploadModal.close();

  addMessage(`Uploaded and processed ${reportFile.name}. You can now ask report-related questions.`, "assistant");
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const question = chatInput.value.trim();
  if (!question) {
    return;
  }

  addMessage(question, "user");
  chatInput.value = "";

  const latest = state.processedFiles[0];
  const response = latest
    ? `For ${latest.fileName}, I processed ${latest.rows} rows and ${latest.columns} columns with ${latest.passes} passes and ${latest.fails} fails. Want module-level breakdown?`
    : "Please upload a test report first so I can answer with dataset context.";

  window.setTimeout(() => addMessage(response, "assistant"), 350);
});

window.setInterval(() => {
  const elapsedSeconds = (performance.now() - state.startTime) / 1000;
  elapsedTime.textContent = `${elapsedSeconds.toFixed(2)}s`;
}, 100);

renderFiles();
