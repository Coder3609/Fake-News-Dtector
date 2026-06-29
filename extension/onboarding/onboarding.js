// Onboarding Slides Controller
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.progress-dot');
let currentSlideIndex = 0;

function goToSlide(index) {
  slides[currentSlideIndex].classList.remove('active');
  dots[currentSlideIndex].classList.remove('active');
  
  currentSlideIndex = index;
  
  slides[currentSlideIndex].classList.add('active');
  dots[currentSlideIndex].classList.add('active');
}

// Slide 1: Welcome -> Auth
document.getElementById('btn-welcome-next').addEventListener('click', () => {
  goToSlide(1);
});

// Slide 2: Google Login -> Permissions
document.getElementById('btn-google-login').addEventListener('click', async () => {
  try {
    chrome.identity.getAuthToken({ interactive: true }, async function(token) {
      if (chrome.runtime.lastError || !token) {
        console.error("Auth error:", chrome.runtime.lastError);
        goToSlide(2); // Fallback to permissions if user cancels or errors
        return;
      }
      
      // We got the Google OAuth token!
      // Send it to our backend to exchange for a Supabase session
      try {
        const response = await fetch("http://127.0.0.1:8010/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider: "google", access_token: token })
        });
        const data = await response.json();
        
        // Save the backend session token
        await chrome.storage.local.set({ 
          userToken: data.token
        });
        
        console.log("Successfully authenticated with TruthLens backend.");
        goToSlide(2);
      } catch (backendErr) {
        console.error("Backend auth error:", backendErr);
        goToSlide(2);
      }
    });
  } catch (err) {
    console.error("Auth UI error:", err);
    goToSlide(2);
  }
});

// Guest Flow
document.getElementById('link-skip-auth').addEventListener('click', (e) => {
  e.preventDefault();
  goToSlide(2);
});

// Slide 3: Permissions -> Activation
document.getElementById('btn-grant-permissions').addEventListener('click', () => {
  // Request optional host permissions for supported social platforms
  const targetOrigins = [
    "https://*.x.com/*",
    "https://*.twitter.com/*",
    "https://*.youtube.com/*",
    "https://*.reddit.com/*"
  ];

  chrome.permissions.request({
    origins: targetOrigins
  }, (granted) => {
    if (granted) {
      console.log("Host permissions granted successfully.");
      // Progress to final slide automatically
      goToSlide(3);
    } else {
      console.warn("Permissions denied or dismissed.");
      // For developer testing / smooth UX, progress anyway
      goToSlide(3);
    }
  });
});

// Slide 4: Start Browsing -> Close Onboarding
document.getElementById('btn-start-browsing').addEventListener('click', async () => {
  // Set onboarding complete
  await chrome.storage.local.set({ onboardingComplete: true });
  
  // Close the current onboarding tab
  window.close();
});
