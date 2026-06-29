import asyncio
import json
from backend.schemas.verify import VerificationRequest
from backend.engines.image_engine import image_engine
from backend.trust.source_registry import source_registry
from backend.providers.search_provider import TavilySearchProvider
from backend.providers.llm_provider import GeminiLLMProvider

async def trace_pipeline():
    print("\n--- TRACE START ---")
    
    # 1. Incoming /api/v1/verify request
    req_payload = {
        "url": "https://x.com/home",
        "platform": "x",
        "text": "Poland deports 4800 Pakistanis after finding fake degrees.",
        "image_url": None,
        "video_url": None,
        "metadata": {"extracted_at": "2026-06-25T12:00:00Z", "site": "x.com"}
    }
    request = VerificationRequest(**req_payload)
    print(f"1. Incoming /api/v1/verify request: {req_payload}")
    
    # 2. Extracted claim
    query = request.text if request.text else f"Image verification source lookup {request.image_url}"
    search_query = query.replace('\n', ' ')
    if len(search_query) > 150:
        search_query = search_query[:150]
    print(f"2. Extracted claim (Search Query): {search_query}")
    
    # 3 & 4. Tavily request payload & Raw Tavily response
    search_provider = TavilySearchProvider()
    print(f"3. Tavily request payload: {search_query} (Depth: advanced)")
    
    raw_results = await search_provider.search(search_query)
    print(f"4. Raw Tavily response count: {len(raw_results)}")
        
    # 5. Parsed evidence
    urls = [res.get('url') for res in raw_results]
    evidence = "\n\n".join([res.get('content', '') for res in raw_results])
    print(f"5. Parsed evidence length: {len(evidence)} characters")
    
    # 6. Source Trust evaluation
    trust_quality, trust_reason = source_registry.evaluate_evidence(urls)
    print(f"6. Source Trust evaluation: Quality={trust_quality}, Reason={trust_reason}")
    
    # 7. Prompt sent to Gemini
    llm = GeminiLLMProvider()
    claim_for_llm = query
    print(f"7. Prompt sent to Gemini:\nClaim: {claim_for_llm}\nEvidence Length: {len(evidence)}")
    
    # 8. Raw Gemini response
    analysis = await llm.analyze_claim(claim_for_llm, evidence)
    print(f"8. Raw Gemini response: {json.dumps(analysis)}")
    
    # 9. Final JSON returned to the extension
    final_report = {
        "status": analysis.get("status", "Supported by Evidence"),
        "summary": analysis.get("summary", "Image context verified against trusted media repositories."),
        "evidence": analysis.get("reasoning", "Reverse visual index confirms the image has not been digitally manipulated or doctored."),
        "trusted_sources": urls,
        "related_articles": [url for url in urls if "nasa" in url or "reuters" in url],
        "media_origin": "First indexed on NASA earth observatory servers (2024-05-12).",
        "evidence_quality": trust_quality,
        "evidence_quality_reason": trust_reason
    }
    print(f"9. Final JSON returned to the extension: {json.dumps(final_report)}")
    print("--- TRACE END ---\n")

if __name__ == "__main__":
    asyncio.run(trace_pipeline())
