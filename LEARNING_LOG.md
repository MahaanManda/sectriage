# Learning Log

## Day 1
- Set up Python venv, installed anthropic + python-dotenv, froze requirements.txt
- Stored API key in .env (gitignored) with .env.example as a safe template
- First successful Claude API call from Python (hello.py)
- Learned: GitHub blocks pushes that expose a private email; fixed by using the noreply address in git config

## Day 2–3
- Built a 20-document security knowledge base (MITRE ATT&CK techniques + triage playbooks)
- Chunked by section (100 chunks), embedded locally with Chroma's default MiniLM model
- Semantic search returns the right document for descriptive queries; short keyword queries are weaker (to revisit with the eval harness)
- Learned: Chroma collection names need 3+ characters