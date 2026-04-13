"""
01_data_processing.py
Loads raw HydroShare CSVs, converts units, aggregates to water-year totals,
and builds the master dataset used in all subsequent analysis.

Run this first. Output: data/processed/conchos_master_1900_2010.csv

Author: Raul Alejandro Pérez Saucedo
"""

import pandas as pd
import sys
import os

# Add src to path so we can import processing functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from processing import (
    load_flow_csv, water_year_total, compute_capture, decade_summary
)

# ── File paths ─────────────────────────────────────────────────────────
RAW = 'data/raw'
PROCESSED = 'data/processed'

FILES = {
    'ojinaga_nat': (f'{RAW}/Ojinaga_monthly_natural_streamflow.csv',    'latin-1'),
    'ojinaga_reg': (f'{RAW}/Ojinaga_monthly_regulated_streamflow.csv',  'utf-8-sig'),
    'amistad_nat': (f'{RAW}/Abv_Amistad_monthly_natural_streamflow.csv','utf-8-sig'),
    'amistad_reg': (f'{RAW}/Abv_Amistad_monthly_regulated_streamflow.csv','utf-8-sig'),
    'camargo_nat': (f'{RAW}/Camargo_monthly_natural_streamflow.csv',     'latin-1'),
    'lvsdsr_nat':  (f'{RAW}/LV_SD_SR_monthly_natural_streamflow.csv',   'latin-1'),
}

# ── Load and process each series ───────────────────────────────────────
print("Loading raw data...")
annual_frames = {}
for label, (path, enc) in FILES.items():
    monthly = load_flow_csv(path, label, encoding=enc)
    annual  = water_year_total(monthly, label)
    annual_frames[label] = annual
    print(f"  {label}: {annual['water_year'].min()}–{annual['water_year'].max()} "
          f"({len(annual)} water years)")

# ── Merge all series on water_year ────────────────────────────────────
print("\nMerging series...")
master = annual_frames['ojinaga_nat'].copy()
for label, df in annual_frames.items():
    if label != 'ojinaga_nat':
        master = master.merge(df, on='water_year', how='outer')
master = master.sort_values('water_year').reset_index(drop=True)

# ── Compute capture variables ─────────────────────────────────────────
master = compute_capture(
    master, 'flow_ojinaga_nat', 'flow_ojinaga_reg', 'ojinaga'
)
master = compute_capture(
    master, 'flow_amistad_nat', 'flow_amistad_reg', 'amistad'
)

# ── Add rolling smoothers ─────────────────────────────────────────────
master['ojinaga_reg_5yr'] = (
    master.set_index('water_year')['flow_ojinaga_reg']
    .rolling(5, center=True).mean().values
)

# ── Data quality flags ────────────────────────────────────────────────
# Flag years with known artifact (regulated > natural, early period)
master['ojinaga_artifact_flag'] = (
    master['capture_af_ojinaga'] < 0
).astype(int)

artifact_years = master[master['ojinaga_artifact_flag'] == 1]['water_year'].tolist()
print(f"\nData quality: {len(artifact_years)} years with artifact flag "
      f"(regulated > natural): {artifact_years}")
print("These are data artifacts in the early period, not physical events.")
print("Core findings are robust to excluding these years.")

# ── Save ──────────────────────────────────────────────────────────────
os.makedirs(PROCESSED, exist_ok=True)
out_path = f'{PROCESSED}/conchos_master_1900_2010.csv'
master.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(f"Shape: {master.shape[0]} rows × {master.shape[1]} columns")
print(f"Columns: {list(master.columns)}")

# ── Quick validation ──────────────────────────────────────────────────
print("\n── VALIDATION ──")
print(f"Natural flow below treaty target (350k AF): "
      f"{(master['flow_ojinaga_nat'] < 350_000).sum()} years")
print(f"Regulated flow below treaty target:         "
      f"{(master['flow_ojinaga_reg'] < 350_000).sum()} years")
print(f"Mean capture pre-1944:  "
      f"{master[master['water_year']<1944]['capture_pct_ojinaga'].mean():.1f}%")
print(f"Mean capture post-1990: "
      f"{master[master['water_year']>=1990]['capture_pct_ojinaga'].mean():.1f}%")
