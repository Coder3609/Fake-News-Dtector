chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === "install") {
    // Open the onboarding page on installation
    chrome.tabs.create({ url: chrome.runtime.getURL("onboarding/onboarding.html") });
  }
});

// Configure side panel to open when clicking the action icon
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));

// Global job store to bridge data from content script to side panel
let activeJob = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "START_VERIFICATION") {
    const tabId = sender.tab?.id;
    if (!tabId) {
      sendResponse({ error: "No active tab" });
      return;
    }

    activeJob = {
      tabId: tabId,
      payload: message.payload,
      status: "queued"
    };

    // Open side panel for this tab
    chrome.sidePanel.open({ tabId })
      .then(() => {
        // Notify the side panel after it opens
        setTimeout(() => {
          chrome.runtime.sendMessage({
            action: "TRIGGER_VERIFICATION",
            job: activeJob
          });
        }, 500);
      })
      .catch((error) => {
        console.error("Error opening side panel:", error);
      });

    sendResponse({ success: true });
  } else if (message.action === "GET_ACTIVE_JOB") {
    sendResponse({ job: activeJob });
  } else if (message.action === "CLEAR_ACTIVE_JOB") {
    activeJob = null;
    sendResponse({ success: true });
  }
});
