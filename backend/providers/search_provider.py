import abc
import httpx
from backend.core.config import settings

class BaseSearchProvider(abc.ABC):
    @abc.abstractmethod
    async def search(self, query: str) -> list:
        """
        Search for evidence matching the query.
        Returns a list of dicts with 'title', 'url', 'content', and 'raw_source' fields.
        """
        pass

class TavilySearchProvider(BaseSearchProvider):
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.is_mock = "mock" in self.api_key.lower() or not self.api_key

    async def search(self, query: str) -> list:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    print(f"Tavily search API failed with status {response.status_code}: {response.text}")
                    return []
            except Exception as e:
                print(f"Tavily search error: {str(e)}.")
                return []
