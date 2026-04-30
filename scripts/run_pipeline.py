from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    path = ROOT / "scripts" / script
    print(f"\n>>> {script}")
    subprocess.run([sys.executable, str(path)], check=True, cwd=ROOT)


def main() -> None:
    run("00_make_sample_data.py")
    run("01_extract_climate_signals.py")
    run("02_build_factor.py")
    run("03_run_asset_pricing_tests.py")
    run("04_analyze_outputs.py")


if __name__ == "__main__":
    main()
