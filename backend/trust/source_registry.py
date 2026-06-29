from urllib.parse import urlparse

class SourceRegistry:
    def __init__(self):
        # Configure trusted domains by Tier
        self.tier1_domains = {
            "reuters.com", "apnews.com", "who.int", "nasa.gov", 
            "isro.gov.in", "cdc.gov", "un.org", "europa.eu"
        }
        
        self.tier2_domains = {
            "nytimes.com", "wsj.com", "bbc.com", "bbc.co.uk", "theguardian.com",
            "wikipedia.org", "nature.com", "science.org", "mit.edu", "harvard.edu",
            "stanford.edu"
        }
        
        self.tier3_domains = {
            "medium.com", "substack.com", "blogspot.com", "wp.com",
            "independent.co.uk", "wired.com", "techcrunch.com"
        }
        
        # Social media / user-generated content defaults to Tier 4
        self.tier4_domains = {
            "twitter.com", "x.com", "reddit.com", "facebook.com", 
            "instagram.com", "youtube.com", "tiktok.com", "quora.com"
        }

    def get_source_tier(self, url: str) -> int:
        try:
            parsed = urlparse(url)
            domain = parsed.hostname
            if not domain:
                return 4
            
            domain = domain.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            # Exact match checks
            if domain in self.tier1_domains or domain.endswith(".gov") or domain.endswith(".mil"):
                return 1
            if domain in self.tier2_domains or domain.endswith(".edu"):
                return 2
            if domain in self.tier3_domains:
                return 3
            if domain in self.tier4_domains:
                return 4
                
            # Fallback checks (subdomains)
            for d in self.tier1_domains:
                if domain.endswith("." + d):
                    return 1
            for d in self.tier2_domains:
                if domain.endswith("." + d):
                    return 2
            for d in self.tier3_domains:
                if domain.endswith("." + d):
                    return 3
                    
            return 3  # General web fallback is Tier 3
        except Exception:
            return 4

    def evaluate_evidence(self, urls: list) -> tuple:
        """
        Evaluate a list of source URLs.
        Returns (Evidence Quality: str, Reason: str)
        """
        if not urls:
            return "Low", "No supporting sources or references found."

        tiers = [self.get_source_tier(url) for url in urls]
        
        tier1_count = tiers.count(1)
        tier2_count = tiers.count(2)
        tier3_count = tiers.count(3)
        tier4_count = tiers.count(4)

        if tier1_count >= 2:
            return "High", f"Supported by multiple Tier 1 sources ({tier1_count} highest-trust sources found)."
        elif tier1_count == 1 or tier2_count >= 2:
            return "Medium", "Supported by established news organizations or academic institutions."
        elif tier3_count >= 1:
            return "Medium", "Supported primarily by independent media or verified blogs."
        else:
            return "Low", "Evidence relies heavily on social media or unverified user-generated forums."

source_registry = SourceRegistry()
