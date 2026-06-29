document.addEventListener('DOMContentLoaded', () => {
  const geminiInput = document.getElementById('geminiKey');
  const tavilyInput = document.getElementById('tavilyKey');
  const saveBtn = document.getElementById('saveBtn');
  const statusEl = document.getElementById('status');

  // Load saved keys
  chrome.storage.local.get(['GEMINI_API_KEY', 'TAVILY_API_KEY'], (result) => {
    if (result.GEMINI_API_KEY) geminiInput.value = result.GEMINI_API_KEY;
    if (result.TAVILY_API_KEY) tavilyInput.value = result.TAVILY_API_KEY;
  });

  // Save keys
  saveBtn.addEventListener('click', () => {
    const geminiKey = geminiInput.value.trim();
    const tavilyKey = tavilyInput.value.trim();

    chrome.storage.local.set({
      GEMINI_API_KEY: geminiKey,
      TAVILY_API_KEY: tavilyKey
    }, () => {
      statusEl.textContent = 'Keys saved successfully! You can now verify tweets.';
      setTimeout(() => {
        statusEl.textContent = '';
      }, 3000);
    });
  });
});
