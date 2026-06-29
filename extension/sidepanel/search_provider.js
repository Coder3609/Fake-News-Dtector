class SearchProvider {
  async search(query, apiKey) {
    if (!apiKey) {
      throw new Error("Missing Tavily API Key. Please add it in Options.");
    }
    
    try {
      const response = await fetch("https://api.tavily.com/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          api_key: apiKey,
          query: query,
          search_depth: "advanced",
          include_answer: false,
          include_images: false,
          include_raw_content: false,
          max_results: 5
        })
      });

      if (!response.ok) {
        throw new Error(`Tavily API failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.results || [];
    } catch (e) {
      console.error("SearchProvider error:", e);
      return [];
    }
  }
}

window.SearchProvider = SearchProvider;
