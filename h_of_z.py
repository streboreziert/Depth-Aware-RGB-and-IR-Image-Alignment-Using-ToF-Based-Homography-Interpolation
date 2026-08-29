#!/usr/bin/env python3
"""H(z) = A + B·z from a linear_depth_homography.txt (9 lines of a,b)."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np


def parse(path: Path) -> list[tuple[float, float]]:
    pairs = []
    for line in path.read_text().splitlines():
        nums = [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", line)]
        if len(nums) >= 2:
            pairs.append((nums[0], nums[1]))
    if len(pairs) < 9:
        raise SystemExit(f"need 9 (a,b) pairs, got {len(pairs)}")
    return pairs[:9]


def H(pairs, z: float) -> np.ndarray:
    flat = [a + b * z for a, b in pairs]
    M = np.array(flat, dtype=float).reshape(3, 3)
    if abs(M[2, 2]) > 1e-12:
        M = M / M[2, 2]
    return M


def main() -> None:
    p = argparse.ArgumentParser(description="Evaluate depth-linear homography")
    p.add_argument("file", type=Path, nargs="?", help="linear_depth_homography.txt")
    p.add_argument("--z", type=float, default=150, help="depth cm")
    p.add_argument("--demo", action="store_true")
    a = p.parse_args()
    if a.demo or not a.file:
        # identity + tiny depth shear — shows the API without calibration files
        pairs = [(1, 0), (0, 0.001), (0, 0), (0, 0), (1, 0), (0, 0), (0, 0), (0, 0), (1, 0)]
    else:
        pairs = parse(a.file)
    print(H(pairs, a.z))


if __name__ == "__main__":
    main()
