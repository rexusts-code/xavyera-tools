import json
import os

USAGE_FILE = os.path.expanduser("~/.xavyera_usage.json")

TIERS = {
    "silver": 5000,
    "gold": 10000,
    "master": float('inf')
}

class QuotaManager:
    def __init__(self, tier: str = "silver"):
        self.tier = tier.lower()
        self.limit = TIERS.get(self.tier, 5000)
        self.usage = self._load_usage()

    def _load_usage(self) -> int:
        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get("usage", 0)
            except:
                return 0
        return 0

    def _save_usage(self):
        with open(USAGE_FILE, 'w') as f:
            json.dump({"usage": self.usage, "tier": self.tier}, f)

    def add_usage(self, tokens: int):
        self.usage += tokens
        self._save_usage()

    def is_exhausted(self) -> bool:
        return self.usage >= self.limit

    def get_remaining(self) -> str:
        if self.limit == float('inf'):
            return "Unlimited"
        remaining = self.limit - self.usage
        return str(max(0, remaining))

    def estimate_tokens(self, text: str) -> int:
        # Simple approximation: 1 token ~= 4 characters
        return len(text) // 4
