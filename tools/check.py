"""One-command check: tests plus text lint. The pre-commit hook runs this; its exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

lint = subprocess.call([sys.executable, "-X", "utf8", "tools/batches.py", "check"], cwd=ROOT)
lint = subprocess.call([sys.executable, "-X", "utf8", "tools/runon.py"], cwd=ROOT) or lint
tests =subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "tests"], cwd=ROOT)
sys.exit(lint or tests)
