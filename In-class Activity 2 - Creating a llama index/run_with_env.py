import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
dotenv = root / '.env'
if dotenv.exists():
    for raw in dotenv.read_text().splitlines():
        if '=' in raw:
            k, v = raw.split('=', 1)
            os.environ[k.strip()] = v.strip()

loaded = {k: bool(os.environ.get(k)) for k in ['LLAMA_CLOUD_API_KEY', 'ORGANIZATION_ID', 'GEMINI_API_KEY']}
print('Loaded env keys:', loaded)

# Exec the main script so it runs in this process with these env vars
script = root / '03-demo_llama_gemini_retrieval.py'
if not script.exists():
    print('Error: script not found:', script)
    sys.exit(1)

os.execv(sys.executable, [sys.executable, str(script)])