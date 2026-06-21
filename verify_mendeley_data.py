#!/usr/bin/env python3
"""
Script verifikasi kelengkapan dataset Mendeley setelah re-download.
Jalankan: python verify_mendeley_data.py
"""
import os
from pathlib import Path
from collections import Counter

# Path dataset
BASE_DIR = Path(r'c:\Users\Monk\Downloads\Deteksi Tuberkulosis (TB)')
MENDELEY_DIR = BASE_DIR / 'Mendeley'
TB_DIR = MENDELEY_DIR / 'TB Chest X-rays'
NORMAL_DIR = MENDELEY_DIR / 'Normal Chest X-rays'

# Expected counts (from Mendeley citation)
EXPECTED_TB = 2494
EXPECTED_NORMAL = 514

print("=" * 60)
print("VERIFIKASI DATASET MENDELEY")
print("=" * 60)

# Check Normal
normal_files = [f for f in os.listdir(NORMAL_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"\nNormal Chest X-rays:")
print(f"  Found   : {len(normal_files)}")
print(f"  Expected: {EXPECTED_NORMAL}")
if len(normal_files) == EXPECTED_NORMAL:
    print(f"  ✓ LENGKAP")
else:
    print(f"  ✗ KURANG {EXPECTED_NORMAL - len(normal_files)} file")

# Check TB
tb_files = [f for f in os.listdir(TB_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"\nTB Chest X-rays:")
print(f"  Found   : {len(tb_files)}")
print(f"  Expected: {EXPECTED_TB}")
if len(tb_files) >= EXPECTED_TB:
    print(f"  ✓ LENGKAP")
else:
    print(f"  ✗ KURANG {EXPECTED_TB - len(tb_files)} file")

# Analyze TB file naming
try:
    tb_nums = sorted([int(f.replace('TB.', '').split('.')[0]) for f in tb_files if f.startswith('TB.')])
    if tb_nums:
        print(f"\n  Naming range: TB.{tb_nums[0]} - TB.{tb_nums[-1]}")
        
        # Check gaps
        expected_range = set(range(tb_nums[0], tb_nums[-1] + 1))
        actual = set(tb_nums)
        missing = expected_range - actual
        if missing:
            print(f"  Gaps in numbering: {len(missing)} missing numbers")
            if len(missing) <= 20:
                print(f"  Missing: {sorted(missing)}")
        else:
            print(f"  ✓ Numbering is contiguous")
except Exception as e:
    print(f"  Could not analyze numbering: {e}")

# Check file sizes
print(f"\n{'='*60}")
print("FILE SIZE ANALYSIS")
print("="*60)

for label, dir_path, files in [("Normal", NORMAL_DIR, normal_files), ("TB", TB_DIR, tb_files)]:
    sizes = [os.path.getsize(dir_path / f) for f in files]
    if sizes:
        print(f"\n{label}:")
        print(f"  Count   : {len(sizes)}")
        print(f"  Min size: {min(sizes):,} bytes ({min(sizes)/1024:.1f} KB)")
        print(f"  Max size: {max(sizes):,} bytes ({max(sizes)/1024:.1f} KB)")
        print(f"  Avg size: {sum(sizes)//len(sizes):,} bytes ({sum(sizes)//len(sizes)/1024:.1f} KB)")
        
        # Check for suspiciously small files (< 1KB might be corrupt)
        tiny = [f for f, s in zip(files, sizes) if s < 1024]
        if tiny:
            print(f"  ⚠ {len(tiny)} files < 1KB (mungkin corrupt): {tiny[:5]}")
        
        # Check for zero-byte files
        empty = [f for f, s in zip(files, sizes) if s == 0]
        if empty:
            print(f"  ✗ {len(empty)} empty files!")

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print("="*60)
total = len(normal_files) + len(tb_files)
expected_total = EXPECTED_NORMAL + EXPECTED_TB
print(f"Total gambar : {total} / {expected_total}")

if total >= expected_total:
    print(f"\n✓ Dataset LENGKAP. Siap untuk menjalankan notebook.")
else:
    print(f"\n✗ Dataset BELUM LENGKAP. Kurang {expected_total - total} file.")
    print(f"  Silakan re-download dari Mendeley Data.")
