import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from yottaflex.generator import generate_dataset
p = argparse.ArgumentParser()
p.add_argument("--employees", type=int, default=10000)
p.add_argument("--seed", type=int, default=20261022)
p.add_argument("--output", default=str(ROOT / "data"))
args = p.parse_args()
manifest = generate_dataset(args.output, args.employees, args.seed)
print("Generation complete")
print("Employees:", args.employees)
print("Seed:", args.seed)
print("Tables:", manifest["row_counts"])
