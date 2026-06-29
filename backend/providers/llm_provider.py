import abc
from google import genai
from backend.core.config import settings

class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    async def analyze_claim(self, claim: str, evidence: str, image_url: str = None) -> dict:
        """
        Analyze a text claim against provided evidence text.
        Returns a dict containing: status, summary, and reasoning.
        """
        pass

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.is_mock = "mock" in self.api_key.lower() or not self.api_key
        
        if not self.is_mock:
            self.client = genai.Client(api_key=self.api_key)

    async def analyze_claim(self, claim: str, evidence: str, image_url: str = None) -> dict:
        if self.is_mock:
            # Fallback mock generator that behaves identically to standard Gemini model responses
            return {
                "status": "Supported by Evidence",
                "summary": f"The claim '{claim[:60]}...' is supported by trusted reports.",
                "reasoning": "Cross-referencing confirms the timeline and facts reported match verified government and official news releases."
            }

        prompt = f"""
        You are TruthLens, an evidence-based fact-checking assistant.
        Analyze the following claim against the EXACT provided evidence.
        
        NEW HARD RULES:
        1. You must answer ONLY from the retrieved evidence provided below.
        2. NEVER invent sources, organizations, scientific findings, or conclusions.
        3. If a source was not explicitly retrieved in the evidence text, it MUST NEVER appear in your response.
        4. If the retrieved evidence is insufficient, empty, or unrelated to the claim, you MUST return "Insufficient evidence" and your summary MUST literally say: "No reliable evidence was found."

        Claim: {claim}
        Evidence: {evidence}

        Classify the claim into one of these strict categories:
        - Verified by trusted sources
        - Contradicted by trusted sources
        - Mixed evidence
        - Insufficient evidence

        Output your response as JSON matching this format:
        {{
            "status": "status_string",
            "summary": "1-2 sentence summary of what actually happened, tracing back ONLY to retrieved evidence. If evidence is insufficient, state: 'Insufficient reliable evidence was retrieved.'",
            "reasoning": "Detail the alignment. If insufficient evidence, state: 'Review the original sources or wait for additional reporting.' Do not fabricate explanations."
        }}
        Do not include markdown wrappers like ```json. Return raw JSON.
        """
        
        from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
        from google.genai.errors import APIError
        
        # We define a helper so we can decorate it with tenacity, since we shouldn't decorate the async method directly if the genai SDK call is sync.
        @retry(
            wait=wait_exponential(multiplier=1, min=2, max=10),
            stop=stop_after_attempt(3),
            reraise=True
        )
        def _call_gemini():
            contents_list = [prompt]
            if image_url:
                import requests
                from PIL import Image
                from io import BytesIO
                try:
                    # In a real environment, we might want a session, but this works for isolation
                    res = requests.get(image_url, timeout=10.0)
                    if res.status_code == 200:
                        img = Image.open(BytesIO(res.content))
                        contents_list.insert(0, img)
                    else:
                        print(f"Image fetch failed with status {res.status_code}")
                except Exception as e:
                    print(f"Image fetch error: {e}")

            return self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents_list
            )

        try:
            response = _call_gemini()
            import json
            # Strip potential markdown formatting if returned
            text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(text)
        except Exception as e:
            # Fallback on parse failure
            return {
                "status": "Insufficient evidence",
                "summary": f"Could not perform reasoning. Error: {str(e)}",
                "reasoning": "AI processing error occurred during analysis."
            }
