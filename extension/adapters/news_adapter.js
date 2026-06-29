class NewsAdapter {
  detectPosts() {
    // Looks for typical article layout tags on news sites
    const articles = document.querySelectorAll('article, main, .article-container, .post-content');
    return articles.length > 0 ? Array.from(articles).slice(0, 1) : []; // Verify page as a single article unit
  }

  injectTruthLensButton(post) {
    // Find the main headline (h1)
    const h1 = post.querySelector('h1') || document.querySelector('h1');
    if (!h1 || document.querySelector('.truthlens-btn')) return;

    const btn = document.createElement('button');
    btn.className = 'truthlens-btn news-btn';
    btn.type = 'button';
    btn.title = "Verify this news article with TruthLens";
    btn.innerHTML = `
      <div class="tl-btn-inner">
        <span class="tl-icon-small">TL</span>
        <span class="tl-btn-text">Verify Article</span>
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

    // Place it cleanly after the headline
    h1.parentNode.insertBefore(btn, h1.nextSibling);
  }

  extractContent(post) {
    const h1 = post.querySelector('h1') || document.querySelector('h1');
    const title = h1 ? h1.innerText : document.title;

    // Collect first 4 paragraphs as representative text
    const paragraphs = Array.from(post.querySelectorAll('p'))
      .map(p => p.innerText.trim())
      .filter(t => t.length > 30)
      .slice(0, 4)
      .join('\n\n');

    const text = `Title: ${title}\n\nContent:\n${paragraphs}`;

    // Extract primary article image
    const imageEl = post.querySelector('img');
    const image_url = imageEl ? imageEl.src : null;

    return { text, image_url };
  }

  buildVerificationPayload(post) {
    const { text, image_url } = this.extractContent(post);
    return {
      url: window.location.href,
      platform: "news",
      text: text,
      image_url: image_url,
      video_url: null,
      metadata: {
        title: document.title,
        extracted_at: new Date().toISOString(),
        site: window.location.hostname
      }
    };
  }
}

// Assign to window for content.js discovery
window.NewsAdapter = NewsAdapter;
