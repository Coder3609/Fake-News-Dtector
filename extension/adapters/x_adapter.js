class XAdapter {
  detectPosts() {
    // Selects tweet containers on X
    return document.querySelectorAll('article[data-testid="tweet"]');
  }

  injectTruthLensButton(post) {
    // Find action group (reply, retweet, like, share icons bar)
    const actionGroup = post.querySelector('div[role="group"]');
    if (!actionGroup || post.querySelector('.truthlens-btn')) return;

    const btn = document.createElement('button');
    btn.className = 'truthlens-btn';
    btn.type = 'button';
    btn.title = "Verify claim with TruthLens";
    btn.innerHTML = `
      <div class="tl-btn-inner">
        <span class="tl-icon-small">TL</span>
      </div>
    `;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const payload = this.buildVerificationPayload(post);
      chrome.runtime.sendMessage({
        action: "START_VERIFICATION",
        payload: payload
      });
    });

    // In X, the share button is usually the last item in the group, we can append there
    actionGroup.appendChild(btn);
  }

  extractContent(post) {
    const textEl = post.querySelector('div[data-testid="tweetText"]');
    const text = textEl ? textEl.innerText : "";

    // Image extraction
    const imageEl = post.querySelector('div[data-testid="tweetPhoto"] img');
    const image_url = imageEl ? imageEl.src : null;

    // Video extraction
    const videoEl = post.querySelector('video');
    const video_url = videoEl ? videoEl.src : null;

    return { text, image_url, video_url };
  }

  buildVerificationPayload(post) {
    const { text, image_url, video_url } = this.extractContent(post);
    return {
      url: window.location.href,
      platform: "x",
      text: text || "Tweet containing media",
      image_url: image_url,
      video_url: video_url,
      metadata: {
        extracted_at: new Date().toISOString(),
        site: "x.com"
      }
    };
  }
}

// Assign to window to make it accessible by content.js
window.XAdapter = XAdapter;
