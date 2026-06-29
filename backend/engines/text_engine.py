from backend.providers.llm_provider import GeminiLLMProvider
from backend.providers.search_provider import TavilySearchProvider

class TextVerificationEngine:
    def __init__(self):
        self.llm = GeminiLLMProvider()
        self.search_provider = TavilySearchProvider()

    async def verify(self, claim: str) -> dict:
        # 1. Clean query for Tavily (search engines fail on massive paragraphs)
        search_query = claim.replace('\n', ' ')
        if len(search_query) > 150:
            search_query = search_query[:150]
            
        # 2. Search for online evidence
        search_results = await self.search_provider.search(search_query)
        
        # 2. Extract texts and references
        evidence_snippets = []
        urls = []
        for res in search_results:
            evidence_snippets.append(f"Title: {res.get('title')}\nSource: {res.get('url')}\nContent: {res.get('content')}")
            urls.append(res.get('url'))

        evidence = "\n\n".join(evidence_snippets)
        
        # 3. Analyze query against collected evidence via LLM
        analysis = await self.llm.analyze_claim(claim, evidence)
        
        # Return results
        return {
            "status": analysis.get("status", "Unable to Verify"),
            "summary": analysis.get("summary", "Analysis completed."),
            "evidence": analysis.get("reasoning", "Evidence cross-reference matches standard parameters."),
            "trusted_sources": urls,
            "related_articles": [url for url in urls if "reuters" in url or "apnews" in url or "bbc" in url],
            "media_origin": None
        }

text_engine = TextVerificationEngine()
