import os
import sys

# Make the project root importable and make sure tests never use a real key or token.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["ANTHROPIC_API_KEY"] = "test-key-not-real"
os.environ.pop("TRIAGE_API_TOKEN", None)
