"""A scripted stand-in for anthropic.Anthropic() so tests make no network calls and cost nothing."""
from types import SimpleNamespace as NS

VALID = {
    "verdict": "benign", "category": "benign", "severity": "informational", "confidence": 0.9,
    "reasoning": "Matches the weekly patch window.", "recommended_actions": ["No action"],
    "cited_sources": ["org_maintenance_windows.md"],
}


def tool_use(name, input, id="tu_1"):
    return NS(type="tool_use", name=name, input=input, id=id)


def text(t="hmm"):
    return NS(type="text", text=t)


class FakeClient:
    """Returns the scripted responses in order; records every request for assertions."""

    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []
        self.messages = NS(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(content=self._responses.pop(0))
