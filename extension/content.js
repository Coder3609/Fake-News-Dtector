// TruthLens Content Orchestrator
let adapter = null;

function initializeAdapter() {
  const host = window.location.hostname.toLowerCase();
  
  if (host.includes('x.com') || host.includes('twitter.com')) {
    if (window.XAdapter) {
      adapter = new window.XAdapter();
    }
  } else {
    console.log("[TruthLens] Unsupported domain. Aborting.");
    return;
  }

  if (adapter) {
    console.log("[TruthLens] Injected adapter for:", host);
    
    // Check if onboarding is complete before injecting buttons
    chrome.storage.local.get(["onboardingComplete"], (data) => {
      if (data.onboardingComplete) {
        injectButtons();
        observeDOM();
      } else {
        console.log("[TruthLens] Onboarding not complete, skipping injection.");
      }
    });
  }
}

function injectButtons() {
  if (!adapter) return;
  const posts = adapter.detectPosts();
  posts.forEach(post => {
    try {
      adapter.injectTruthLensButton(post);
    } catch (e) {
      console.error("[TruthLens] Error injecting button:", e);
    }
  });
}

function observeDOM() {
  // Mutation observer for infinite scrolling / dynamic loading
  const observer = new MutationObserver(() => {
    injectButtons();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Initialize content injection
if (document.readyState === "complete" || document.readyState === "interactive") {
  initializeAdapter();
} else {
  document.addEventListener("DOMContentLoaded", initializeAdapter);
}
