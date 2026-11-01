from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from yottaflex.validation import validate_dataset
errors = validate_dataset(ROOT / "data")
if errors:
    print("VALIDATION FAILED")
    for e in errors: print("-", e)
    raise SystemExit(1)
print("VALIDATION PASSED: primary keys, foreign keys, ranges and outcome dates checked.")
