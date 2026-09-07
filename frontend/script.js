const API_BASE = "http://localhost:5000";

const form = document.getElementById("ad-form");
const generateBtn = document.getElementById("generate-btn");
const btnLabel = document.getElementById("btn-label");
const errorMsg = document.getElementById("error-msg");

const stageEmpty = document.getElementById("stage-empty");
const stageLoading = document.getElementById("stage-loading");
const stageResult = document.getElementById("stage-result");
const loadingText = document.getElementById("loading-text");
const resultImage = document.getElementById("result-image");

const stageFooter = document.getElementById("stage-footer");
const metaTagline = document.getElementById("meta-tagline");
const metaCta = document.getElementById("meta-cta");
const downloadBtn = document.getElementById("download-btn");

const loadingMessages = [
  "Writing the copy…",
  "Mixing the palette…",
  "Rendering the visual…",
  "Setting the type…",
];

let loadingInterval;
let lastImageDataUrl = null;

function showState(state) {
  stageEmpty.hidden = state !== "empty";
  stageLoading.hidden = state !== "loading";
  stageResult.hidden = state !== "result";
  stageFooter.hidden = state !== "result";

  if (state !== "result") {
    stageResult.classList.remove("is-visible");
    stageFooter.classList.remove("is-visible");
  } else {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        stageResult.classList.add("is-visible");
        stageFooter.classList.add("is-visible");
      });
    });
  }
}

function startLoadingMessages() {
  let i = 0;
  loadingText.textContent = loadingMessages[0];
  loadingInterval = setInterval(() => {
    i = (i + 1) % loadingMessages.length;
    loadingText.textContent = loadingMessages[i];
  }, 2200);
}

function stopLoadingMessages() {
  clearInterval(loadingInterval);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.textContent = "";

  const payload = {
    product_name: document.getElementById("product_name").value.trim(),
    product_description: document.getElementById("product_description").value.trim(),
    audience: document.getElementById("audience").value.trim(),
    mood: document.getElementById("mood").value,
    platform: document.getElementById("platform").value,
  };

  generateBtn.disabled = true;
  btnLabel.textContent = "Generating…";
  showState("loading");
  startLoadingMessages();

  try {
    const res = await fetch(`${API_BASE}/api/generate-ad`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Something went wrong. Try again.");
    }

    resultImage.src = data.image_base64;
    lastImageDataUrl = data.image_base64;
    metaTagline.textContent = data.tagline;
    metaCta.textContent = data.cta;
    showState("result");
  } catch (err) {
    errorMsg.textContent = err.message;
    showState("empty");
  } finally {
    stopLoadingMessages();
    generateBtn.disabled = false;
    btnLabel.textContent = "Generate ad concept";
  }
});

downloadBtn.addEventListener("click", () => {
  if (!lastImageDataUrl) return;
  const a = document.createElement("a");
  a.href = lastImageDataUrl;
  a.download = "ad-concept.png";
  a.click();
});