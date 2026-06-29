// Standalone Architecture - No Backend URL needed

// DOM Elements
const stateIdle = document.getElementById('state-idle');
const stateLoading = document.getElementById('state-loading');
const stateResult = document.getElementById('state-result');
const stateError = document.getElementById('state-error');

const loadingHeader = document.getElementById('loading-header');
const progressList = document.getElementById('progress-list');
const btnReset = document.getElementById('btn-reset');
const btnRetry = document.getElementById('btn-error-retry');
const btnSave = document.getElementById('btn-save-report');

// Result Elements
const resultStatusBadge = document.getElementById('result-status-badge');
const resultStatusText = document.getElementById('result-status-text');
const resultSummary = document.getElementById('result-summary');
const resultEvidence = document.getElementById('result-evidence');
const resultTrustLevel = document.getElementById('result-trust-level');
const resultTrustReason = document.getElementById('result-trust-reason');
const cardMediaOrigin = document.getElementById('card-media-origin');
const resultMediaOrigin = document.getElementById('result-media-origin');
const resultSources = document.getElementById('result-sources');
const resultRelated = document.getElementById('result-related');

// Error Elements
const errorMessage = document.getElementById('error-message');

let currentActiveJob = null;
let pollingInterval = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  // Check if there is an active job already in background
  chrome.runtime.sendMessage({ action: "GET_ACTIVE_JOB" }, (response) => {
    if (response && response.job) {
      startVerificationFlow(response.job);
    } else {
      showState('idle');
    }
  });
});

// Reset panel click
btnReset.addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: "CLEAR_ACTIVE_JOB" });
  stopPolling();
  showState('idle');
});

// Retry click
btnRetry.addEventListener('click', () => {
  if (currentActiveJob) {
    startVerificationFlow(currentActiveJob);
  } else {
    showState('idle');
  }
});

// Listen for incoming verifications
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "TRIGGER_VERIFICATION" && message.job) {
    startVerificationFlow(message.job);
  }
});

function showState(state) {
  stateIdle.classList.remove('active');
  stateLoading.classList.remove('active');
  stateResult.classList.remove('active');
  stateError.classList.remove('active');

  if (state === 'idle') stateIdle.classList.add('active');
  else if (state === 'loading') stateLoading.classList.add('active');
  else if (state === 'result') stateResult.classList.add('active');
  else if (state === 'error') stateError.classList.add('active');
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}

async function startVerificationFlow(job) {
  currentActiveJob = job;
  showState('loading');
  resetProgressSteps();
  stopPolling();

  const isVideo = job.payload.video_url || job.payload.content_type === 'video';
  loadingHeader.innerText = isVideo ? "Analyzing Video (Local)..." : "Analyzing Content (Local)...";

  try {
    // 1. Get API Keys
    const keys = await new Promise((resolve) => {
      chrome.storage.local.get(['GEMINI_API_KEY', 'TAVILY_API_KEY'], resolve);
    });

    if (!keys.GEMINI_API_KEY || !keys.TAVILY_API_KEY) {
      throw new Error("Missing API Keys! Please click the TruthLens icon -> Options to set them.");
    }

    const searchProvider = new window.SearchProvider();
    const llmProvider = new window.LLMProvider();

    // 2. Extract and Search
    updateProgressUI('validate');
    const claimText = job.payload.text || "Tweet containing media";
    const imageUrl = job.payload.image_url;
    
    updateProgressUI('searching');
    const searchResults = await searchProvider.search(claimText, keys.TAVILY_API_KEY);
    
    const evidenceText = searchResults.map(res => res.content).join("\\n\\n");
    const sourceUrls = searchResults.map(res => res.url);

    // 3. Reason with LLM
    updateProgressUI('reasoning');
    let claimForLLM = claimText;
    if (imageUrl) {
      claimForLLM = `User is asking about this image. The accompanying text is: ${claimText}`;
    }

    const analysis = await llmProvider.analyzeClaim(claimForLLM, evidenceText, keys.GEMINI_API_KEY, imageUrl);

    // 4. Calculate Trust Layer mock based on result count
    updateProgressUI('trust');
    let trustQuality = sourceUrls.length > 0 ? "Medium" : "Low";
    let trustReason = sourceUrls.length > 0 ? "Supported primarily by independent media or verified blogs." : "No supporting sources or references found.";

    const finalReport = {
      verification_id: "local-" + Date.now(),
      status: analysis.status || "Insufficient evidence",
      summary: analysis.summary || "No reliable evidence was found.",
      evidence: analysis.reasoning || "Review the original sources or wait for additional reporting.",
      trusted_sources: sourceUrls,
      related_articles: [],
      evidence_quality: trustQuality,
      evidence_quality_reason: trustReason
    };

    updateProgressUI('completed');
    renderReport(finalReport);
    showState('result');

  } catch (error) {
    console.error("Verification failed:", error);
    errorMessage.innerText = `Analysis Failed: ${error.message}`;
    showState('error');
  }
}

function pollJobStatus() {
  // Deprecated in standalone mode
}

function resetProgressSteps() {
  const steps = progressList.querySelectorAll('.step-item');
  steps.forEach(step => {
    step.className = 'step-item';
  });
}

function updateProgressUI(progressText) {
  if (!progressText) return;
  const text = progressText.toLowerCase();
  
  const markActive = (stepId) => {
    const steps = ['step-validate', 'step-extract', 'step-fingerprint', 'step-search', 'step-reason', 'step-trust'];
    let reached = false;
    steps.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (id === stepId) {
        el.className = 'step-item active';
        reached = true;
      } else if (!reached) {
        el.className = 'step-item completed';
      } else {
        el.className = 'step-item';
      }
    });
  };

  if (text.includes("completed")) {
    const steps = progressList.querySelectorAll('.step-item');
    steps.forEach(step => {
      step.className = 'step-item completed';
    });
  } else if (text.includes("received") || text.includes("queue") || text.includes("validate")) {
    markActive('step-validate');
  } else if (text.includes("extracting") || text.includes("speech")) {
    markActive('step-extract');
  } else if (text.includes("cache") || text.includes("syntax") || text.includes("indices")) {
    markActive('step-fingerprint');
  } else if (text.includes("references") || text.includes("registries") || text.includes("searching")) {
    markActive('step-search');
  } else if (text.includes("frames") || text.includes("reasoning")) {
    markActive('step-reason');
  } else if (text.includes("tiers") || text.includes("source")) {
    markActive('step-trust');
  }
}

function renderReport(report) {
  // 1. Status Badge
  resultStatusText.innerText = report.status;
  resultStatusBadge.className = 'status-badge'; // reset
  
  const statusLower = report.status.toLowerCase();
  if (statusLower.includes('supported')) {
    resultStatusBadge.classList.add('supported');
  } else if (statusLower.includes('contradict')) {
    resultStatusBadge.classList.add('contradicted');
  } else if (statusLower.includes('mixed')) {
    resultStatusBadge.classList.add('mixed');
  } else {
    resultStatusBadge.classList.add('unable');
  }

  // 2. Text Details
  resultSummary.innerText = report.summary;
  resultEvidence.innerText = report.evidence;

  // 3. Trust level
  resultTrustLevel.innerText = report.evidence_quality;
  resultTrustReason.innerText = report.evidence_quality_reason;

  // 4. Media Origin
  if (report.media_origin) {
    cardMediaOrigin.style.display = 'block';
    resultMediaOrigin.innerText = report.media_origin;
  } else {
    cardMediaOrigin.style.display = 'none';
  }

  // 5. Sources Lists
  resultSources.innerHTML = '';
  if (report.trusted_sources && report.trusted_sources.length > 0) {
    report.trusted_sources.forEach(src => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = src;
      a.target = '_blank';
      a.innerText = getDomainName(src);
      li.appendChild(a);
      resultSources.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.innerText = 'No sources listed.';
    resultSources.appendChild(li);
  }

  resultRelated.innerHTML = '';
  if (report.related_articles && report.related_articles.length > 0) {
    report.related_articles.forEach(art => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = art;
      a.target = '_blank';
      a.innerText = getDomainName(art);
      li.appendChild(a);
      resultRelated.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.innerText = 'No related articles.';
    resultRelated.appendChild(li);
  }

  // Save report action listener
  btnSave.onclick = async () => {
    btnSave.innerText = "Saving to Browser...";
    btnSave.disabled = true;
    try {
      chrome.storage.local.get(['saved_reports'], (res) => {
        const history = res.saved_reports || [];
        history.push(report);
        chrome.storage.local.set({ saved_reports: history }, () => {
          btnSave.innerHTML = "✅ Saved Locally";
        });
      });
    } catch (err) {
      console.error(err);
      btnSave.innerHTML = "❌ Failed to Save";
      setTimeout(() => {
        btnSave.innerHTML = "💾 Save Report";
        btnSave.disabled = false;
      }, 2000);
    }
  };
}

function getDomainName(urlStr) {
  try {
    const url = new URL(urlStr);
    return url.hostname.replace('www.', '');
  } catch (e) {
    return urlStr;
  }
}
